"""
Generate PunctuatedASR QA pairs from a template .jsonl and a metadata .jsonl(.gz).

Same contract as the stock recognition generator, plus caption-gated routing: a
template may declare a `requires` predicate naming a recording condition it
asserts ("This recording is noisy. Write out what is said anyway."), and is then
offered only to rows whose `caption` supports that claim. Gating switches itself
off for template files that never declare `requires`.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

The ParaSpeechCaps `text` field carries a leading space on ~95% of rows, so the
templates evaluate `text.strip()` rather than a bare `text`.

Supported answer expressions include common deterministic expressions such as:
    text.strip()
    text.strip().lower()
    text.strip().upper()
    text.strip().title()
    ' '.join(text.split())

Notes
-----
- `question` is treated as a plain string. If it contains Python-style format
  placeholders like "{text}" or "{id}", they will be filled from metadata.
- `answer` is evaluated with a restricted expression evaluator rather than raw eval.
- If `weight` exists in the template file, it can be used for weighted sampling.

Examples
--------
# 1) One template per metadata entry, sampled by weight (dev / test)
python generate_qa.py \
  --template template.jsonl \
  --metadata /path/to/test.jsonl.gz \
  --output test.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --seed 42

# 2) Two templates per metadata entry (train shards)
python generate_qa.py \
  --template template.jsonl \
  --metadata /path/to/train_shard0.jsonl.gz \
  --output train_shard0.jsonl.gz \
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
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Sequence

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


# --------------------------------------------------------------------------
# Caption-gated template routing
# --------------------------------------------------------------------------
#
# A handful of ParaSpeechCaps prompts describe the recording before asking for
# the transcript -- "This recording is noisy. Write out what is said anyway."
# Those claims are true of some rows and false of others, so firing them blindly
# would teach the model that the description is noise to be ignored.
#
# The `caption` field carries exactly this information and is present in every
# split, so a template may declare a `requires` predicate naming the condition
# it asserts.  Such a template is offered only to rows whose caption supports
# the claim; templates without `requires` stay eligible everywhere.  Rows that
# satisfy nothing simply draw from the ungated pool.
#
# Two traps in the caption vocabulary shape the patterns below:
#   * "quiet" nearly always describes the *environment* ("a clean and quiet
#     environment"), not the voice, so the quiet-voice predicate keys on
#     whispering and soft-spokenness instead.
#   * A small number of captions negate a condition ("no discernible background
#     noise").  Negated spans are blanked before matching, so those rows do not
#     count as noisy.

NEGATION_RE = re.compile(
    r"\b(?:no|not|never|without|free\s+of|devoid\s+of|lacking|lacks|"
    r"isn't|aren't|is\s+not|are\s+not)\b(?:[\s-]+\w+){0,3}",
    re.IGNORECASE,
)

CAPTION_PREDICATES: Dict[str, re.Pattern] = {
    "noisy": re.compile(r"\bnois", re.IGNORECASE),
    "loud": re.compile(r"\bloud\w*|booming|shout\w*|yell\w*", re.IGNORECASE),
    # Voice volume, deliberately *not* the word "quiet" -- see note above.
    "quiet": re.compile(
        r"whisper\w*|soft-spoken|softly\s+spoken|speaks\s+softly|hushed|murmur\w*",
        re.IGNORECASE,
    ),
    "fast": re.compile(
        r"\bfast\w*|\brapid\w*|\brushed\b|hurried|speaks\s+quickly|quick\s+(?:pace|delivery)",
        re.IGNORECASE,
    ),
    "slow": re.compile(r"\bslow\w*|leisurely|unhurried|drawn-out", re.IGNORECASE),
    "emotional": re.compile(
        r"angr(?:y|ily)|\bsad(?:ly)?\b|happ(?:y|ily)|disgust\w*|enthusiastic\w*|"
        r"excite\w*|anxious\w*|scared|fearful|sarcast\w*|sympath\w*|bored|"
        r"\bawe\b|desire|\bpain\w*|guilt\w*|frustrat\w*|confused|nervous|"
        r"worried|cheerful|annoyed|emotional",
        re.IGNORECASE,
    ),
    "accent": re.compile(r"\baccent\w*", re.IGNORECASE),
}


def row_predicates(metadata: Dict[str, Any], caption_field: str) -> set:
    """Which caption predicates this row satisfies."""
    caption = metadata.get(caption_field)
    if not isinstance(caption, str) or not caption:
        return set()
    residual = NEGATION_RE.sub(" ", caption)
    return {name for name, pat in CAPTION_PREDICATES.items() if pat.search(residual)}


def template_requirement(template: Dict[str, Any]) -> Any:
    req = template.get("requires")
    if req in (None, "", []):
        return None
    if not isinstance(req, str):
        raise ValueError(f"'requires' must be a string, got {type(req).__name__}")
    if req not in CAPTION_PREDICATES:
        raise ValueError(
            f"Unknown 'requires' predicate {req!r}. "
            f"Known predicates: {sorted(CAPTION_PREDICATES)}"
        )
    return req


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
        key = math.log(u) / w  # larger (closer to 0) is better
        scored.append((key, id(tpl), tpl))
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
        k = min(num_templates_per_entry, len(templates))
        return rng.sample(list(templates), k)
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
    caption_field: str = "caption",
    caption_gating: str = "auto",
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
    num_written = 0
    num_metadata = 0
    num_missing_caption = 0
    predicate_hits: Dict[str, int] = {name: 0 for name in CAPTION_PREDICATES}
    gated_served = 0

    output_path_obj = Path(output_path)
    if not output_path.endswith(".jsonl.gz"):
        output_path = str(output_path_obj.with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1

            pool: Sequence[Dict[str, Any]] = templates
            if gating_on:
                if not isinstance(metadata.get(caption_field), str):
                    num_missing_caption += 1
                satisfied = row_predicates(metadata, caption_field)
                for name in satisfied:
                    predicate_hits[name] += 1
                pool = eligible_templates(
                    templates, ungated, gated_by_predicate, satisfied
                )

            chosen_templates = select_templates(
                templates=pool,
                mode=mode,
                num_templates_per_entry=num_templates_per_entry,
                rng=rng,
            )
            for tpl in chosen_templates:
                question = render_question(str(tpl["question"]), metadata)
                answer = render_answer(tpl["answer"], metadata)
                if template_requirement(tpl) is not None:
                    gated_served += 1
                record = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)} "
          f"({len(ungated)} ungated, {len(templates) - len(ungated)} caption-gated)")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    if gating_on:
        sizes = {p: len(v) for p, v in sorted(gated_by_predicate.items())}
        print(f"Caption gating: on; gated pool sizes {sizes}")
        rates = {
            p: f"{predicate_hits[p] / num_metadata:.1%}"
            for p in sorted(gated_by_predicate)
            if num_metadata
        }
        print(f"Rows satisfying each gated predicate: {rates}")
        print(f"QA pairs served by a gated template: {gated_served}")
        if num_missing_caption:
            print(
                f"Rows with no '{caption_field}' field (ungated pool only): "
                f"{num_missing_caption}"
            )
    else:
        print("Caption gating: off (no template declares a 'requires' predicate)")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate ParaSpeechCaps PunctuatedASR QA JSONL from template JSONL "
            "and metadata JSONL(.gz)."
        )
    )
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
        "--caption-field",
        default="caption",
        help="Metadata field holding the style caption, read to evaluate 'requires' predicates.",
    )
    parser.add_argument(
        "--caption-gating",
        default="auto",
        choices=["auto", "on", "off"],
        help=(
            "Offer a template declaring a 'requires' predicate (noisy, loud, "
            "quiet, fast, slow, emotional, accent) only to rows whose caption "
            "supports the claim. 'auto' enables gating only when such templates "
            "exist."
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
        caption_field=args.caption_field,
        caption_gating=args.caption_gating,
    )
