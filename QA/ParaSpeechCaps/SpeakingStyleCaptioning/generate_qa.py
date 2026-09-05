#!/usr/bin/env python3
"""
Generate ParaSpeechCaps SpeakingStyleCaptioning QA pairs from a template .jsonl
and a metadata .jsonl(.gz).

The task target is the `caption` field -- a paralinguistic description of *how*
the speech sounds (voice, pitch, pace, articulation, mood, recording
environment).  It is not the transcript; `text` is the target of the sibling
PunctuatedASR task and is dropped from the emitted metadata, along with
`caption` itself.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

Three things beyond the stock recognition generator:

1. `' '.join(caption.split())`.  The field carries a leading space on 100% of
   dev/test rows and on none of the train rows, and ~0.2% of captions carry an
   embedded newline from a leftover annotator aside, so the answer expression
   normalises whitespace rather than only stripping the ends.

2. Caption-gated routing.  A template may declare a `requires` predicate naming
   an aspect it asks the model to cover ("...including the emotion in their
   voice") or a length it asks for ("...in a single sentence").  Such a template
   is offered only to rows whose caption supports the request; templates without
   `requires` stay eligible everywhere.  Fired blindly, an aspect request would
   land on a caption that never mentions the aspect (emotion appears in 27-41%
   of captions, marked volume in 24-40%), and a length request would contradict
   its own gold answer (71% of captions run to two or three sentences).

3. Artifact rows are skipped.  About 0.3% of captions are annotator residue
   rather than a description -- a "(Note: ...)" aside, an "Or:" list of
   alternative wordings, a bare tag dump, or a "Description:" restart.  Trained
   as targets they would teach the model to emit annotation meta-commentary, so
   they are dropped from both the output and the distractor pool.

4. Multiple choice.  A template carrying a `sampling_config` of type
   `mcq_options` is rendered with N candidate captions, one of them this row's.
   Distractors are real captions drawn from elsewhere in the same manifest,
   filtered so each conflicts with the gold on at least two style slots
   (gender / pitch / speed / environment / accent) and is not a lexical
   near-copy.  Roughly half the distractors are chosen to share the gold's
   gender, so "the odd gender out" is never the shortcut answer.

Answer expressions are ordinary Python evaluated by a restricted evaluator:
    ' '.join(caption.split())
    ' '.join(caption.split()).lower()
    option_of(options, gold_option)      # "(B) A male speaker ..."
    letter_of(options, gold_option)      # "B"
    gold_option                          # the caption itself

Questions are plain strings; any "{...}" span is evaluated as an expression
against the row (plus the sampled MCQ variables), so both "{duration}" and
"{options_block(options, 'lines')}" work.

Examples
--------
# dev / test: one template per row
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/ParaSpeechCaps/SpeakingStyleCaptionAndPunctuatedASR/dev.jsonl.gz \
  --output dev.jsonl.gz \
  --mode weighted_sample --num-templates-per-entry 1 --seed 42

# train shards: two templates per row
python generate_qa.py \
  --template template.jsonl \
  --metadata .../train_shard0.jsonl.gz \
  --output train_shard0.jsonl.gz \
  --mode weighted_sample --num-templates-per-entry 2 --seed 42
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import math
import random
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence, Tuple

from tqdm import tqdm


# --------------------------------------------------------------------------
# Restricted expression evaluation
# --------------------------------------------------------------------------

SAFE_BUILTINS: Dict[str, Any] = {
    "len": len,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "round": round,
    "min": min,
    "max": max,
    "abs": abs,
    "sum": sum,
    "sorted": sorted,
    "list": list,
    "enumerate": enumerate,
}

SAFE_STR_METHODS = {
    "lower", "upper", "title", "strip", "lstrip", "rstrip", "replace",
    "capitalize", "casefold", "split", "rsplit", "join", "startswith",
    "endswith", "removeprefix", "removesuffix", "count",
}

SAFE_LIST_METHODS = {"count", "index"}
SAFE_DICT_METHODS = {"get", "keys", "values", "items"}

ALLOWED_AST_NODES = (
    ast.Expression, ast.Name, ast.Load, ast.Constant, ast.List, ast.Tuple,
    ast.Dict, ast.Set, ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.BinOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.NotEq, ast.Lt,
    ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.IfExp, ast.Subscript,
    ast.Slice, ast.Index if hasattr(ast, "Index") else ast.Slice,
    ast.Attribute, ast.Call, ast.keyword,
)


class SafeEvaluator:
    """Evaluate a whitelisted subset of Python against a row context."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def eval(self, expr: str) -> Any:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_AST_NODES):
                raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            if node.id in HELPERS:
                return HELPERS[node.id]
            if node.id in SAFE_BUILTINS:
                return SAFE_BUILTINS[node.id]
            raise KeyError(f"Unknown name in expression: {node.id}")

        if isinstance(node, ast.List):
            return [self._eval_node(e) for e in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(e) for e in node.elts)
        if isinstance(node, ast.Set):
            return {self._eval_node(e) for e in node.elts}
        if isinstance(node, ast.Dict):
            return {self._eval_node(k): self._eval_node(v)
                    for k, v in zip(node.keys, node.values)}

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.Not):
                return not operand
            raise ValueError("Unsupported unary operator")

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            ops = {ast.Add: lambda: left + right, ast.Sub: lambda: left - right,
                   ast.Mult: lambda: left * right, ast.Div: lambda: left / right,
                   ast.FloorDiv: lambda: left // right, ast.Mod: lambda: left % right,
                   ast.Pow: lambda: left ** right}
            for op_type, fn in ops.items():
                if isinstance(node.op, op_type):
                    return fn()
            raise ValueError("Unsupported binary operator")

        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(v) for v in node.values]
            if isinstance(node.op, ast.And):
                result: Any = True
                for v in values:
                    result = result and v
                return result
            result = False
            for v in values:
                result = result or v
            return result

        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator)
                if isinstance(op, ast.Eq):
                    ok = left == right
                elif isinstance(op, ast.NotEq):
                    ok = left != right
                elif isinstance(op, ast.Lt):
                    ok = left < right
                elif isinstance(op, ast.LtE):
                    ok = left <= right
                elif isinstance(op, ast.Gt):
                    ok = left > right
                elif isinstance(op, ast.GtE):
                    ok = left >= right
                elif isinstance(op, ast.In):
                    ok = left in right
                elif isinstance(op, ast.NotIn):
                    ok = left not in right
                else:
                    raise ValueError("Unsupported comparison operator")
                if not ok:
                    return False
                left = right
            return True

        if isinstance(node, ast.IfExp):
            return self._eval_node(node.body) if self._eval_node(node.test) \
                else self._eval_node(node.orelse)

        if isinstance(node, ast.Subscript):
            value = self._eval_node(node.value)
            if isinstance(node.slice, ast.Slice):
                lo = self._eval_node(node.slice.lower) if node.slice.lower else None
                hi = self._eval_node(node.slice.upper) if node.slice.upper else None
                st = self._eval_node(node.slice.step) if node.slice.step else None
                return value[slice(lo, hi, st)]
            return value[self._eval_node(node.slice)]

        if isinstance(node, ast.Attribute):
            value = self._eval_node(node.value)
            attr = node.attr
            if isinstance(value, str) and attr in SAFE_STR_METHODS:
                return getattr(value, attr)
            if isinstance(value, list) and attr in SAFE_LIST_METHODS:
                return getattr(value, attr)
            if isinstance(value, dict) and attr in SAFE_DICT_METHODS:
                return getattr(value, attr)
            raise ValueError(
                f"Attribute access not allowed: {type(value).__name__}.{attr}"
            )

        if isinstance(node, ast.Call):
            func = self._eval_node(node.func)
            args = [self._eval_node(a) for a in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)

        raise ValueError(f"Unsupported AST node: {type(node).__name__}")


