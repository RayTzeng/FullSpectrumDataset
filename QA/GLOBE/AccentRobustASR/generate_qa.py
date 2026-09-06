"""
Generate GLOBE AccentRobustASR QA pairs from a template .jsonl and a metadata
.jsonl(.gz).

Same contract as the stock recognition generator, plus three GLOBE specifics:

1. Accent canonicalisation.  GLOBE copies Mozilla Common Voice's self-reported
   `accent` field verbatim, so it is free text: 500 distinct strings in train,
   comma-joined mixes of the 16 checkbox varieties the profile form offers and
   whatever the contributor typed ("non native speaker,german english",
   "united states english,midwestern,low,demure").  The comma is not a clean
   separator -- three checkbox labels contain one inside parentheses -- so the
   split here is parenthesis-aware, exactly as the sibling
   EnglishAccentClassification task does it.  A row resolves when exactly one
   canonical variety survives: 98.5% of train, 98.0% of dev, 97.4% of test.

2. Accent parameterization.  A template may write "{accent_display}",
   "{an_accent}", "{accent_region}", "{accent_homeland}", "{age_display}" or
   "{gender_display}" in its question; this script fills them from the row.
   Variety names are sampled among aliases by weight, so the same accent does
   not always surface under the same name.  "{an_accent}" carries the article
   with it ("an American English", "a Canadian English") because English
   article agreement does not survive a bare placeholder.

3. Row gating.  Every template that names the row's accent, region, age or
   gender declares a `requires` predicate (one name or a list of them) and is
   offered only to rows that satisfy it.  Rows whose accent does not resolve,
   or whose gender is "non-binary" / "do_not_wish_to_say", stay in the manifest
   and simply draw from the accent-free and generic families instead.

The target field is `text`: sentence-cased English in standard written form.
Seven train rows carry stray surrounding whitespace, so templates evaluate
`text.strip()` rather than a bare `text`.

The cascade families answer with a joint accent + transcript string built by
`format_accent_cascade`, `format_accent_lines` or `format_accent_prose`.  Those
always use the canonical display name, never a sampled alias, so the gold label
in a cascade answer is stable across rows.  Each cascade question states its
serialization explicitly, since the wrapper text is not part of the stored
target.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

Supported answer expressions include common deterministic expressions such as:
    text.strip()
    text.strip().lower()
    text.strip().upper()
    ' '.join(text.split())
    format_accent_cascade(accent, text)

Notes
-----
- `question` is treated as a plain string; placeholders are filled from the row
  context (metadata plus the derived accent/age/gender fields).
- `answer` is evaluated with a restricted expression evaluator rather than raw eval.
- If `weight` exists in the template file, it can be used for weighted sampling.

Examples
--------
# 1) One template per metadata entry, sampled by weight (dev / test)
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/GLOBE/test.jsonl.gz \
  --output test.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --seed 42

# 2) Two templates per metadata entry (train)
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/GLOBE/train.jsonl.gz \
  --output train.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 2 \
  --seed 42
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import math
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence

from tqdm import tqdm


class SafeDict(dict):
    """Return the original placeholder when a key is missing."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


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


def positive_weight(template: Dict[str, Any]) -> float:
    try:
        w = float(template.get("weight", 1.0))
    except (TypeError, ValueError):
        w = 1.0
    return max(w, 0.0)


# --------------------------------------------------------------------------
# Accent canonicalisation
# --------------------------------------------------------------------------
#
# The 16 accent options Common Voice's English profile form offers, spelled
# exactly as GLOBE stores them, plus `german english`, promoted from free text
# because it is the only non-checkbox variety with enough rows in every split
# to be worth naming.  This mirrors
# QA/GLOBE/EnglishAccentClassification/prepare_manifest.py; keep the two in
# step if either is edited.

CV_CHECKBOX = [
    "united states english",
    "england english",
    "india and south asia (india, pakistan, sri lanka)",
    "canadian english",
    "australian english",
    "southern african (south africa, zimbabwe, namibia)",
    "northern irish",
    "irish english",
    "new zealand english",
    "scottish english",
    "filipino",
    "hong kong english",
    "singaporean english",
    "malaysian english",
    "welsh english",
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)",
]

GERMAN_ENGLISH = "german english"
GERMAN_VARIANTS = {
    "german english", "german", "german accent", "germany english",
    "german native speaker", "german native", "austrian",
    "south german accent", "south-west german", "alemannic german accent",
    "south german / swiss accent", "english with swiss german accent",
}

