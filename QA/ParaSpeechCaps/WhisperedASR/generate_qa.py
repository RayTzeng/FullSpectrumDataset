#!/usr/bin/env python3
"""
Generate QA pairs by weighted-sampling templates for each metadata entry.

Input
-----
1. template.jsonl
   Each line must contain at least:
       {"question": "...", "answer": "...", "weight": 0.85}

2. metadata.jsonl or metadata.jsonl.gz
   Each line is one metadata dictionary.

Output
------
A .jsonl.gz file where each line is:
    {"question": ..., "answer": ..., "metadata": {...}}

Notes
-----
- The question string supports Python-style .format_map(...) placeholders,
  e.g. "Transcribe {id}".
- The answer field is evaluated with a restricted expression evaluator.
- Templates are sampled WITHOUT replacement for each metadata entry.
- If a template has no valid weight, weight=1.0 is used.
- Non-positive weights are ignored during sampling.
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


def get_positive_weight(template: Dict[str, Any]) -> float:
    raw_weight = template.get("weight", 1.0)
    try:
        weight = float(raw_weight)
    except (TypeError, ValueError):
        weight = 1.0

    if not math.isfinite(weight):
        return 0.0
    return max(weight, 0.0)


def weighted_sample_without_replacement(
    templates: Sequence[Dict[str, Any]],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    """Weighted sampling without replacement using Efraimidis-Spirakis."""
    weighted_templates = [
        (template, get_positive_weight(template))
        for template in templates
    ]
    weighted_templates = [
        (template, weight)
        for template, weight in weighted_templates
        if weight > 0.0
    ]

    if k <= 0 or not weighted_templates:
        return []

    if k >= len(weighted_templates):
        return [template for template, _ in weighted_templates]

    scored_templates = []
    for template, weight in weighted_templates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        score = math.log(u) / weight
        scored_templates.append((score, template))

    scored_templates.sort(key=lambda x: x[0], reverse=True)
    return [template for _, template in scored_templates[:k]]


def generate_qa(
    template_path: str,
    metadata_path: str,
    output_path: str,
    num_templates_per_entry: int,
    seed: int,
) -> None:
    templates = load_jsonl(template_path)
    if not templates:
        raise ValueError("No templates found in the template file.")

    required_keys = {"question", "answer"}
    for index, template in enumerate(templates):
        missing = required_keys - set(template.keys())
        if missing:
            raise ValueError(
                f"Template #{index} is missing required keys: {sorted(missing)}"
            )

    output_path_obj = Path(output_path)
    if output_path_obj.suffix != ".gz":
        if output_path_obj.suffix == ".jsonl":
            output_path_obj = output_path_obj.with_suffix(".jsonl.gz")
        else:
            output_path_obj = Path(str(output_path_obj) + ".jsonl.gz")

    rng = random.Random(seed)
    num_metadata_entries = 0
    num_output_rows = 0

    with gzip.open(output_path_obj, "wt", encoding="utf-8") as output_file:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Generating QA"):
            num_metadata_entries += 1
            selected_templates = weighted_sample_without_replacement(
                templates=templates,
                k=num_templates_per_entry,
                rng=rng,
            )

            for template in selected_templates:
                question = render_question(str(template["question"]), metadata)
                answer = render_answer(template["answer"], metadata)
                output_record = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }
                output_file.write(json.dumps(output_record, ensure_ascii=False) + "\n")
                num_output_rows += 1

    print(f"Templates loaded: {len(templates)}")
    print(f"Metadata entries processed: {num_metadata_entries}")
    print(f"QA pairs written: {num_output_rows}")
    print(f"Output path: {output_path_obj}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Weighted-sample templates and generate QA pairs as .jsonl.gz"
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to template .jsonl file (with optional weight field)",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to metadata .jsonl or .jsonl.gz file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output .jsonl.gz file",
    )
    parser.add_argument(
        "--num-templates-per-entry",
        type=int,
        default=1,
        help="How many templates to sample per metadata entry",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_qa(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        num_templates_per_entry=args.num_templates_per_entry,
        seed=args.seed,
    )
