#!/usr/bin/env python3
"""
Generate QA pairs for IPA phoneme-recognition instruction templates.

Input:
  1. template.jsonl
     Each line should contain:
       {
         "template_id": "...",
         "question_template": "...",
         "answer_template": "...",
         "weight": 0.9
       }

  2. metadata.jsonl.gz
     Each line should contain at least:
       {
         "id": "...",
         "path": "...",
         "IPA": "...",
         ...
       }

Output:
  .jsonl.gz file where each line is:
       {
         "question": "...",
         "answer": "...",
         "metadata": {...}
       }

Example:
  python generate_qa.py \
    --template-jsonl template.jsonl \
    --metadata metadata.jsonl.gz \
    --output qa.jsonl.gz \
    --samples-per-entry 1 \
    --seed 42 \
    --keep-metadata
"""

import argparse
import ast
import gzip
import json
import random
from typing import Any, Dict, Iterable, List, Optional


def read_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    """Read either .jsonl or .jsonl.gz."""
    opener = gzip.open if path.endswith(".gz") else open
    mode = "rt"

    with opener(path, mode, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at {path}:{line_num}: {e}") from e


def write_jsonl_gz(path: str, rows: Iterable[Dict[str, Any]]) -> None:
    """Write rows to .jsonl.gz."""
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_templates(path: str) -> List[Dict[str, Any]]:
    templates = list(read_jsonl(path))
    if not templates:
        raise ValueError(f"No templates found in {path}")

    required_fields = {"question_template", "answer_template"}
    for i, t in enumerate(templates):
        missing = required_fields - set(t)
        if missing:
            raise ValueError(f"Template index {i} is missing fields: {sorted(missing)}")

        weight = t.get("weight", 1.0)
        try:
            weight = float(weight)
        except Exception as e:
            raise ValueError(f"Invalid weight in template index {i}: {t.get('weight')}") from e

        if not (0.0 < weight <= 1.0):
            raise ValueError(
                f"Weight must be in (0, 1], got {weight} in template index {i}"
            )

        t["weight"] = weight

    return templates


def normalize_pipe_spacing(text: str) -> str:
    """
    Normalize spacing around IPA word-boundary pipes.

    The templates assume the canonical format:
      phone phone | phone phone

    This helper makes answer-template behavior robust if metadata has:
      phone phone|phone phone
      phone phone |phone phone
      phone phone| phone phone
    """
    parts = [part.strip() for part in text.split("|")]
    return " | ".join(part for part in parts if part)


def render_question(question_template: str, metadata: Dict[str, Any]) -> str:
    """
    Render a question template.

    Current IPA templates are mostly literal strings, but this supports simple
    Python .format_map(...) fields if future templates include metadata fields,
    e.g. "Transcribe this {dataset} clip into IPA."
    """
    try:
        return question_template.format_map(SafeDict(metadata))
    except Exception as e:
        raise ValueError(
            f"Failed to render question_template={question_template!r} "
            f"for metadata id={metadata.get('id')!r}: {e}"
        ) from e


class SafeDict(dict):
    """Keep unresolved placeholders visible instead of crashing."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class SafeAnswerEvaluator(ast.NodeVisitor):
    """
    Evaluate restricted answer_template expressions.

    Supported examples:
      IPA
      IPA.replace(' | ', '\\n')
      IPA.replace(' | ', ' ')
      IPA.replace(' | ', ' ').replace(' ', ', ')
      '/' + IPA + '/'

    This intentionally does not allow arbitrary Python execution.
    """

    ALLOWED_METHODS = {"replace", "strip", "lower", "upper"}
    ALLOWED_NAMES = {"IPA"}

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def eval(self, expr: str) -> str:
        expr = expr.strip()

        # Common fast path: direct field lookup.
        if expr in self.context:
            return str(self.context[expr])

        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid answer_template syntax: {expr!r}") from e

        value = self.visit(tree.body)
        return str(value)

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.ALLOWED_NAMES:
            raise ValueError(f"Unsupported variable in answer_template: {node.id}")
        return self.context[node.id]

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, str):
            return node.value
        raise ValueError(f"Only string constants are supported: {node.value!r}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        if not isinstance(node.op, ast.Add):
            raise ValueError("Only string concatenation with + is supported")
        left = self.visit(node.left)
        right = self.visit(node.right)
        if not isinstance(left, str) or not isinstance(right, str):
            raise ValueError("Only string concatenation is supported")
        return left + right

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Attribute):
            raise ValueError("Only string method calls are supported")

        receiver = self.visit(node.func.value)
        method_name = node.func.attr

        if not isinstance(receiver, str):
            raise ValueError("Only string methods are supported")
        if method_name not in self.ALLOWED_METHODS:
            raise ValueError(f"Unsupported string method: {method_name}")

        args = [self.visit(arg) for arg in node.args]
        kwargs = {}
        if node.keywords:
            raise ValueError("Keyword arguments are not supported in answer_template")

        method = getattr(receiver, method_name)
        return method(*args, **kwargs)

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(
            f"Unsupported expression in answer_template: {type(node).__name__}"
        )


def evaluate_answer(answer_template: str, metadata: Dict[str, Any]) -> str:
    if "IPA" not in metadata:
        raise KeyError(f"Metadata entry {metadata.get('id')!r} is missing IPA field")

    context = dict(metadata)
    context["IPA"] = normalize_pipe_spacing(str(metadata["IPA"]))

    evaluator = SafeAnswerEvaluator(context)
    return evaluator.eval(answer_template)


def sample_template(
    templates: List[Dict[str, Any]],
    rng: random.Random,
) -> Dict[str, Any]:
    weights = [float(t["weight"]) for t in templates]
    return rng.choices(templates, weights=weights, k=1)[0]


def generate_rows(
    templates: List[Dict[str, Any]],
    metadata_path: str,
    samples_per_entry: int,
    rng: random.Random,
    keep_metadata: bool,
    keep_template_info: bool,
    skip_missing_ipa: bool,
) -> Iterable[Dict[str, Any]]:
    if samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be positive")

    for metadata in read_jsonl(metadata_path):
        if "IPA" not in metadata:
            if skip_missing_ipa:
                continue
            raise KeyError(f"Metadata entry {metadata.get('id')!r} is missing IPA field")

        for _ in range(samples_per_entry):
            template = sample_template(templates, rng)

            question = render_question(template["question_template"], metadata)
            answer = evaluate_answer(template["answer_template"], metadata)

            out_metadata = dict(metadata) if keep_metadata else {
                "id": metadata.get("id"),
                "path": metadata.get("path"),
                "dataset": metadata.get("dataset"),
                "duration": metadata.get("duration"),
                "sampling_rate": metadata.get("sampling_rate"),
            }

            if keep_template_info:
                out_metadata["template_id"] = template.get("template_id")
                out_metadata["template_weight"] = template.get("weight")
                out_metadata["answer_template"] = template.get("answer_template")

            yield {
                "question": question,
                "answer": answer,
                "metadata": out_metadata,
            }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate weighted QA pairs for IPA phoneme recognition."
    )
    parser.add_argument(
        "--template-jsonl",
        required=True,
        help="Path to weighted template JSONL.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to metadata .jsonl or .jsonl.gz.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path, recommended .jsonl.gz.",
    )
    parser.add_argument(
        "--samples-per-entry",
        type=int,
        default=1,
        help="Number of QA pairs to sample per metadata entry.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--keep-metadata",
        action="store_true",
        default=True,
        help="Keep full metadata in the output.",
    )
    parser.add_argument(
        "--keep-template-info",
        action="store_true",
        help="Store template_id, template_weight, and answer_template in output metadata.",
    )
    parser.add_argument(
        "--skip-missing-ipa",
        action="store_true",
        help="Skip metadata entries without an IPA field instead of raising an error.",
    )

    args = parser.parse_args()

    templates = load_templates(args.template_jsonl)
    rng = random.Random(args.seed)

    rows = generate_rows(
        templates=templates,
        metadata_path=args.metadata,
        samples_per_entry=args.samples_per_entry,
        rng=rng,
        keep_metadata=args.keep_metadata,
        keep_template_info=args.keep_template_info,
        skip_missing_ipa=args.skip_missing_ipa,
    )

    write_jsonl_gz(args.output, rows)


if __name__ == "__main__":
    main()