CANON: Dict[str, str] = {t: t for t in CV_CHECKBOX}
CANON.update({v: GERMAN_ENGLISH for v in GERMAN_VARIANTS})

# Canonical display name per variety, matching the sibling classification task.
ACCENT_DISPLAY: Dict[str, str] = {
    "united states english": "American English",
    "england english": "English English",
    "india and south asia (india, pakistan, sri lanka)": "South Asian English",
    "canadian english": "Canadian English",
    "australian english": "Australian English",
    "southern african (south africa, zimbabwe, namibia)": "southern African English",
    "northern irish": "Northern Irish English",
    "irish english": "Irish English",
    "new zealand english": "New Zealand English",
    "scottish english": "Scottish English",
    "filipino": "Philippine English",
    "hong kong english": "Hong Kong English",
    "singaporean english": "Singaporean English",
    "malaysian english": "Malaysian English",
    "welsh english": "Welsh English",
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)": "Caribbean English",
    GERMAN_ENGLISH: "German-accented English",
}

# Alternative names a person might use for the same variety, sampled by weight
# so prompts do not always say it the same way.  Every alias must denote the
# same set of speakers as the label: "British English" is absent because
# Scottish and Welsh English are separate labels here, and "Indian English" is
# absent because the label also covers Pakistan and Sri Lanka.
ACCENT_ALIASES: Dict[str, List[tuple]] = {
    "united states english": [("American English", 1.0), ("US English", 0.45),
                              ("United States English", 0.35)],
    "england english": [("English English", 0.7), ("England English", 0.6)],
    "india and south asia (india, pakistan, sri lanka)":
        [("South Asian English", 1.0), ("Indian or South Asian English", 0.4)],
    "canadian english": [("Canadian English", 1.0)],
    "australian english": [("Australian English", 1.0)],
    "southern african (south africa, zimbabwe, namibia)": [("southern African English", 1.0)],
    "northern irish": [("Northern Irish English", 1.0)],
    "irish english": [("Irish English", 1.0)],
    "new zealand english": [("New Zealand English", 1.0), ("Kiwi English", 0.2)],
    "scottish english": [("Scottish English", 1.0)],
    "filipino": [("Philippine English", 1.0), ("Filipino English", 0.7)],
    "hong kong english": [("Hong Kong English", 1.0)],
    "singaporean english": [("Singaporean English", 1.0), ("Singapore English", 0.45)],
    "malaysian english": [("Malaysian English", 1.0)],
    "welsh english": [("Welsh English", 1.0)],
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)":
        [("Caribbean English", 1.0), ("West Indian English", 0.45)],
    GERMAN_ENGLISH: [("German-accented English", 1.0)],
}

ACCENT_REGION: Dict[str, str] = {
    "united states english": "North America",
    "canadian english": "North America",
    "england english": "the British Isles",
    "scottish english": "the British Isles",
    "welsh english": "the British Isles",
    "irish english": "the British Isles",
    "northern irish": "the British Isles",
    "australian english": "Oceania",
    "new zealand english": "Oceania",
    "india and south asia (india, pakistan, sri lanka)": "South Asia",
    "filipino": "Southeast Asia",
    "singaporean english": "Southeast Asia",
    "malaysian english": "Southeast Asia",
    "hong kong english": "East Asia",
    "southern african (south africa, zimbabwe, namibia)": "Africa",
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)": "the Caribbean",
    GERMAN_ENGLISH: "continental Europe",
}

# Where the variety is spoken.  Four labels cover several countries and the
# metadata does not say which, so the phrasing stays disjunctive rather than
# inventing a specific one.
ACCENT_HOMELAND: Dict[str, str] = {
    "united states english": "the United States",
    "canadian english": "Canada",
    "england english": "England",
    "scottish english": "Scotland",
    "welsh english": "Wales",
    "irish english": "the Republic of Ireland",
    "northern irish": "Northern Ireland",
    "australian english": "Australia",
    "new zealand english": "New Zealand",
    "india and south asia (india, pakistan, sri lanka)": "India, Pakistan or Sri Lanka",
    "filipino": "the Philippines",
    "singaporean english": "Singapore",
    "malaysian english": "Malaysia",
    "hong kong english": "Hong Kong",
    "southern african (south africa, zimbabwe, namibia)": "South Africa, Zimbabwe or Namibia",
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)":
        "the Bahamas, Bermuda, Jamaica or Trinidad",
    GERMAN_ENGLISH: "Germany, Austria or German-speaking Switzerland",
}

