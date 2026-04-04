#!/usr/bin/env python3
"""
Generate QA pairs from a weighted template JSONL file and a metadata JSONL/JSONL.GZ file.

Output format (one JSON object per line, gzipped):
    {"question": ..., "answer": ..., "metadata": {...}}

Expected template format:
    {"question": "...", "answer": "...", "weight": 0.83}

Notes
-----
- `question` is treated as a Python format string. Placeholders like `{text}` or `{id}`
  are filled from metadata.
- `answer` is evaluated using a restricted expression evaluator rather than raw eval.
- `weight` controls weighted template sampling. Missing/invalid/non-positive weights are
  treated as 0.0 and excluded from weighted sampling.
- By default, templates are sampled *without replacement* for each metadata entry so the
  same template is not drawn twice for the same example when `--num-templates-per-entry > 1`.

Examples
--------
# Sample 1 template per metadata entry according to template weights
python generate_weighted_qa.py \
  --template template.jsonl \
  --metadata metadata.jsonl.gz \
  --output qa.jsonl.gz \
  --num-templates-per-entry 1 \
  --seed 42

# Sample 3 templates per metadata entry, allowing repeated templates
python generate_weighted_qa.py \
  --template template.jsonl \
  --metadata metadata.jsonl.gz \
  --output qa.jsonl.gz \
  --num-templates-per-entry 3 \
  --sample-with-replacement \
  --seed 42
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import math
import random
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
                for value in values:
                    result = result and value
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for value in values:
                    result = result or value
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
    with open_text_auto(path) as file_obj:
        for line_no, line in enumerate(file_obj, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return items


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    with open_text_auto(path) as file_obj:
        for line_no, line in enumerate(file_obj, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc


def render_question(question_template: str, metadata: Dict[str, Any]) -> str:
    return question_template.format_map(SafeDict(metadata))


def render_answer(answer_expr: Any, metadata: Dict[str, Any]) -> Any:
    if not isinstance(answer_expr, str):
        return answer_expr
    evaluator = SafeEvaluator(metadata)
    return evaluator.eval(answer_expr)


def normalize_weight(template: Dict[str, Any]) -> float:
    try:
        weight = float(template.get("weight", 1.0))
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(weight) or math.isinf(weight) or weight <= 0:
        return 0.0
    return weight


def weighted_choice_with_replacement(
    templates: Sequence[Dict[str, Any]],
    weights: Sequence[float],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if k <= 0:
        return []
    return rng.choices(list(templates), weights=list(weights), k=k)


def weighted_sample_without_replacement(
    templates: Sequence[Dict[str, Any]],
    weights: Sequence[float],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if k <= 0:
        return []

    candidates = [(tpl, w) for tpl, w in zip(templates, weights) if w > 0]
    if not candidates:
        return []
    if k >= len(candidates):
        return [tpl for tpl, _ in candidates]

    # Efraimidis-Spirakis weighted sampling without replacement.
    scored: List[tuple[float, Dict[str, Any]]] = []
    for tpl, weight in candidates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        key = math.log(u) / weight  # larger (closer to 0) is better
        scored.append((key, tpl))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [tpl for _, tpl in scored[:k]]


def choose_templates(
    templates: Sequence[Dict[str, Any]],
    weights: Sequence[float],
    num_templates_per_entry: int,
    sample_with_replacement: bool,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if sample_with_replacement:
        return weighted_choice_with_replacement(
            templates=templates,
            weights=weights,
            k=num_templates_per_entry,
            rng=rng,
        )
    return weighted_sample_without_replacement(
        templates=templates,
        weights=weights,
        k=num_templates_per_entry,
        rng=rng,
    )


def validate_templates(templates: Sequence[Dict[str, Any]]) -> List[float]:
    if not templates:
        raise ValueError("No templates found.")

    required_keys = {"question", "answer"}
    weights: List[float] = []
    positive_count = 0

    for idx, template in enumerate(templates):
        missing = required_keys - template.keys()
        if missing:
            raise ValueError(f"Template #{idx} is missing required keys: {sorted(missing)}")
        weight = normalize_weight(template)
        weights.append(weight)
        if weight > 0:
            positive_count += 1

    if positive_count == 0:
        raise ValueError("No templates have positive weights.")

    return weights


def ensure_gzip_output_path(path: str) -> str:
    path_obj = Path(path)
    if str(path_obj).endswith(".jsonl.gz"):
        return str(path_obj)
    if path_obj.suffix == ".gz":
        return str(path_obj)
    if path_obj.suffix == ".jsonl":
        return str(path_obj) + ".gz"
    return str(path_obj) + ".jsonl.gz"


def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    num_templates_per_entry: int,
    sample_with_replacement: bool,
    seed: int,
) -> None:
    if num_templates_per_entry <= 0:
        raise ValueError("--num-templates-per-entry must be a positive integer.")

    templates = load_jsonl(template_path)
    weights = validate_templates(templates)
    rng = random.Random(seed)

    output_path = ensure_gzip_output_path(output_path)

    num_metadata = 0
    num_written = 0

    with gzip.open(output_path, "wt", encoding="utf-8") as out_file:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1
            chosen_templates = choose_templates(
                templates=templates,
                weights=weights,
                num_templates_per_entry=num_templates_per_entry,
                sample_with_replacement=sample_with_replacement,
                rng=rng,
            )
            for template in chosen_templates:
                question = render_question(str(template["question"]), metadata)
                answer = render_answer(template["answer"], metadata)
                record = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }
                out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)}")
    print(f"Templates with positive weight: {sum(w > 0 for w in weights)}")
    print(f"Processed metadata entries: {num_metadata}")
    print(f"Wrote QA pairs: {num_written}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate weighted QA JSONL.GZ from template JSONL and metadata JSONL/JSONL.GZ."
    )
    parser.add_argument("--template", required=True, help="Path to template .jsonl")
    parser.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz")
    parser.add_argument("--output", required=True, help="Path to output .jsonl.gz")
    parser.add_argument(
        "--num-templates-per-entry",
        type=int,
        default=1,
        help="How many templates to sample for each metadata entry.",
    )
    parser.add_argument(
        "--sample-with-replacement",
        action="store_true",
        help="Sample templates with replacement. Default is without replacement.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        num_templates_per_entry=args.num_templates_per_entry,
        sample_with_replacement=args.sample_with_replacement,
        seed=args.seed,
    )
