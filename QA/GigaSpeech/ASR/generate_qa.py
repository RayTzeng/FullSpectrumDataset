#!/usr/bin/env python3
"""
Generate raw-ASR QA pairs from a template .jsonl file and a metadata .jsonl(.gz).

Same contract as the stock recognition generator, plus two row-conditional
routings, both of which switch themselves off for template files that do not
use them -- so this one file serves LibriSpeech and GigaSpeech unchanged:

  * Non-speech routing.  GigaSpeech stores a whole-utterance music/noise/
    silence segment as an empty transcript.  Such a row draws only from
    templates flagged `"nonspeech_ok": true`, which state what to return when
    a clip has no speech.  Those templates are phrased conditionally, so they
    stay truthful on ordinary speech rows and remain in the general pool --
    the only way the tag-free training split can teach the convention at all.

  * Source gating.  A template that asserts where the audio comes from
    ("This is a clip from a podcast.") declares `"requires": "podcast"` and is
    offered only to rows whose id carries the matching GigaSpeech prefix.
    Firing such a claim blindly would teach the model to ignore it.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

Supported answer expressions include common deterministic expressions such as:
    text
    text.lower()
    text.upper()
    text.title()
    'yes' if score >= 0.5 else 'no'
    f"{speaker_id}:{text}"   # not supported; use question string formatting instead

Notes
-----
- `question` is treated as a plain string. If it contains Python-style format
  placeholders like "{text}" or "{id}", they will be filled from metadata.
- `answer` is evaluated with a restricted expression evaluator rather than raw eval.
- If `weight` exists in the template file, it can be used for weighted sampling.

Examples
--------
# 1) Sample one template per metadata entry using template weights
python generate_qa_from_templates.py \
  --template template.jsonl \
  --metadata metadata.jsonl.gz \
  --output qa.jsonl \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --seed 42

# 2) Generate the full Cartesian product (every template x every metadata entry)
python generate_qa_from_templates.py \
  --template template.jsonl \
  --metadata metadata.jsonl.gz \
  --output qa.jsonl \
  --mode cartesian
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
from typing import Any, Dict, Iterable, Iterator, List, Sequence

from tqdm import tqdm


class SafeDict(dict):
    """Return the original placeholder when a key is missing."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def title_words(text: str) -> str:
    """Capitalize each whitespace-delimited word, leaving the rest lowercase.

    str.title() is wrong for this corpus: it treats an apostrophe as a word
    boundary, so LET'S becomes "Let'S".  ~24% of rows in both GigaSpeech and
    LibriSpeech contain an apostrophe, so the title-case templates would
    otherwise be teaching that artifact.
    """
    return " ".join(word.capitalize() for word in text.split())


SAFE_BUILTINS = {
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
    "title_words": title_words,
}

SAFE_STR_METHODS = {
    "lower",
    "upper",
    "title",
    "strip",
    "lstrip",
    "rstrip",
    "replace",
    "capitalize",
    "casefold",
    "split",
    "rsplit",
    "join",
    "startswith",
    "endswith",
    "removeprefix",
    "removesuffix",
    "count",
}

SAFE_LIST_METHODS = {"count", "index"}
SAFE_DICT_METHODS = {"get", "keys", "values", "items"}

ALLOWED_AST_NODES = (
    ast.Expression,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Set,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.IfExp,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Slice,
)


class SafeEvaluator:
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
            if node.id in SAFE_BUILTINS:
                return SAFE_BUILTINS[node.id]
            raise KeyError(f"Unknown name in expression: {node.id}")

        if isinstance(node, ast.List):
            return [self._eval_node(elt) for elt in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt) for elt in node.elts)

        if isinstance(node, ast.Set):
            return {self._eval_node(elt) for elt in node.elts}

        if isinstance(node, ast.Dict):
            return {
                self._eval_node(k): self._eval_node(v)
                for k, v in zip(node.keys, node.values)
            }

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
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise ValueError("Unsupported binary operator")

        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(v) for v in node.values]
            if isinstance(node.op, ast.And):
                result = True
                for v in values:
                    result = result and v
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for v in values:
                    result = result or v
                return result
            raise ValueError("Unsupported boolean operator")

        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator_node in zip(node.ops, node.comparators):
                right = self._eval_node(comparator_node)
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
            return self._eval_node(node.body) if self._eval_node(node.test) else self._eval_node(node.orelse)

        if isinstance(node, ast.Subscript):
            value = self._eval_node(node.value)
            if isinstance(node.slice, ast.Slice):
                lower = self._eval_node(node.slice.lower) if node.slice.lower is not None else None
                upper = self._eval_node(node.slice.upper) if node.slice.upper is not None else None
                step = self._eval_node(node.slice.step) if node.slice.step is not None else None
                return value[slice(lower, upper, step)]
            index = self._eval_node(node.slice)
            return value[index]

        if isinstance(node, ast.Attribute):
            value = self._eval_node(node.value)
            attr = node.attr
            if isinstance(value, str) and attr in SAFE_STR_METHODS:
                return getattr(value, attr)
            if isinstance(value, list) and attr in SAFE_LIST_METHODS:
                return getattr(value, attr)
            if isinstance(value, dict) and attr in SAFE_DICT_METHODS:
                return getattr(value, attr)
            raise ValueError(f"Attribute access not allowed: {type(value).__name__}.{attr}")

        if isinstance(node, ast.Call):
            func = self._eval_node(node.func)
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)

        raise ValueError(f"Unsupported AST node: {type(node).__name__}")


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