# `age` is stored with Common Voice's spelling, including "fourties"; prompts
# render the ordinary English spelling because the label is prose here, not a
# target.  The answer is the transcript, so nothing downstream depends on it.
AGE_DISPLAY: Dict[str, str] = {
    "teens": "their teens",
    "twenties": "their twenties",
    "thirties": "their thirties",
    "fourties": "their forties",
    "fifties": "their fifties",
    "sixties": "their sixties",
    "seventies": "their seventies",
    "eighties": "their eighties",
    "nineties": "their nineties",
}

# Only the two categories with enough rows to be worth naming in a prompt.
# train carries 24 non-binary, 11 do_not_wish_to_say and 10 transgender rows;
# those rows simply never draw a gender-naming template.
GENDER_DISPLAY: Dict[str, str] = {"male": "male", "female": "female"}

# Every canonical variety must appear in all four maps, or a row would raise
# at fill time instead of at import.
for _label in set(CANON.values()):
    for _map, _name in ((ACCENT_DISPLAY, "ACCENT_DISPLAY"), (ACCENT_ALIASES, "ACCENT_ALIASES"),
                        (ACCENT_REGION, "ACCENT_REGION"), (ACCENT_HOMELAND, "ACCENT_HOMELAND")):
        assert _label in _map, f"{_label!r} missing from {_name}"

PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

# Placeholders that name the row's accent, one way or another.
ACCENT_SLOTS = {"accent_display", "Accent_display", "an_accent",
                "accent_region", "accent_homeland"}


def split_tags(value: str) -> List[str]:
    """Comma-split that never splits inside parentheses.

    "india and south asia (india, pakistan, sri lanka)" is one tag, while
    "non native speaker,german english" is two.
    """
    out, depth, cur = [], 0, ""
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return [t for t in out if t]


def canonical_accent(value: Any) -> str:
    """The row's single canonical variety, or "" if it has zero or several.

    Free-text tags sitting alongside a canonical one ("low", "demure") are
    contributor commentary about a sub-variety, not a competing claim, so they
    are discarded.  A row that ticked two checkboxes is genuinely ambiguous and
    resolves to nothing.
    """
    if not isinstance(value, str) or not value:
        return ""
    hits = {CANON[t] for t in split_tags(value.lower()) if t in CANON}
    return hits.pop() if len(hits) == 1 else ""


# Article choice follows pronunciation, not spelling: "a US English accent"
# (you-ess) and "a United States English accent" (you-nited), against "an
# American English accent".  These are the only names in this label space whose
# vowel letter opens with a consonant sound.
GLIDE_INITIAL = ("us", "united", "uk", "euro", "uni")


def article_for(phrase: str) -> str:
    """"a" or "an" for a display name, by how the name is said aloud."""
    lowered = phrase.lower()
    if lowered.startswith(GLIDE_INITIAL):
        return "a"
    return "an" if lowered[:1] in "aeiou" else "a"


# "{an_accent}" is always followed by the word "accent", and
# "a German-accented English accent" doubles the head; name the accent itself.
ACCENT_AS_MODIFIER: Dict[str, str] = {GERMAN_ENGLISH: "German"}


def _display(accent: Any) -> str:
    return ACCENT_DISPLAY.get(canonical_accent(accent), "")


def format_accent_cascade(accent: Any, text: Any) -> str:
    """One line: 'Accent: American English. Transcript: ...'"""
    return f"Accent: {_display(accent)}. Transcript: {str(text).strip()}"


def format_accent_lines(accent: Any, text: Any) -> str:
    """Two lines: 'Accent: ...' then 'Transcript: ...'"""
    return f"Accent: {_display(accent)}\nTranscript: {str(text).strip()}"


def format_accent_prose(accent: Any, text: Any) -> str:
    """'The accent is American English. The speaker says: ...'"""
    return f"The accent is {_display(accent)}. The speaker says: {str(text).strip()}"


ANSWER_HELPERS = {
    "format_accent_cascade": format_accent_cascade,
    "format_accent_lines": format_accent_lines,
    "format_accent_prose": format_accent_prose,
}


