#!/usr/bin/env python3
"""
Generate QA pairs from a weighted template JSONL and a metadata JSONL(.gz).

Supports mixed template schemas:
- {"question_template": "...", "answer_template": "...", "weight": ...}
- {"question": "...", "answer": "...", "weight": ...}

Output format:
{"question": "...", "answer": "...", "metadata": {...}}

Example:
python generate_qa.py \
  --template-jsonl template.jsonl \
  --metadata metadata.jsonl.gz \
  --output output.jsonl.gz \
  --samples-per-entry 1 \
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
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional


def open_text(path: str, mode: str = "rt"):
    """Open plain text or gzip-compressed text files."""
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """Yield JSON objects from a .jsonl or .jsonl.gz file."""
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}: {e}") from e
            if not isinstance(obj, dict):
                raise ValueError(
                    f"Expected a JSON object on line {line_no} of {path}, got {type(obj).__name__}"
                )
            yield obj


def write_jsonl_gz(path: str, records: Iterable[Dict[str, Any]]) -> None:
    """Write records to .jsonl.gz (or .jsonl if not ending with .gz)."""
    with open_text(path, "wt") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def smart_title(text: str) -> str:
    """
    Simple title-casing for accent display strings.
    Keeps slashes and hyphens intact reasonably well.
    """
    parts = re.split(r"(\s+|/|-)", text.strip())
    titled = []
    for part in parts:
        if re.fullmatch(r"\s+|/|-", part or ""):
            titled.append(part)
        else:
            titled.append(part[:1].upper() + part[1:].lower() if part else part)
    return "".join(titled)


def parse_accent_parts(accent: str) -> Dict[str, Optional[str]]:
    """
    Parse an accent label into:
    - base_raw
    - subtype_raw (inside parentheses), if any
    - has_parenthetical

    Example:
      "northern irish (culchie) english"
        -> base_raw="northern irish english", subtype_raw="culchie"
    """
    accent = normalize_space(str(accent))
    m = re.match(r"^(.*?)\((.*?)\)(.*)$", accent)
    if not m:
        return {
            "base_raw": accent,
            "subtype_raw": None,
            "has_parenthetical": False,
        }

    left = normalize_space(m.group(1))
    subtype = normalize_space(m.group(2))
    right = normalize_space(m.group(3))
    base = normalize_space(f"{left} {right}")
    return {
        "base_raw": base,
        "subtype_raw": subtype or None,
        "has_parenthetical": True,
    }


def accent_to_display(accent: str) -> str:
    """
    Display form used in accent-specific prompts, e.g.
      'united states english' -> 'United States English'
      'northern irish (culchie) english' -> 'Northern Irish (Culchie) English'
    """
    accent = normalize_space(str(accent))
    m = re.match(r"^(.*?)\((.*?)\)(.*)$", accent)
    if not m:
        return smart_title(accent)

    left = normalize_space(m.group(1))
    subtype = normalize_space(m.group(2))
    right = normalize_space(m.group(3))

    left_disp = smart_title(left)
    subtype_disp = smart_title(subtype)
    right_disp = smart_title(right)

    pieces = [p for p in [left_disp, right_disp] if p]
    outer = normalize_space(" ".join(pieces))
    return f"{outer.replace('  ', ' ').strip()[:-0] if outer else ''}".strip() and f"{left_disp} ({subtype_disp}) {right_disp}".strip()


def format_accent_cascade_region(accent: str, text: str) -> str:
    """
    Cascade output formatter:
    - no parentheses:
        It is United States English. Transcription: ...
    - with parentheses:
        It is Northern Irish English, specifically from Culchie Region. Transcription: ...
    """
    parts = parse_accent_parts(accent)
    base_display = smart_title(parts["base_raw"])
    subtype_raw = parts["subtype_raw"]

    if subtype_raw:
        subtype_display = smart_title(subtype_raw)
        return f"It is {base_display}, specifically from {subtype_display} Region. Transcription: {text}"
    return f"It is {base_display}. Transcription: {text}"


def build_format_context(metadata: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Context for question formatting and answer evaluation.
    Adds accent_display plus all metadata fields directly.
    """
    ctx = dict(metadata)
    accent = str(metadata.get("accent", ""))
    ctx["accent_display"] = accent_to_display(accent) if accent else ""
    return ctx