# --------------------------------------------------------------------------
# IO
# --------------------------------------------------------------------------

def open_text_auto(path: str):
    path_obj = Path(path)
    if path_obj.suffix == ".gz":
        return gzip.open(path_obj, "rt", encoding="utf-8")
    return open(path_obj, "r", encoding="utf-8")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    with open_text_auto(path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {e}") from e
    return items


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    with open_text_auto(path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {e}") from e


# --------------------------------------------------------------------------
# Caption-gated template routing
# --------------------------------------------------------------------------
#
# Two families of template declare a `requires` predicate.
#
# Aspect coverage -- "...and include their accent", "...including the emotion in
# their voice".  Only ~90% of captions name an accent, ~30% an emotion, ~57% a
# voice texture and ~30% a marked volume, so these are routed to rows whose
# caption actually covers the aspect.
#
# Length -- "...in a single sentence" versus "...in a couple of sentences".
# Captions run to one sentence on ~30% of rows and two or three on the rest, so
# an ungated length request would be contradicted by its own gold answer.
#
# Two traps in the ParaSpeechCaps caption vocabulary shape the patterns:
#   * "quiet" almost always describes the *environment* ("a clean and quiet
#     environment") rather than the voice, so the volume predicate keys on
#     loudness and on whispering/soft-spokenness instead of on that word.
#   * Some captions negate a condition ("no discernible background noise").
#     Negated spans are blanked before matching.
#
# The accent predicate deliberately accepts a bare nationality adjective: "a
# British male speaker" describes an accent without ever using the word.

NEGATION_RE = re.compile(
    r"\b(?:no|not|never|without|free\s+of|devoid\s+of|lacking|lacks|"
    r"isn't|aren't|is\s+not|are\s+not)\b(?:[\s-]+\w+){0,3}",
    re.IGNORECASE,
)

NATIONALITY = (
    r"American|British|English|Canadian|Australian|Jamaican|Irish|Scottish|Welsh|"
    r"Indian|German|French|Italian|Spanish|New\s+Zealand|South\s+African|Nigerian|"
    r"Filipino|Russian|Dutch|Swedish|Polish|Chinese|Japanese|Korean|Mexican|"
    r"Brazilian|Portuguese|Danish|Norwegian|Finnish|Greek|Turkish|Israeli|"
    r"Malaysian|Singaporean|Pakistani|Bangladeshi|Sri\s+Lankan|Kenyan|Ghanaian|"
    r"Egyptian|Lebanese|Iranian|Vietnamese|Thai|Indonesian|Ukrainian|Czech|"
    r"Hungarian|Romanian|Bulgarian|Croatian|Serbian|Slovak|Austrian|Swiss|"
    r"Belgian|Cuban|Colombian|Argentinian|Argentine|Chilean|Peruvian|Venezuelan"
)

CAPTION_PREDICATES: Dict[str, re.Pattern] = {
    "accent": re.compile(rf"\baccent\w*|\b(?:{NATIONALITY})\b", re.IGNORECASE),
    "emotional": re.compile(
        r"\b(?:happ\w+|sad\w*|angr\w+|calm\w*|anxious\w*|scared|fearful|"
        r"enthusiastic\w*|disgust\w+|excit\w+|frustrat\w+|confus\w+|sympath\w+|"
        r"bewilder\w+|awe|surpris\w+|amaz\w+|animated|sarcas\w+|sleepy|drowsy|"
        r"nervous|joy\w+|cheer\w+|somber|melanchol\w+|authoritative|hesitan\w+|"
        r"contempl\w+|admir\w+|pained|guilt\w*|bored|jealous|desire|annoy\w+|"
        r"worried|apologetic|urgent|emotional)\b",
        re.IGNORECASE,
    ),
    "voice_quality": re.compile(
        r"\b(?:husky|breathy|nasal|guttural|raspy|silky|shrill|booming|hoarse|"
        r"gravelly|velvet\w*|throaty|smooth|warm|thin|textured|texture|timbre|"
        r"crisp|resonant)\b",
        re.IGNORECASE,
    ),
    "volume_marked": re.compile(
        r"\bloud\w*|booming|shout\w*|yell\w*|whisper\w*|soft-spoken|"
        r"softly\s+spoken|speaks\s+softly|hushed|murmur\w*",
        re.IGNORECASE,
    ),
}

SENTENCE_END_RE = re.compile(r"[.!?]+(?:\s|$)")

# A small share of ParaSpeechCaps captions are not captions but annotator
# residue: an aside about the annotation ("(Note: the term 'singsong' was not
# explicitly included...)"), a second and third alternative wording after an
# "Or:" line, a bare tag dump, or a "Description:" restart that repeats the
# caption.  Every observed instance spans more than one line, so a newline is
# the reliable marker; the two colon forms catch the single-line cases.
# Together they cover ~0.3% of rows, which are skipped rather than trained on.
ARTIFACT_CAPTION_RE = re.compile(
    r"\n|\(\s*Note\s*:|\b(?:Description|Caption)\s*:", re.IGNORECASE
)


def is_artifact_caption(caption: str) -> bool:
    return bool(ARTIFACT_CAPTION_RE.search(caption))

# Predicates computed from caption structure rather than vocabulary.
STRUCTURAL_PREDICATES = ("one_sentence", "multi_sentence")

KNOWN_PREDICATES = tuple(CAPTION_PREDICATES) + STRUCTURAL_PREDICATES


def row_predicates(metadata: Dict[str, Any], caption_field: str) -> set:
    """Which `requires` predicates this row satisfies."""
    caption = metadata.get(caption_field)
    if not isinstance(caption, str) or not caption.strip():
        return set()
    caption = caption.strip()
    residual = NEGATION_RE.sub(" ", caption)
    satisfied = {n for n, p in CAPTION_PREDICATES.items() if p.search(residual)}
    n_sentences = len(SENTENCE_END_RE.findall(caption))
    satisfied.add("one_sentence" if n_sentences <= 1 else "multi_sentence")
    return satisfied


def template_requirement(template: Dict[str, Any]) -> Any:
    req = template.get("requires")
    if req in (None, "", []):
        return None
    if not isinstance(req, str):
        raise ValueError(f"'requires' must be a string, got {type(req).__name__}")
    if req not in KNOWN_PREDICATES:
        raise ValueError(
            f"Unknown 'requires' predicate {req!r}. "
            f"Known predicates: {sorted(KNOWN_PREDICATES)}"
        )
    return req


# --------------------------------------------------------------------------
# Style signatures, for multiple-choice distractor selection
# --------------------------------------------------------------------------
#
# A signature is the handful of style slots a caption commits to.  Two captions
# conflict on a slot when both name it and they disagree; a distractor has to
# conflict on at least `min_conflicts` slots before it can be offered as a wrong
# answer, which is what keeps an MCQ item from having two defensible options.
#
# Coverage on dev: gender 99.7%, speed 99.5%, accent 93%, env 91.5%, pitch 91%.

SLOT_PATTERNS: Dict[str, List[Tuple[str, re.Pattern]]] = {
    "gender": [
        ("female", re.compile(r"\b(?:female|woman|women|she|her|hers|lady)\b", re.I)),
        ("male", re.compile(r"\b(?:male|man|men|he|his|him|gentleman)\b", re.I)),
    ],
    # Explicit "X-pitched" phrases are tried before descriptive words, because a
    # caption may carry both ("a medium-pitched voice ... yet shrill") and the
    # explicit phrase is the one that states the pitch.
    "pitch": [
        ("high", re.compile(r"high[- ]pitched", re.I)),
        ("low", re.compile(r"low[- ]pitched", re.I)),
        ("medium", re.compile(r"medium[- ]pitched|mid[- ]pitched|moderate pitch", re.I)),
        ("high", re.compile(r"shrill|treble", re.I)),
        ("low", re.compile(r"deep[- ]?(?:toned|voice|pitched)?\b|bassy", re.I)),
    ],
    "speed": [
        ("fast", re.compile(
            r"\bfast\b|\brapid|\brushed\b|hurried|quick(?:ly|\s+pace|\s+delivery|\s+speed)|"
            r"speaks\s+quickly|brisk", re.I)),
        ("slow", re.compile(r"\bslow\w*|leisurely|unhurried|drawn[- ]out|deliberate pace", re.I)),
        ("measured", re.compile(
            r"measured|moderate\s+(?:speed|pace)|steady\s+(?:pace|speed)|even pace|"
            r"normal\s+(?:speed|pace)", re.I)),
    ],
    "env": [
        ("noisy", re.compile(r"\bnois\w+", re.I)),
        ("reverberant", re.compile(r"reverberan\w+|echo\w*", re.I)),
        ("clean", re.compile(r"\bclean\b|clear environment|balanced in clarity|very clear", re.I)),
    ],
}

ACCENT_VALUE_RE = re.compile(rf"\b({NATIONALITY})\b", re.IGNORECASE)

# Slots compared when counting conflicts.
CONFLICT_SLOTS = ("gender", "pitch", "speed", "env", "accent")


def style_signature(caption: str) -> Dict[str, str]:
    """The style slots this caption commits to."""
    residual = NEGATION_RE.sub(" ", caption)
    sig: Dict[str, str] = {}
    for slot, options in SLOT_PATTERNS.items():
        for value, pattern in options:
            if pattern.search(residual):
                sig[slot] = value
                break
    accent = ACCENT_VALUE_RE.search(residual)
    if accent:
        sig["accent"] = re.sub(r"\s+", " ", accent.group(1)).title()
    return sig


def count_conflicts(a: Dict[str, str], b: Dict[str, str]) -> int:
    return sum(1 for slot in CONFLICT_SLOTS
               if slot in a and slot in b and a[slot] != b[slot])


def token_overlap(a: str, b: str) -> float:
    """Jaccard overlap of word sets -- a guard against near-copy distractors."""
    ta = set(re.findall(r"[a-z']+", a.lower()))
    tb = set(re.findall(r"[a-z']+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


class CaptionPool:
    """A reservoir sample of (caption, signature) drawn from the whole manifest.

    Reservoir rather than the first N rows: the train shards are ordered
    PSC-Base then PSC-Scaled and the caption vocabulary drifts across that
    boundary, so a head sample would draw distractors from one half only.
    Acceptance is decided from the line index alone, so only the ~20k accepted
    lines are ever JSON-parsed.
    """

    def __init__(self, captions: List[str], signatures: List[Dict[str, str]]):
        self.captions = captions
        self.signatures = signatures
        self.by_gender: Dict[str, List[int]] = {}
        for i, sig in enumerate(signatures):
            self.by_gender.setdefault(sig.get("gender", "?"), []).append(i)

    def __len__(self) -> int:
        return len(self.captions)

    @classmethod
    def build(cls, metadata_path: str, caption_field: str, size: int,
              rng: random.Random) -> "CaptionPool":
        reservoir: List[str] = []
        seen = 0
        with open_text_auto(metadata_path) as f:
            for line in tqdm(f, desc="Building MCQ distractor pool"):
                if not line.strip():
                    continue
                seen += 1
                if len(reservoir) < size:
                    reservoir.append(line)
                else:
                    j = rng.randrange(seen)
                    if j < size:
                        reservoir[j] = line
        captions: List[str] = []
        signatures: List[Dict[str, str]] = []
        for line in reservoir:
            caption = json.loads(line).get(caption_field)
            if isinstance(caption, str) and caption.strip() \
                    and not is_artifact_caption(caption):
                # Collapsed, not merely stripped: ~0.2% of captions carry an
                # embedded newline from an annotator aside, and a multi-line
                # option would break the "(A) ... / (B) ..." block.
                caption = " ".join(caption.split())
                captions.append(caption)
                signatures.append(style_signature(caption))
        if len(captions) < 8:
            raise ValueError(
                f"Only {len(captions)} usable captions in {metadata_path}; cannot "
                "build multiple-choice options. Drop the MCQ templates or point "
                "--metadata at the full manifest."
            )
        return cls(captions, signatures)

    def draw(self, gold: str, gold_sig: Dict[str, str], n: int,
             rng: random.Random, min_conflicts: int, max_overlap: float,
             max_probes: int = 400) -> Tuple[List[str], bool]:
        """n distractors for `gold`, gender-balanced. Returns (options, relaxed)."""
        gold_gender = gold_sig.get("gender")
        # Aim for about half the distractors to share the gold's gender, with the
        # odd one randomised, so neither "same gender" nor "different gender"
        # identifies the answer.
        n_same = n // 2
        if n % 2 and rng.random() < 0.5:
            n_same += 1
        if gold_gender is None:
            n_same = 0

        def qualified(index_pool: Sequence[int], want: int, floor: int) -> List[str]:
            found: List[str] = []
            texts: set = set()
            probes = 0
            budget = max_probes if index_pool else 0
            while found.__len__() < want and probes < budget:
                probes += 1
                i = index_pool[rng.randrange(len(index_pool))]
                cand = self.captions[i]
                if cand == gold or cand in texts:
                    continue
                if count_conflicts(gold_sig, self.signatures[i]) < floor:
                    continue
                if token_overlap(gold, cand) > max_overlap:
                    continue
                found.append(cand)
                texts.add(cand)
            return found

        same_pool = self.by_gender.get(gold_gender, []) if gold_gender else []
        other_pool = [i for g, idx in self.by_gender.items() if g != gold_gender
                      for i in idx] if gold_gender else list(range(len(self.captions)))

        chosen: List[str] = []
        chosen += qualified(same_pool, n_same, min_conflicts)
        chosen += [c for c in qualified(other_pool, n - len(chosen), min_conflicts)
                   if c not in chosen]

        relaxed = False
        # Fallback ladder: fewer required conflicts, then any distinct caption.
        for floor in (min_conflicts - 1, 0):
            if len(chosen) >= n:
                break
            relaxed = True
            extra = qualified(list(range(len(self.captions))), n - len(chosen), max(floor, 0))
            chosen += [c for c in extra if c not in chosen]
        while len(chosen) < n:  # degenerate manifests only
            relaxed = True
            cand = self.captions[rng.randrange(len(self.captions))]
            if cand != gold and cand not in chosen:
                chosen.append(cand)
        return chosen[:n], relaxed


# --------------------------------------------------------------------------
# Multiple-choice rendering
# --------------------------------------------------------------------------

_LETTERS = "ABCDEFGH"


def options_block(options: Sequence[str], style: str = "lines", sep: str = "  ") -> str:
    """Render the candidate captions for the question text.

    style="lines"   -> one per line, "(A) ..."  (the readable default for
                       captions, which run ~30 words)
    style="letter"  -> "(A) ...  (B) ..." on one line
    style="number"  -> "1. ...  2. ..."
    style="inline"  -> quoted and joined with ", or "
    """
    opts = [str(o) for o in options]
    if style == "inline":
        quoted = [f'"{o}"' for o in opts]
        if len(quoted) == 1:
            return quoted[0]
        return ", or ".join([", ".join(quoted[:-1]), quoted[-1]]) if len(quoted) > 2 \
            else f"{quoted[0]}, or {quoted[1]}"
    if style == "number":
        return sep.join(f"{i + 1}. {o}" for i, o in enumerate(opts))
    if style == "letter":
        return sep.join(f"({_LETTERS[i]}) {o}" for i, o in enumerate(opts))
    return "\n".join(f"({_LETTERS[i]}) {o}" for i, o in enumerate(opts))


def letter_of(options: Sequence[str], value: str, style: str = "letter") -> str:
    """The marker of `value` within `options`: 'B', or '2' for style='number'."""
    for i, opt in enumerate(options):
        if str(opt) == str(value):
            return str(i + 1) if style == "number" else _LETTERS[i]
    raise ValueError(
        "The gold caption is not among the options. An mcq_options draw always "
        "includes it, so the answer expression referenced the wrong variable."
    )


def option_of(options: Sequence[str], value: str, style: str = "letter") -> str:
    """'(B) A male speaker ...' -- the marker-plus-caption answer form."""
    mark = letter_of(options, value, style)
    return f"{mark}. {value}" if style == "number" else f"({mark}) {value}"


HELPERS: Dict[str, Any] = {
    "options_block": options_block,
    "letter_of": letter_of,
    "option_of": option_of,
}


# --------------------------------------------------------------------------
# Question rendering: literal text with "{expression}" spans
# --------------------------------------------------------------------------

Segment = Any  # str literal, or ("expr", source)


def parse_question(question: str) -> List[Segment]:
    """Split into literal and expression segments in one left-to-right scan.

    Single scan so that "{{"/"}}" escapes cannot interfere with "{expr}" spans.
    """
    segments: List[Segment] = []
    literal: List[str] = []
    i = 0
    n = len(question)
    while i < n:
        ch = question[i]
        if ch == "{":
            if i + 1 < n and question[i + 1] == "{":
                literal.append("{")
                i += 2
                continue
            depth = 1
            j = i + 1
            while j < n and depth:
                if question[j] == "{":
                    depth += 1
                elif question[j] == "}":
                    depth -= 1
                j += 1
            if depth:
                raise ValueError(f"Unbalanced '{{' in question: {question!r}")
            segments.append("".join(literal))
            literal = []
            segments.append(("expr", question[i + 1:j - 1]))
            i = j
            continue
        if ch == "}":
            if i + 1 < n and question[i + 1] == "}":
                literal.append("}")
                i += 2
                continue
            raise ValueError(f"Unmatched '}}' in question: {question!r}")
        literal.append(ch)
        i += 1
    segments.append("".join(literal))
    return [s for s in segments if s != ""]


def render_question(segments: Sequence[Segment], context: Dict[str, Any]) -> str:
    if len(segments) == 1 and isinstance(segments[0], str):
        return segments[0]
    evaluator = SafeEvaluator(context)
    out: List[str] = []
    for seg in segments:
        if isinstance(seg, str):
            out.append(seg)
        else:
            out.append(str(evaluator.eval(seg[1])))
    return "".join(out)


def render_answer(answer_expr: Any, context: Dict[str, Any]) -> Any:
    if not isinstance(answer_expr, str):
        return answer_expr
    return SafeEvaluator(context).eval(answer_expr)


def expression_names(segments: Sequence[Segment], answer: str) -> set:
    names: set = set()
    sources = [s[1] for s in segments if not isinstance(s, str)]
    if isinstance(answer, str):
        sources.append(answer)
    for src in sources:
        try:
            tree = ast.parse(src, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Cannot parse expression {src!r}: {e}") from e
        names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    return names


# --------------------------------------------------------------------------
# Template loading
# --------------------------------------------------------------------------

MCQ_STYLES = {"lines", "letter", "number", "inline"}


def mcq_spec(template: Dict[str, Any]) -> Dict[str, Any] | None:
    config = template.get("sampling_config")
    if not config:
        return None
    if not isinstance(config, dict) or "opts" not in config:
        raise ValueError(
            f"sampling_config must be a dict with an 'opts' entry, got {config!r}"
        )
    spec = config["opts"]
    if spec.get("type") != "mcq_options":
        raise ValueError(f"Unsupported sampling type {spec.get('type')!r}")
    n = int(spec.get("n_options", 4))
    if not 2 <= n <= len(_LETTERS):
        raise ValueError(f"n_options must be between 2 and {len(_LETTERS)}, got {n}")
    style = spec.get("style", "lines")
    if style not in MCQ_STYLES:
        raise ValueError(f"Unknown MCQ style {style!r}; known: {sorted(MCQ_STYLES)}")
    return {"n_options": n, "style": style}


def prepare_templates(templates: Sequence[Dict[str, Any]]) -> None:
    """Validate and attach parsed forms, once, in place."""
    for i, tpl in enumerate(templates):
        missing = {"question", "answer", "weight"} - tpl.keys()
        if missing:
            raise ValueError(f"Template #{i} is missing required keys: {sorted(missing)}")
        weight = float(tpl["weight"])
        if not 0.0 < weight <= 1.0:
            raise ValueError(
                f"Template #{i} ({tpl.get('template_id')}) has weight {weight}; "
                "expected (0, 1]."
            )
        template_requirement(tpl)
        spec = mcq_spec(tpl)
        tpl["_segments"] = parse_question(str(tpl["question"]))
        tpl["_mcq"] = spec
        names = expression_names(tpl["_segments"], tpl["answer"])
        needs_mcq = bool(names & {"options", "gold_option"})
        if needs_mcq and spec is None:
            raise ValueError(
                f"Template #{i} ({tpl.get('template_id')}) references options / "
                "gold_option but declares no sampling_config of type mcq_options."
            )
        if spec is not None and not needs_mcq:
            raise ValueError(
                f"Template #{i} ({tpl.get('template_id')}) declares mcq_options but "
                "neither its question nor its answer uses them."
            )


def positive_weight(template: Dict[str, Any]) -> float:
    try:
        return max(float(template.get("weight", 1.0)), 0.0)
    except (TypeError, ValueError):
        return 1.0


# --------------------------------------------------------------------------
# Sampling
# --------------------------------------------------------------------------

def eligible_templates(
    templates: Sequence[Dict[str, Any]],
    ungated: Sequence[Dict[str, Any]],
    gated_by_predicate: Dict[str, List[Dict[str, Any]]],
    satisfied: set,
) -> Sequence[Dict[str, Any]]:
    """Ungated templates plus the gated ones this row qualifies for."""
    if not gated_by_predicate:
        return templates
    extra: List[Dict[str, Any]] = []
    for pred in satisfied:
        extra.extend(gated_by_predicate.get(pred, ()))
    if not extra:
        return ungated
    return list(ungated) + extra


def weighted_sample_without_replacement(
    templates: Sequence[Dict[str, Any]], k: int, rng: random.Random
) -> List[Dict[str, Any]]:
    candidates = [(t, positive_weight(t)) for t in templates]
    candidates = [(t, w) for t, w in candidates if w > 0]
    if k <= 0 or not candidates:
        return []
    if k >= len(candidates):
        return [t for t, _ in candidates]
    # Efraimidis-Spirakis weighted sampling without replacement.
    scored = []
    for tpl, w in candidates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        scored.append((math.log(u) / w, id(tpl), tpl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, _, t in scored[:k]]


def select_templates(templates, mode, num_templates_per_entry, rng):
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        return rng.sample(list(templates), min(num_templates_per_entry, len(templates)))
    if mode == "weighted_sample":
        return weighted_sample_without_replacement(templates, num_templates_per_entry, rng)
    raise ValueError(f"Unknown mode: {mode}")


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    mode: str,
    num_templates_per_entry: int,
    seed: int,
    caption_field: str = "caption",
    caption_gating: str = "auto",
    drop_fields: Sequence[str] = ("caption", "text"),
    skip_artifact_captions: bool = True,
    mcq_pool_size: int = 20000,
    mcq_min_conflicts: int = 2,
    mcq_max_overlap: float = 0.6,
) -> None:
    templates = load_jsonl(template_path)
    if not templates:
        raise ValueError("No templates found.")
    prepare_templates(templates)

    ungated: List[Dict[str, Any]] = []
    gated_by_predicate: Dict[str, List[Dict[str, Any]]] = {}
    for tpl in templates:
        req = template_requirement(tpl)
        if req is None:
            ungated.append(tpl)
        else:
            gated_by_predicate.setdefault(req, []).append(tpl)

    if caption_gating == "on" and not gated_by_predicate:
        raise ValueError(
            "Caption gating was requested but no template declares a 'requires' "
            "predicate. Either add such templates or pass --caption-gating off."
        )
    gating_on = caption_gating == "on" or (
        caption_gating == "auto" and bool(gated_by_predicate)
    )
    if not gating_on:
        ungated = list(templates)

    rng = random.Random(seed)

    needs_mcq = any(t["_mcq"] for t in templates)
    pool = None
    if needs_mcq:
        pool = CaptionPool.build(metadata_path, caption_field,
                                 mcq_pool_size, random.Random(seed ^ 0x5EED))
        print(f"MCQ distractor pool: {len(pool)} captions")

    if not output_path.endswith(".jsonl.gz"):
        output_path = str(Path(output_path).with_suffix("")) + ".jsonl.gz"

    drop = set(drop_fields)
    num_written = num_metadata = num_missing_caption = num_artifact = 0
    gated_served = mcq_served = mcq_relaxed = 0
    predicate_hits: Dict[str, int] = {n: 0 for n in KNOWN_PREDICATES}

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for row in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1
            caption = row.get(caption_field)
            if not isinstance(caption, str) or not caption.strip():
                num_missing_caption += 1
                continue
            if skip_artifact_captions and is_artifact_caption(caption):
                num_artifact += 1
                continue

            pool_templates: Sequence[Dict[str, Any]] = templates
            if gating_on:
                satisfied = row_predicates(row, caption_field)
                for name in satisfied:
                    predicate_hits[name] += 1
                pool_templates = eligible_templates(
                    templates, ungated, gated_by_predicate, satisfied
                )

            chosen = select_templates(pool_templates, mode, num_templates_per_entry, rng)
            emitted = {k: v for k, v in row.items() if k not in drop}
            # Matches the templates' "' '.join(caption.split())" answer form, so
            # the rendered options and the answer are the same string.
            gold = " ".join(caption.split())
            gold_sig = None

            for tpl in chosen:
                context: Dict[str, Any] = dict(row)
                spec = tpl["_mcq"]
                if spec is not None:
                    if gold_sig is None:
                        gold_sig = style_signature(gold)
                    distractors, relaxed = pool.draw(
                        gold, gold_sig, spec["n_options"] - 1, rng,
                        mcq_min_conflicts, mcq_max_overlap,
                    )
                    options = [gold] + distractors
                    rng.shuffle(options)  # uniform gold position
                    context["options"] = options
                    context["gold_option"] = gold
                    mcq_served += 1
                    mcq_relaxed += int(relaxed)

                question = render_question(tpl["_segments"], context)
                answer = render_answer(tpl["answer"], context)
                if template_requirement(tpl) is not None:
                    gated_served += 1
                out_f.write(json.dumps(
                    {"question": question, "answer": answer, "metadata": emitted},
                    ensure_ascii=False,
                ) + "\n")
                num_written += 1

    n_gated = len(templates) - len(ungated) if gating_on else 0
    print(f"Loaded templates: {len(templates)} ({len(templates) - n_gated} ungated, "
          f"{n_gated} caption-gated, {sum(1 for t in templates if t['_mcq'])} multiple-choice)")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    if num_missing_caption:
        print(f"Skipped rows with no usable '{caption_field}': {num_missing_caption}")
    if skip_artifact_captions:
        print(f"Skipped rows whose caption is annotator residue: {num_artifact}"
              + (f" ({num_artifact / num_metadata:.2%})" if num_metadata else ""))
    if gating_on:
        sizes = {p: len(v) for p, v in sorted(gated_by_predicate.items())}
        print(f"Caption gating: on; gated pool sizes {sizes}")
        usable = num_metadata - num_missing_caption - num_artifact
        if usable:
            print("Rows satisfying each gated predicate: " + str({
                p: f"{predicate_hits[p] / usable:.1%}" for p in sorted(gated_by_predicate)
            }))
        print(f"QA pairs served by a gated template: {gated_served}")
    else:
        print("Caption gating: off (no template declares a 'requires' predicate)")
    if needs_mcq:
        print(f"Multiple-choice items: {mcq_served}"
              + (f" ({mcq_relaxed} needed a relaxed distractor filter)" if mcq_relaxed else ""))
    print(f"Dropped from emitted metadata: {sorted(drop)}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate ParaSpeechCaps SpeakingStyleCaptioning QA JSONL "
                    "from template JSONL and metadata JSONL(.gz)."
    )
    p.add_argument("--template", required=True, help="Path to template .jsonl")
    p.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz")
    p.add_argument("--output", required=True, help="Path to output .jsonl.gz")
    p.add_argument("--mode", default="weighted_sample",
                   choices=["cartesian", "random_sample", "weighted_sample"],
                   help="cartesian = every template x every row; random_sample = "
                        "uniform templates per row; weighted_sample = sample by 'weight'.")
    p.add_argument("--num-templates-per-entry", type=int, default=1,
                   help="Templates sampled per metadata entry in the sampling modes.")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--caption-field", default="caption",
                   help="Metadata field holding the style caption (the task target).")
    p.add_argument("--caption-gating", default="auto", choices=["auto", "on", "off"],
                   help="Offer a template declaring 'requires' (accent, emotional, "
                        "voice_quality, volume_marked, one_sentence, multi_sentence) "
                        "only to rows whose caption supports it. 'auto' enables "
                        "gating only when such templates exist.")
    p.add_argument("--drop-fields", default="caption,text",
                   help="Comma-separated metadata fields omitted from the emitted "
                        "'metadata' object.")
    p.add_argument("--skip-artifact-captions", default="on", choices=["on", "off"],
                   help="Skip rows whose caption is annotator residue rather than a "
                        "style description -- a '(Note: ...)' aside, an 'Or:' list of "
                        "alternative wordings, a tag dump, or a 'Description:' restart. "
                        "About 0.3% of rows.")
    p.add_argument("--mcq-pool-size", type=int, default=20000,
                   help="Captions held in the multiple-choice distractor reservoir.")
    p.add_argument("--mcq-min-conflicts", type=int, default=2,
                   help="Style slots (gender/pitch/speed/env/accent) a distractor "
                        "must disagree with the gold caption on.")
    p.add_argument("--mcq-max-overlap", type=float, default=0.6,
                   help="Reject a distractor whose word-set Jaccard overlap with the "
                        "gold caption exceeds this.")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        mode=args.mode,
        num_templates_per_entry=args.num_templates_per_entry,
        seed=args.seed,
        caption_field=args.caption_field,
        caption_gating=args.caption_gating,
        drop_fields=tuple(f.strip() for f in args.drop_fields.split(",") if f.strip()),
        skip_artifact_captions=args.skip_artifact_captions == "on",
        mcq_pool_size=args.mcq_pool_size,
        mcq_min_conflicts=args.mcq_min_conflicts,
        mcq_max_overlap=args.mcq_max_overlap,
    )