def render_answer(answer_expr: Any, metadata: Dict[str, Any]) -> Any:
    if not isinstance(answer_expr, str):
        return answer_expr
    context = dict(metadata)
    context.update(ANSWER_HELPERS)
    return SafeEvaluator(context).eval(answer_expr)


def row_context(metadata: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """Metadata plus the fields templates may reference through placeholders.

    A placeholder that cannot be filled is simply absent from the context, and
    `eligible_templates` withholds any template that needs it.
    """
    context = dict(metadata)

    accent = canonical_accent(metadata.get("accent"))
    if accent:
        aliases = ACCENT_ALIASES[accent]
        names = [name for name, _ in aliases]
        weights = [w for _, w in aliases]
        display = rng.choices(names, weights=weights, k=1)[0]
        context["accent_display"] = display
        context["Accent_display"] = display[:1].upper() + display[1:]
        modifier = ACCENT_AS_MODIFIER.get(accent, display)
        context["an_accent"] = f"{article_for(modifier)} {modifier}"
        context["accent_canonical"] = ACCENT_DISPLAY[accent]
        context["accent_region"] = ACCENT_REGION[accent]
        context["accent_homeland"] = ACCENT_HOMELAND[accent]

    age = AGE_DISPLAY.get(str(metadata.get("age", "")).lower())
    if age:
        context["age_display"] = age

    gender = GENDER_DISPLAY.get(str(metadata.get("gender", "")).lower())
    if gender:
        context["gender_display"] = gender

    return context


def question_placeholders(question: str) -> set:
    return set(PLACEHOLDER_RE.findall(question))


# --------------------------------------------------------------------------
# Row-gated template routing
# --------------------------------------------------------------------------
#
# A template that names the speaker's accent, origin, age or gender is true of
# some rows and false or unresolvable for others.  Firing it blindly would
# teach the model that the stated condition is noise to be ignored, so such a
# template declares a `requires` predicate -- one name, or a list of names all
# of which must hold -- and is offered only to rows that satisfy it.  Templates
# without `requires` stay eligible everywhere.

ROW_PREDICATES = {
    "canonical_accent": lambda m: bool(canonical_accent(m.get("accent"))),
    "known_age": lambda m: str(m.get("age", "")).lower() in AGE_DISPLAY,
    "known_gender": lambda m: str(m.get("gender", "")).lower() in GENDER_DISPLAY,
}


def row_predicates(metadata: Dict[str, Any]) -> set:
    """Which predicates this row satisfies."""
    return {name for name, fn in ROW_PREDICATES.items() if fn(metadata)}


def template_requirement(template: Dict[str, Any]) -> List[str]:
    """The predicates a template needs, as a list (possibly empty)."""
    req = template.get("requires")
    if req in (None, "", []):
        return []
    names = [req] if isinstance(req, str) else req
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise ValueError(f"'requires' must be a string or list of strings, got {req!r}")
    for name in names:
        if name not in ROW_PREDICATES:
            raise ValueError(
                f"Unknown 'requires' predicate {name!r}. "
                f"Known predicates: {sorted(ROW_PREDICATES)}"
            )
    return names


def eligible_templates(
    templates: Sequence[Dict[str, Any]],
    context: Dict[str, Any],
    satisfied: set,
    gating_on: bool,
) -> List[Dict[str, Any]]:
    """Templates this row qualifies for: predicates satisfied, placeholders resolvable."""
    pool: List[Dict[str, Any]] = []
    for tpl in templates:
        if gating_on and not set(template_requirement(tpl)) <= satisfied:
            continue
        needed = question_placeholders(str(tpl["question"]))
        if needed and not needed <= context.keys():
            continue
        pool.append(tpl)
    return pool


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
    scored: List[tuple] = []
    for tpl, w in candidates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        scored.append((math.log(u) / w, id(tpl), tpl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [tpl for _, _, tpl in scored[:k]]


def select_templates(
    templates: Sequence[Dict[str, Any]],
    mode: str,
    num_templates_per_entry: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        return rng.sample(list(templates), min(num_templates_per_entry, len(templates)))
    if mode == "weighted_sample":
        return weighted_sample_without_replacement(templates, num_templates_per_entry, rng)
    raise ValueError(f"Unknown mode: {mode}")


def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    mode: str,
    num_templates_per_entry: int,
    seed: int,
    gating: str = "auto",
    limit: int = 0,
) -> None:
    templates = load_jsonl(template_path)
    if not templates:
        raise ValueError("No templates found.")

    for i, tpl in enumerate(templates):
        missing = {"question", "answer"} - tpl.keys()
        if missing:
            raise ValueError(f"Template #{i} is missing required keys: {sorted(missing)}")
        template_requirement(tpl)  # validate predicate names early

    gated = [tpl for tpl in templates if template_requirement(tpl)]
    if gating == "on" and not gated:
        raise ValueError(
            "Row gating was requested but no template declares a 'requires' "
            "predicate. Either add such templates or pass --gating off."
        )
    gating_on = gating == "on" or (gating == "auto" and bool(gated))

    parameterized = [t for t in templates if question_placeholders(str(t["question"]))]

    rng = random.Random(seed)
    num_written = 0
    num_metadata = 0
    predicate_hits: Counter = Counter()
    family_served: Counter = Counter()
    accent_served: Counter = Counter()
    rows_without_accent = 0

    if not output_path.endswith(".jsonl.gz"):
        output_path = str(Path(output_path).with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1
            if limit and num_metadata > limit:
                num_metadata -= 1
                break

            context = row_context(metadata, rng)
            if "accent_display" not in context:
                rows_without_accent += 1

            satisfied = row_predicates(metadata) if gating_on else set(ROW_PREDICATES)
            predicate_hits.update(satisfied)

            pool = eligible_templates(templates, context, satisfied, gating_on)
            if not pool:
                raise ValueError(
                    f"No eligible template for row {metadata.get('id')!r}; "
                    "every template was withheld by gating or placeholder resolution."
                )

            for tpl in select_templates(pool, mode, num_templates_per_entry, rng):
                question = render_question(str(tpl["question"]), context)
                answer = render_answer(tpl["answer"], context)
                family_served[tpl.get("family", "?")] += 1
                # Only accent-bearing placeholders belong in this tally; the
                # age/gender-only templates can fire on a row whose accent
                # never resolved.
                if ACCENT_SLOTS & question_placeholders(str(tpl["question"])):
                    accent_served[context["accent_canonical"]] += 1
                out_f.write(json.dumps(
                    {"question": question, "answer": answer, "metadata": metadata},
                    ensure_ascii=False,
                ) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)} "
          f"({len(gated)} row-gated, {len(parameterized)} placeholder-parameterized)")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    if gating_on and num_metadata:
        rates = {n: f"{predicate_hits[n] / num_metadata:.1%}" for n in sorted(ROW_PREDICATES)}
        print(f"Row gating: on; rows satisfying each predicate: {rates}")
        print(f"Rows whose accent does not resolve (conditioned templates withheld): "
              f"{rows_without_accent} ({rows_without_accent / num_metadata:.1%})")
    else:
        print("Row gating: off")
    if family_served and num_written:
        print("QA pairs by template family:")
        for name, n in family_served.most_common():
            print(f"  {name:18s} {n:9,}  {n / num_written:5.1%}")
    if accent_served:
        print("Accent-conditioned pairs by variety:")
        for name, n in accent_served.most_common():
            print(f"  {name:26s} {n:9,}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Generate GLOBE AccentRobustASR QA JSONL from template JSONL "
                     "and metadata JSONL(.gz).")
    )
    parser.add_argument("--template", required=True, help="Path to template .jsonl")
    parser.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz")
    parser.add_argument("--output", required=True, help="Path to output .jsonl.gz")
    parser.add_argument(
        "--mode",
        default="weighted_sample",
        choices=["cartesian", "random_sample", "weighted_sample"],
        help=("Generation mode: cartesian = every eligible template x every metadata entry; "
              "random_sample = uniform random templates per metadata entry; "
              "weighted_sample = sample using template 'weight'."),
    )
    parser.add_argument(
        "--num-templates-per-entry",
        type=int,
        default=1,
        help="How many templates to sample per metadata entry in random_sample / weighted_sample mode.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--gating",
        default="auto",
        choices=["auto", "on", "off"],
        help=("Offer a template declaring a 'requires' predicate (canonical_accent, "
              "known_age, known_gender) only to rows that satisfy it. 'auto' enables "
              "gating only when such templates exist."),
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Stop after N metadata rows (0 = all). For spot-checking output.",
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
        gating=args.gating,
        limit=args.limit,
    )