def render_question(question_template: str, metadata: Dict[str, Any]) -> str:
    return question_template.format_map(SafeDict(metadata))


def render_answer(answer_expr: Any, metadata: Dict[str, Any]) -> Any:
    if not isinstance(answer_expr, str):
        return answer_expr
    evaluator = SafeEvaluator(metadata)
    return evaluator.eval(answer_expr)


def positive_weight(template: Dict[str, Any]) -> float:
    try:
        w = float(template.get("weight", 1.0))
    except (TypeError, ValueError):
        w = 1.0
    return max(w, 0.0)


def weighted_sample_without_replacement(
    templates: Sequence[Dict[str, Any]],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    candidates = [(tpl, positive_weight(tpl)) for tpl in templates]
    candidates = [(tpl, w) for tpl, w in candidates if w > 0]
    if k <= 0 or not candidates:
        return []
    if k >= len(candidates):
        return [tpl for tpl, _ in candidates]

    # Efraimidis-Spirakis weighted sampling without replacement.
    scored: List[tuple[float, Dict[str, Any]]] = []
    for tpl, w in candidates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        key = math.log(u) / w  # larger (closer to 0) is better
        scored.append((key, tpl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [tpl for _, tpl in scored[:k]]


def select_templates(
    templates: Sequence[Dict[str, Any]],
    mode: str,
    num_templates_per_entry: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        k = min(num_templates_per_entry, len(templates))
        return rng.sample(list(templates), k)
    if mode == "weighted_sample":
        return weighted_sample_without_replacement(templates, num_templates_per_entry, rng)
    raise ValueError(f"Unknown mode: {mode}")



# ---------------------------------------------------------------------------
# Row-conditional template routing
# ---------------------------------------------------------------------------
#
# Two independent constraints decide which templates a row may draw from.
# Both are inferred from explicit template fields rather than from question
# wording, so a rephrasing never silently changes a template's scope.

# GigaSpeech id prefixes: YOU = YouTube, POD = podcast, AUD = audiobook.
# Corpora whose ids carry no such prefix (LibriSpeech) satisfy no predicate,
# which is harmless because their templates declare no requirement either.
SOURCE_PREFIXES = {
    "POD": "podcast",
    "YOU": "youtube",
    "AUD": "audiobook",
}
SOURCE_PREDICATES = frozenset(SOURCE_PREFIXES.values())

NONSPEECH_FLAG = "nonspeech_ok"


def row_source(metadata: Dict[str, Any]) -> Any:
    """Which source predicate this row satisfies, or None."""
    row_id = metadata.get("id")
    if not isinstance(row_id, str):
        return None
    return SOURCE_PREFIXES.get(row_id[:3].upper())


def is_nonspeech_row(metadata: Dict[str, Any], target_field: str) -> bool:
    """True when the row's whole transcript target is empty."""
    target = metadata.get(target_field)
    return isinstance(target, str) and not target.strip()


def template_requirement(template: Dict[str, Any]) -> Any:
    """Validate and return a template's `requires` predicate, if any."""
    req = template.get("requires")
    if req in (None, "", []):
        return None
    if not isinstance(req, str):
        raise ValueError(f"'requires' must be a string, got {type(req).__name__}")
    if req not in SOURCE_PREDICATES:
        raise ValueError(
            f"Unknown 'requires' predicate {req!r}. "
            f"Known predicates: {sorted(SOURCE_PREDICATES)}"
        )
    return req


def build_pool(
    templates: Sequence[Dict[str, Any]],
    source: Any,
    nonspeech: bool,
    source_gating: bool,
    nonspeech_routing: bool,
) -> List[Dict[str, Any]]:
    """Templates a row of this (source, nonspeech) class may draw from."""
    pool: List[Dict[str, Any]] = []
    for tpl in templates:
        if source_gating:
            req = tpl.get("requires")
            if req and req != source:
                continue
        if nonspeech_routing and nonspeech and not tpl.get(NONSPEECH_FLAG):
            continue
        pool.append(tpl)
    return pool


def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    mode: str,
    num_templates_per_entry: int,
    seed: int,
    target_field: str = "text",
    source_gating: str = "auto",
    nonspeech_routing: str = "auto",
) -> None:
    templates = load_jsonl(template_path)
    if not templates:
        raise ValueError("No templates found.")

    required_keys = {"question", "answer"}
    for i, tpl in enumerate(templates):
        missing = required_keys - tpl.keys()
        if missing:
            raise ValueError(f"Template #{i} is missing required keys: {sorted(missing)}")
        template_requirement(tpl)  # validate the predicate name early

    has_gated = any(template_requirement(t) for t in templates)
    has_nonspeech = any(t.get(NONSPEECH_FLAG) for t in templates)

    if source_gating == "on" and not has_gated:
        raise ValueError(
            "Source gating was requested but no template declares a 'requires' "
            "predicate. Either add such templates or pass --source-gating off."
        )
    if nonspeech_routing == "on" and not has_nonspeech:
        raise ValueError(
            f"Non-speech routing was requested but no template sets "
            f"'{NONSPEECH_FLAG}'. Either add such templates or pass "
            f"--nonspeech-routing off."
        )
    gating_on = source_gating == "on" or (source_gating == "auto" and has_gated)
    routing_on = nonspeech_routing == "on" or (nonspeech_routing == "auto" and has_nonspeech)

    # At most (#sources + 1) x 2 distinct row classes, so pools are built once
    # each rather than per row.
    pools: Dict[Any, List[Dict[str, Any]]] = {}

    def pool_for(source: Any, nonspeech: bool) -> List[Dict[str, Any]]:
        key = (source, nonspeech)
        if key not in pools:
            pools[key] = build_pool(
                templates, source, nonspeech, gating_on, routing_on
            )
        return pools[key]

    rng = random.Random(seed)
    num_written = 0
    num_metadata = 0
    num_nonspeech = 0
    num_nonspeech_unmatched = 0
    source_counts: Dict[str, int] = {}

    # Ensure output path ends with .jsonl.gz
    output_path_obj = Path(output_path)
    if not output_path.endswith(".jsonl.gz"):
        output_path = str(output_path_obj.with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1
            source = row_source(metadata) if gating_on else None
            nonspeech = routing_on and is_nonspeech_row(metadata, target_field)
            if source:
                source_counts[source] = source_counts.get(source, 0) + 1
            if nonspeech:
                num_nonspeech += 1

            candidates = pool_for(source, nonspeech)
            if not candidates:
                # No template states the convention this row needs; fall back to
                # the ungated pool rather than dropping the row silently.
                num_nonspeech_unmatched += nonspeech
                candidates = pool_for(source, False) or list(templates)

            chosen_templates = select_templates(
                templates=candidates,
                mode=mode,
                num_templates_per_entry=num_templates_per_entry,
                rng=rng,
            )
            for tpl in chosen_templates:
                question = render_question(str(tpl["question"]), metadata)
                answer = render_answer(tpl["answer"], metadata)
                record = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)}")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    if routing_on:
        pool_size = len([t for t in templates if t.get(NONSPEECH_FLAG)])
        print(f"Non-speech routing: on ({pool_size} templates state the convention)")
        print(f"  Rows with an empty transcript routed to them: {num_nonspeech}")
        if num_nonspeech_unmatched:
            print(f"  Empty rows with no matching template (used full pool): {num_nonspeech_unmatched}")
    else:
        print(f"Non-speech routing: off (no template sets '{NONSPEECH_FLAG}')")
    if gating_on:
        sizes = {
            pred: len([t for t in templates if t.get("requires") == pred])
            for pred in sorted(SOURCE_PREDICATES)
        }
        print(f"Source gating: on (gated templates per source: {sizes})")
        print(f"  Rows per source: {dict(sorted(source_counts.items()))}")
    else:
        print("Source gating: off (no template declares a 'requires' predicate)")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate QA JSONL from template JSONL and metadata JSONL(.gz).")
    parser.add_argument("--template", required=True, help="Path to template .jsonl")
    parser.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz")
    parser.add_argument("--output", required=True, help="Path to output .jsonl.gz")
    parser.add_argument(
        "--mode",
        default="weighted_sample",
        choices=["cartesian", "random_sample", "weighted_sample"],
        help=(
            "Generation mode: cartesian = every template x every metadata entry; "
            "random_sample = uniform random templates per metadata entry; "
            "weighted_sample = sample using template 'weight'."
        ),
    )
    parser.add_argument(
        "--num-templates-per-entry",
        type=int,
        default=1,
        help="How many templates to sample per metadata entry in random_sample / weighted_sample mode.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--target-field",
        default="text",
        help="Metadata field holding the transcript; scanned to detect non-speech rows.",
    )
    parser.add_argument(
        "--source-gating",
        default="auto",
        choices=["auto", "on", "off"],
        help=(
            "Offer a template declaring a 'requires' predicate (podcast, youtube, "
            "audiobook) only to rows whose id carries the matching GigaSpeech "
            "prefix. 'auto' enables it when some template declares one."
        ),
    )
    parser.add_argument(
        "--nonspeech-routing",
        default="auto",
        choices=["auto", "on", "off"],
        help=(
            "Route rows whose transcript target is empty to templates flagged "
            "'nonspeech_ok', which state what to return for a clip with no "
            "speech. 'auto' enables it when some template sets the flag."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        mode=args.mode,
        num_templates_per_entry=args.num_templates_per_entry,
        seed=args.seed,
        target_field=args.target_field,
        source_gating=args.source_gating,
        nonspeech_routing=args.nonspeech_routing,
    )
