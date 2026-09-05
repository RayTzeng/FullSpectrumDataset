"""
Generate L2-Arctic PunctuatedASR QA pairs from a template .jsonl and a metadata
.jsonl(.gz).

Same contract as the stock recognition generator, plus two L2-Arctic specifics:

1. L1 parameterization.  Every speaker in L2-Arctic is a non-native English
   speaker from one of six first-language backgrounds, and the background is
   recoverable from the speaker code that prefixes `id` ("BWC_arctic_a0577" ->
   Mandarin).  A template may write "{l1}" in its question; this script fills it
   from that map, sampling among the language's aliases by weight so the same
   background does not always surface under the same name.  Templates whose
   placeholders cannot be resolved for a row are withheld from that row.

2. Row-gated punctuation claims.  A few templates assert something about the
   reference text -- that it ends in a period, that it contains commas.  Those
   hold for most rows but not all (48 of 26,867 rows are not period-final), so
   such a template declares a `requires` predicate and is offered only to rows
   that satisfy it.  Gating switches itself off for template files that never
   declare `requires`.

The target field is `text`.  24 rows carry trailing whitespace, so the templates
evaluate `text.strip()` rather than a bare `text`.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

Supported answer expressions include common deterministic expressions such as:
    text.strip()
    text.strip().lower()
    text.strip().upper()
    text.strip().title()
    ' '.join(text.split())

Notes
-----
- `question` is treated as a plain string. Python-style format placeholders such
  as "{l1}" or "{id}" are filled from the row context (metadata + derived `l1`,
  `speaker`, `l1_canonical`).
- `answer` is evaluated with a restricted expression evaluator rather than raw eval.
- If `weight` exists in the template file, it can be used for weighted sampling.
- L2-Arctic ships train and test only; there is no dev split.

Examples
--------
# 1) One template per metadata entry, sampled by weight (test)
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/L2-Arctic/test.jsonl.gz \
  --output test.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --seed 42

# 2) Two templates per metadata entry (train)
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/L2-Arctic/train.jsonl.gz \
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
# Speaker first-language map and alias sampling
# --------------------------------------------------------------------------
#
# L2-Arctic has 24 speakers, four per L1 background, and the speaker code is the
# first underscore-separated field of `id`.  The map below is the README's
# roster; all 24 codes present in train and test are covered by it.
#
# Aliases let the same background surface under more than one name.  Only
# Mandarin has real alternatives in ordinary usage; the other five languages are
# named one way, so their alias lists have a single entry.

SPEAKER_L1: Dict[str, str] = {
    # Arabic
    "ABA": "Arabic", "SKA": "Arabic", "YBAA": "Arabic", "ZHAA": "Arabic",
    # Mandarin
    "BWC": "Mandarin", "LXC": "Mandarin", "NCC": "Mandarin", "TXHC": "Mandarin",
    # Hindi
    "ASI": "Hindi", "RRBI": "Hindi", "SVBI": "Hindi", "TNI": "Hindi",
    # Korean
    "HJK": "Korean", "HKK": "Korean", "YDCK": "Korean", "YKWK": "Korean",
    # Spanish
    "EBVS": "Spanish", "ERMS": "Spanish", "MBMPS": "Spanish", "NJS": "Spanish",
    # Vietnamese
    "HQTV": "Vietnamese", "PNV": "Vietnamese", "THV": "Vietnamese", "TLV": "Vietnamese",
}

L1_ALIASES: Dict[str, List[tuple]] = {
    "Arabic": [("Arabic", 1.0)],
    "Mandarin": [("Mandarin", 1.0), ("Mandarin Chinese", 0.6), ("Chinese", 0.5)],
    "Hindi": [("Hindi", 1.0)],
    "Korean": [("Korean", 1.0)],
    "Spanish": [("Spanish", 1.0)],
    "Vietnamese": [("Vietnamese", 1.0)],
}

PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def speaker_code(metadata: Dict[str, Any]) -> str:
    """Speaker code prefixing the utterance id, e.g. 'BWC_arctic_a0577' -> 'BWC'."""
    utt_id = metadata.get("id")
    if not isinstance(utt_id, str) or "_" not in utt_id:
        return ""
    return utt_id.split("_", 1)[0]


def row_context(metadata: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """Metadata plus the fields templates may reference through placeholders."""
    context = dict(metadata)
    code = speaker_code(metadata)
    canonical = SPEAKER_L1.get(code)
    if code:
        context["speaker"] = code
    if canonical:
        aliases = L1_ALIASES[canonical]
        names = [name for name, _ in aliases]
        weights = [w for _, w in aliases]
        context["l1"] = rng.choices(names, weights=weights, k=1)[0]
        context["l1_canonical"] = canonical
    return context


def question_placeholders(question: str) -> set:
    return set(PLACEHOLDER_RE.findall(question))


# --------------------------------------------------------------------------
# Row-gated template routing
# --------------------------------------------------------------------------
#
# A template that asserts a property of the reference text -- "give me the
# sentence with a closing period", "write out what is said, including the
# commas" -- is true of some rows and false of others.  Firing it blindly would
# teach the model that the stated condition is noise to be ignored, so such a
# template declares a `requires` predicate and is offered only to rows whose
# `text` satisfies it.  Templates without `requires` stay eligible everywhere.

TEXT_PREDICATES = {
    "period_final": lambda t: t.endswith("."),
    "has_comma": lambda t: "," in t,
    "comma_and_period": lambda t: "," in t and t.endswith("."),
}


def row_predicates(metadata: Dict[str, Any], text_field: str) -> set:
    """Which text predicates this row satisfies."""
    text = metadata.get(text_field)
    if not isinstance(text, str) or not text:
        return set()
    stripped = text.strip()
    return {name for name, fn in TEXT_PREDICATES.items() if fn(stripped)}


def template_requirement(template: Dict[str, Any]) -> Any:
    req = template.get("requires")
    if req in (None, "", []):
        return None
    if not isinstance(req, str):
        raise ValueError(f"'requires' must be a string, got {type(req).__name__}")
    if req not in TEXT_PREDICATES:
        raise ValueError(
            f"Unknown 'requires' predicate {req!r}. "
            f"Known predicates: {sorted(TEXT_PREDICATES)}"
        )
    return req


def eligible_templates(
    templates: Sequence[Dict[str, Any]],
    context: Dict[str, Any],
    satisfied: set,
    gating_on: bool,
) -> List[Dict[str, Any]]:
    """Templates this row qualifies for: predicate satisfied and placeholders resolvable."""
    pool: List[Dict[str, Any]] = []
    for tpl in templates:
        if gating_on:
            req = template_requirement(tpl)
            if req is not None and req not in satisfied:
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
    text_field: str = "text",
    gating: str = "auto",
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

    gated = [tpl for tpl in templates if template_requirement(tpl) is not None]
    if gating == "on" and not gated:
        raise ValueError(
            "Row gating was requested but no template declares a 'requires' "
            "predicate. Either add such templates or pass --gating off."
        )
    gating_on = gating == "on" or (gating == "auto" and bool(gated))

    parameterized = [
        tpl for tpl in templates if question_placeholders(str(tpl["question"]))
    ]

    rng = random.Random(seed)
    num_written = 0
    num_metadata = 0
    num_unknown_speaker = 0
    predicate_hits: Dict[str, int] = {name: 0 for name in TEXT_PREDICATES}
    gated_served = 0
    l1_served: Dict[str, int] = {}

    output_path_obj = Path(output_path)
    if not output_path.endswith(".jsonl.gz"):
        output_path = str(output_path_obj.with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1

            context = row_context(metadata, rng)
            if "l1" not in context:
                num_unknown_speaker += 1

            satisfied = row_predicates(metadata, text_field) if gating_on else set()
            for name in satisfied:
                predicate_hits[name] += 1

            pool = eligible_templates(templates, context, satisfied, gating_on)
            if not pool:
                raise ValueError(
                    f"No eligible template for row {metadata.get('id')!r}; "
                    "every template was withheld by gating or placeholder resolution."
                )

            chosen_templates = select_templates(
                templates=pool,
                mode=mode,
                num_templates_per_entry=num_templates_per_entry,
                rng=rng,
            )
            for tpl in chosen_templates:
                question = render_question(str(tpl["question"]), context)
                answer = render_answer(tpl["answer"], context)
                if template_requirement(tpl) is not None:
                    gated_served += 1
                if question_placeholders(str(tpl["question"])):
                    name = context.get("l1", "?")
                    l1_served[name] = l1_served.get(name, 0) + 1
                record = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)} "
          f"({len(gated)} row-gated, {len(parameterized)} placeholder-parameterized)")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    if gating_on:
        rates = {
            name: f"{predicate_hits[name] / num_metadata:.1%}"
            for name in sorted({template_requirement(t) for t in gated})
            if num_metadata
        }
        print(f"Row gating: on; rows satisfying each gated predicate: {rates}")
        print(f"QA pairs served by a gated template: {gated_served}")
    else:
        print("Row gating: off (no template declares a 'requires' predicate)")
    if num_unknown_speaker:
        print(
            f"Rows whose speaker code is not in SPEAKER_L1 "
            f"(L1 templates withheld): {num_unknown_speaker}"
        )
    if l1_served:
        print(f"QA pairs served by an L1 template, by alias: {dict(sorted(l1_served.items()))}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate L2-Arctic PunctuatedASR QA JSONL from template JSONL "
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
        "--text-field",
        default="text",
        help="Metadata field holding the reference transcript, read to evaluate 'requires' predicates.",
    )
    parser.add_argument(
        "--gating",
        default="auto",
        choices=["auto", "on", "off"],
        help=(
            "Offer a template declaring a 'requires' predicate (period_final, "
            "has_comma, comma_and_period) only to rows whose text satisfies it. "
            "'auto' enables gating only when such templates exist."
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
        text_field=args.text_field,
        gating=args.gating,
    )