def safe_eval(expr: str, context: Mapping[str, Any]) -> Any:
    """
    Evaluate a restricted answer expression.

    Supported patterns:
    - direct field access: "text"
    - helper call: "format_accent_cascade_region(accent, text)"
    - simple Python expressions over metadata fields and provided helpers
    """
    allowed_globals = {
        "__builtins__": {},
        "format_accent_cascade_region": format_accent_cascade_region,
        "accent_to_display": accent_to_display,
        "smart_title": smart_title,
        "normalize_space": normalize_space,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "len": len,
    }
    return eval(expr, allowed_globals, dict(context))  # noqa: S307


def instantiate_question(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    question = template_obj.get("question_template", template_obj.get("question"))
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"Template missing valid question/question_template: {template_obj}")

    try:
        return question.format_map(SafeDict(context))
    except Exception as e:
        raise ValueError(f"Failed to format question: {question}\nContext keys: {sorted(context.keys())}") from e


def instantiate_answer(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    answer_expr = template_obj.get("answer_template", template_obj.get("answer"))
    if answer_expr is None:
        raise ValueError(f"Template missing answer/answer_template: {template_obj}")

    if not isinstance(answer_expr, str):
        raise ValueError(f"Answer expression must be a string, got {type(answer_expr).__name__}")

    answer_expr = answer_expr.strip()
    if not answer_expr:
        raise ValueError(f"Empty answer expression in template: {template_obj}")

    # Fast path: exact field name in context
    if answer_expr in context:
        value = context[answer_expr]
        return "" if value is None else str(value)

    try:
        value = safe_eval(answer_expr, context)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression: {answer_expr}\n"
            f"Available context keys: {sorted(context.keys())}"
        ) from e

    return "" if value is None else str(value)


class SafeDict(dict):
    """format_map helper that leaves unknown placeholders untouched."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def load_templates(path: str) -> List[Dict[str, Any]]:
    templates: List[Dict[str, Any]] = []
    for obj in iter_jsonl(path):
        question = obj.get("question_template", obj.get("question"))
        answer = obj.get("answer_template", obj.get("answer"))
        weight = obj.get("weight", 1.0)

        if question is None or answer is None:
            raise ValueError(f"Template missing question/answer fields: {obj}")

        try:
            weight = float(weight)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid weight in template: {obj}") from e

        if not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"Weight must be > 0 and finite, got {weight} in template: {obj}")

        templates.append(dict(obj))

    if not templates:
        raise ValueError(f"No templates loaded from {path}")
    return templates


def weighted_sample_template(
    templates: List[Dict[str, Any]],
    rng: random.Random,
) -> Dict[str, Any]:
    weights = [float(t.get("weight", 1.0)) for t in templates]
    return rng.choices(templates, weights=weights, k=1)[0]


def maybe_limit_metadata(metadata: Dict[str, Any], keep_metadata: bool) -> Dict[str, Any]:
    return metadata if keep_metadata else {}


def generate_records(
    template_path: str,
    metadata_path: str,
    samples_per_entry: int,
    rng: random.Random,
    keep_metadata: bool = True,
) -> Iterator[Dict[str, Any]]:
    templates = load_templates(template_path)

    for metadata in iter_jsonl(metadata_path):
        context = build_format_context(metadata)

        for _ in range(samples_per_entry):
            template_obj = weighted_sample_template(templates, rng)
            question = instantiate_question(template_obj, context)
            answer = instantiate_answer(template_obj, context)

            yield {
                "question": question,
                "answer": answer,
                "metadata": maybe_limit_metadata(metadata, keep_metadata),
            }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate weighted QA pairs from template JSONL and metadata JSONL(.gz)."
    )
    parser.add_argument(
        "--template-jsonl",
        type=str,
        required=True,
        help="Path to template .jsonl file.",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        required=True,
        help="Path to metadata .jsonl or .jsonl.gz file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output .jsonl.gz (or .jsonl).",
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
        default=0,
        help="Random seed.",
    )
    parser.add_argument(
        "--no-keep-metadata",
        action="store_true",
        help="If set, output an empty metadata object instead of the full metadata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be >= 1")

    rng = random.Random(args.seed)

    records = generate_records(
        template_path=args.template_jsonl,
        metadata_path=args.metadata,
        samples_per_entry=args.samples_per_entry,
        rng=rng,
        keep_metadata=not args.no_keep_metadata,
    )
    write_jsonl_gz(args.output, records)


if __name__ == "__main__":
    main()