#!/usr/bin/env python3
"""
Generate QA pairs from weighted prompt templates and metadata.

Input:
  - template.jsonl
  - metadata.jsonl.gz (or .jsonl)

Output:
  - output.jsonl.gz

Each output row has the format:
  {"question": ..., "answer": ..., "metadata": {...}}

Example:
  python generate_qa.py \
      --template-jsonl templates.jsonl \
      --metadata metadata.jsonl.gz \
      --output qa_pairs.jsonl.gz \
      --samples-per-entry 3 \
      --seed 42 \
      --keep-metadata

Notes:
  - Templates are sampled according to their "weight" field.
  - question_template is formatted with metadata fields via str.format(**metadata).
  - answer_template is evaluated in a restricted environment using metadata fields.
  - Supports .jsonl and .jsonl.gz for both input metadata and output.
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


def open_text(path: str, mode: str = "rt"):
    """Open a plain-text or gzipped file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def read_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    """Yield JSON objects from a .jsonl or .jsonl.gz file."""
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON on line {line_no} of {path}: {e}") from e


def write_jsonl_gz(path: str, rows: Iterable[Dict[str, Any]]) -> None:
    """Write JSON objects to .jsonl.gz."""
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def validate_template(template: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Validate and normalize one template row."""
    required = ["template_id", "question_template", "answer_template"]
    for key in required:
        if key not in template:
            raise ValueError(f"Template #{idx} is missing required field: {key}")

    weight = template.get("weight", 1.0)
    if not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
        raise ValueError(
            f"Template #{idx} ({template.get('template_id')}) has invalid weight: {weight!r}. "
            "Weight must be a positive finite number."
        )

    sampling_config = template.get("sampling_config", {})
    if sampling_config is None:
        sampling_config = {}
    if not isinstance(sampling_config, dict):
        raise ValueError(
            f"Template #{idx} ({template.get('template_id')}) has invalid sampling_config: "
            "must be a dict if provided."
        )

    normalized = {
        "template_id": template["template_id"],
        "question_template": template["question_template"],
        "answer_template": template["answer_template"],
        "weight": float(weight),
        "sampling_config": sampling_config,
    }
    return normalized


def sample_from_config(spec: Dict[str, Any], rng: random.Random) -> Any:
    """
    Sample a value from one sampling config spec.

    Supported formats:
      {"type": "choice", "values": [...]}
      {"type": "int", "min": 1, "max": 5}
      {"type": "float", "min": 0.0, "max": 1.0}
      {"type": "bool"}
    """
    if "type" not in spec:
        raise ValueError(f"sampling_config item missing 'type': {spec}")

    typ = spec["type"]

    if typ == "choice":
        values = spec.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError(f"choice sampling requires non-empty 'values': {spec}")
        return rng.choice(values)

    if typ == "int":
        min_v = spec.get("min")
        max_v = spec.get("max")
        if not isinstance(min_v, int) or not isinstance(max_v, int) or min_v > max_v:
            raise ValueError(f"int sampling requires valid integer min/max: {spec}")
        return rng.randint(min_v, max_v)

    if typ == "float":
        min_v = spec.get("min")
        max_v = spec.get("max")
        if not isinstance(min_v, (int, float)) or not isinstance(max_v, (int, float)) or min_v > max_v:
            raise ValueError(f"float sampling requires valid numeric min/max: {spec}")
        return rng.uniform(float(min_v), float(max_v))

    if typ == "bool":
        return rng.choice([True, False])

    raise ValueError(f"Unsupported sampling_config type: {typ}")


def sample_template_variables(sampling_config: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """Sample all variables defined in sampling_config."""
    sampled: Dict[str, Any] = {}
    for key, spec in sampling_config.items():
        sampled[key] = sample_from_config(spec, rng)
    return sampled


class SafeEvalVisitor(ast.NodeVisitor):
    """
    Minimal AST validator for answer expressions.

    Allows:
      - literals
      - variable names
      - attribute calls like caption.lower()
      - simple function calls from safe globals
      - indexing/slicing
      - list/tuple/dict/set literals
      - boolean/comparison/arithmetic operators
      - conditional expressions
      - comprehensions
      - joins and common string/list ops through attribute access
    Disallows:
      - imports
      - lambdas
      - assignments
      - walrus
      - class/def
      - accessing double-underscore attributes
    """

    ALLOWED_NODES = {
        ast.Expression,
        ast.Constant,
        ast.Name,
        ast.Load,
        ast.Attribute,
        ast.Call,
        ast.Subscript,
        ast.Slice,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Set,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.IfExp,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
        ast.comprehension,
        ast.JoinedStr,
        ast.FormattedValue,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Not,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.In,
        ast.NotIn,
        ast.Is,
        ast.IsNot,
    }

    def generic_visit(self, node):
        if type(node) not in self.ALLOWED_NODES:
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr.startswith("__"):
            raise ValueError("Double-underscore attribute access is not allowed.")
        self.visit(node.value)

    def visit_Call(self, node: ast.Call):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            self.visit(kw.value)


SAFE_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
    "sorted": sorted,
    "round": round,
    "abs": abs,
    "list": list,
    "tuple": tuple,
    "set": set,
    "dict": dict,
    "enumerate": enumerate,
    "zip": zip,
    "range": range,
    "any": any,
    "all": all,
}


def safe_eval(expr: str, context: Dict[str, Any]) -> Any:
    """Safely evaluate a restricted answer_template expression."""
    try:
        tree = ast.parse(expr, mode="eval")
        SafeEvalVisitor().visit(tree)
        compiled = compile(tree, "<answer_template>", "eval")
        return eval(compiled, SAFE_GLOBALS, context)
    except Exception as e:
        keys = sorted(context.keys())
        raise ValueError(
            f"Failed to evaluate answer_template: {expr!r}. "
            f"Available context keys: {keys}. Error: {e}"
        ) from e


_FIELD_PATTERN = re.compile(r"{([^{}]+)}")


def find_format_fields(template_str: str) -> List[str]:
    """
    Extract likely format field names from a str.format template.
    This is intentionally simple and works for standard cases like:
      {caption}, {threshold}, {value:.2f}
    """
    fields = []
    for raw in _FIELD_PATTERN.findall(template_str):
        # Strip format spec/conversion if present.
        field = raw.split("!")[0].split(":")[0].strip()
        if field:
            fields.append(field)
    return fields


def render_question(question_template: str, context: Dict[str, Any]) -> str:
    """Render question_template using standard Python str.format."""
    try:
        return question_template.format(**context)
    except KeyError as e:
        missing = e.args[0]
        fields = find_format_fields(question_template)
        raise ValueError(
            f"Missing field {missing!r} when formatting question_template: {question_template!r}. "
            f"Referenced fields: {fields}. Context keys: {sorted(context.keys())}"
        ) from e
    except Exception as e:
        raise ValueError(
            f"Failed to render question_template: {question_template!r}. Error: {e}"
        ) from e


def weighted_sample_templates(
    templates: Sequence[Dict[str, Any]],
    k: int,
    rng: random.Random,
    with_replacement: bool,
) -> List[Dict[str, Any]]:
    """Sample k templates according to weight."""
    if k <= 0:
        return []

    if with_replacement:
        weights = [t["weight"] for t in templates]
        return rng.choices(list(templates), weights=weights, k=k)

    if k > len(templates):
        raise ValueError(
            f"Requested {k} samples per entry without replacement, "
            f"but only {len(templates)} templates are available."
        )

    remaining = list(templates)
    chosen: List[Dict[str, Any]] = []
    for _ in range(k):
        weights = [t["weight"] for t in remaining]
        picked = rng.choices(remaining, weights=weights, k=1)[0]
        chosen.append(picked)
        remaining.remove(picked)
    return chosen


def build_output_row(
    template: Dict[str, Any],
    metadata: Dict[str, Any],
    rng: random.Random,
    keep_metadata: bool,
    include_template_id: bool,
) -> Dict[str, Any]:
    """Instantiate one template against one metadata entry."""
    sampled_vars = sample_template_variables(template.get("sampling_config", {}), rng)

    context = dict(metadata)
    context.update(sampled_vars)

    question = render_question(template["question_template"], context)
    answer = safe_eval(template["answer_template"], context)

    if not isinstance(answer, str):
        # Keep behavior predictable for sequence-generation tasks.
        answer = str(answer)

    out: Dict[str, Any] = {
        "question": question,
        "answer": answer,
        "metadata": metadata if keep_metadata else {},
    }

    if include_template_id:
        out["template_id"] = template["template_id"]

    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weighted QA pairs from templates and metadata.")
    parser.add_argument("--template-jsonl", required=True, help="Path to template JSONL.")
    parser.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz.")
    parser.add_argument("--output", required=True, help="Path to output .jsonl.gz.")
    parser.add_argument(
        "--samples-per-entry",
        type=int,
        default=1,
        help="Number of templates to sample for each metadata entry.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--with-replacement",
        action="store_true",
        help="Sample templates with replacement for each metadata entry.",
    )
    parser.add_argument(
        "--keep-metadata",
        action="store_true",
        default=True,
        help="Keep the original metadata object in the output row. "
             "If omitted, output uses an empty metadata dict.",
    )
    parser.add_argument(
        "--include-template-id",
        action="store_true",
        help="Include template_id in each output row for debugging/auditing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be >= 1")

    if not args.output.endswith(".gz"):
        raise ValueError("--output must end with .jsonl.gz")

    rng = random.Random(args.seed)

    templates = [
        validate_template(t, idx=i)
        for i, t in enumerate(read_jsonl(args.template_jsonl), start=1)
    ]
    if not templates:
        raise ValueError("No templates found.")

    metadata_rows = list(read_jsonl(args.metadata))
    if not metadata_rows:
        raise ValueError("No metadata rows found.")

    def row_generator() -> Iterable[Dict[str, Any]]:
        for entry_idx, metadata in enumerate(metadata_rows, start=1):
            selected_templates = weighted_sample_templates(
                templates=templates,
                k=args.samples_per_entry,
                rng=rng,
                with_replacement=args.with_replacement,
            )

            for sample_idx, template in enumerate(selected_templates, start=1):
                try:
                    yield build_output_row(
                        template=template,
                        metadata=metadata,
                        rng=rng,
                        keep_metadata=args.keep_metadata,
                        include_template_id=args.include_template_id,
                    )
                except Exception as e:
                    meta_id = metadata.get("id", f"<entry_{entry_idx}>")
                    raise RuntimeError(
                        f"Failed on metadata entry {meta_id!r}, sample {sample_idx}, "
                        f"template {template.get('template_id')!r}: {e}"
                    ) from e

    write_jsonl_gz(args.output, row_generator())


if __name__ == "__main__":
    main()