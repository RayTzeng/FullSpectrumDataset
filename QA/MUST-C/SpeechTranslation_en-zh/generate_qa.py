#!/usr/bin/env python3
"""
Generate QA pairs for speech translation tasks from a weighted template JSONL and
a metadata JSONL/JSONL.GZ file.

Output format (JSONL.GZ):
{"question": ..., "answer": ..., "metadata": {...}}

This version supports:
1. weighted template sampling
2. source/target language alias lists
3. optional alias weights

Behavior:
- question_template uses randomly sampled aliases for {source_language} and {target_language}
- answer_template uses the SAME sampled aliases as the question

Example:
python generate_st_qa.py \
  --template-jsonl template.jsonl \
  --metadata metadata.jsonl.gz \
  --output qa.jsonl.gz \
  --samples-per-entry 2 \
  --source-language Spanish Español Espanol \
  --source-language-weights 0.8 0.15 0.05 \
  --target-language English Inglés Ingles \
  --target-language-weights 0.85 0.10 0.05 \
  --seed 42 \
  --keep-metadata
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import re
from typing import Any, Dict, Iterable, List, Sequence


PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def open_text(path: str, mode: str = "rt"):
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open_text(path, "rt") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON on line {line_num} of {path}: {e}") from e
    return records


def write_jsonl_gz(path: str, records: Iterable[Dict[str, Any]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_templates(templates: Sequence[Dict[str, Any]]) -> None:
    required = {"template_id", "question_template", "answer_template", "weight"}
    for i, template in enumerate(templates):
        missing = required - set(template.keys())
        if missing:
            raise ValueError(
                f"Template index {i} is missing required fields: {sorted(missing)}"
            )
        weight = template["weight"]
        if not isinstance(weight, (int, float)) or weight <= 0:
            raise ValueError(
                f"Template {template.get('template_id', i)} has invalid weight: {weight}"
            )


def validate_alias_weights(
    aliases: Sequence[str],
    weights: Sequence[float] | None,
    arg_name: str,
) -> List[float]:
    if not aliases:
        raise ValueError(f"{arg_name} must contain at least one alias.")

    if weights is None:
        return [1.0] * len(aliases)

    if len(weights) != len(aliases):
        raise ValueError(
            f"{arg_name}-weights must have the same length as {arg_name}. "
            f"Got {len(weights)} weights for {len(aliases)} aliases."
        )

    validated: List[float] = []
    for i, w in enumerate(weights):
        if not isinstance(w, (int, float)) or w <= 0:
            raise ValueError(
                f"{arg_name}-weights contains invalid value at position {i}: {w}. "
                f"All alias weights must be > 0."
            )
        validated.append(float(w))

    return validated


def substitute_placeholders(template_str: str, values: Dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(
                f"Placeholder {{{key}}} not found in context. "
                f"Available keys: {sorted(values.keys())}"
            )
        return str(values[key])

    return PLACEHOLDER_PATTERN.sub(repl, template_str)


def safe_globals() -> Dict[str, Any]:
    return {
        "__builtins__": {},
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "len": len,
        "min": min,
        "max": max,
        "round": round,
        "abs": abs,
        "sum": sum,
        "sorted": sorted,
        "math": math,
        "json": json,
    }


def render_answer_expression(expr: str, context: Dict[str, Any]) -> str:
    try:
        value = eval(expr, safe_globals(), context)
    except Exception as e:
        context_keys = sorted(context.keys())
        raise ValueError(
            f"Failed to evaluate answer_template expression:\n{expr}\n"
            f"Context keys: {context_keys}\n"
            f"Error: {type(e).__name__}: {e}"
        ) from e

    if isinstance(value, str):
        return value
    return str(value)


def weighted_sample_indices(
    rng: random.Random,
    weights: Sequence[float],
    k: int,
    with_replacement: bool,
) -> List[int]:
    if k <= 0:
        return []

    if with_replacement:
        population = list(range(len(weights)))
        return rng.choices(population, weights=weights, k=k)

    if k > len(weights):
        raise ValueError(
            f"Cannot sample {k} templates without replacement from {len(weights)} templates."
        )

    chosen: List[int] = []
    remaining_indices = list(range(len(weights)))
    remaining_weights = list(weights)

    for _ in range(k):
        total = sum(remaining_weights)
        if total <= 0:
            raise ValueError("All remaining template weights are non-positive.")
        r = rng.random() * total
        cumsum = 0.0
        pick_pos = 0
        for j, w in enumerate(remaining_weights):
            cumsum += w
            if r <= cumsum:
                pick_pos = j
                break
        chosen.append(remaining_indices[pick_pos])
        del remaining_indices[pick_pos]
        del remaining_weights[pick_pos]

    return chosen


def build_context(
    metadata: Dict[str, Any],
    source_language_alias: str,
    target_language_alias: str,
) -> Dict[str, Any]:
    context = dict(metadata)
    context["source_language"] = source_language_alias
    context["target_language"] = target_language_alias
    return context


def sample_alias(
    rng: random.Random,
    aliases: Sequence[str],
    alias_weights: Sequence[float],
) -> str:
    return rng.choices(list(aliases), weights=list(alias_weights), k=1)[0]


def generate_examples(
    templates: Sequence[Dict[str, Any]],
    metadata_records: Sequence[Dict[str, Any]],
    samples_per_entry: int,
    source_language_aliases: Sequence[str],
    source_language_alias_weights: Sequence[float],
    target_language_aliases: Sequence[str],
    target_language_alias_weights: Sequence[float],
    rng: random.Random,
    with_replacement: bool,
    keep_metadata: bool,
) -> Iterable[Dict[str, Any]]:
    weights = [float(t["weight"]) for t in templates]

    for metadata in metadata_records:
        sampled_indices = weighted_sample_indices(
            rng=rng,
            weights=weights,
            k=samples_per_entry,
            with_replacement=with_replacement,
        )

        for template_index in sampled_indices:
            template = templates[template_index]

            source_alias = sample_alias(
                rng=rng,
                aliases=source_language_aliases,
                alias_weights=source_language_alias_weights,
            )
            target_alias = sample_alias(
                rng=rng,
                aliases=target_language_aliases,
                alias_weights=target_language_alias_weights,
            )

            context = build_context(
                metadata=metadata,
                source_language_alias=source_alias,
                target_language_alias=target_alias,
            )

            question_template = str(template["question_template"])
            answer_template = str(template["answer_template"])

            question = substitute_placeholders(question_template, context)
            answer_expr = substitute_placeholders(answer_template, context)
            answer = render_answer_expression(answer_expr, context)

            record: Dict[str, Any] = {
                "question": question,
                "answer": answer,
                "metadata": dict(metadata) if keep_metadata else {
                    "id": metadata.get("id"),
                    "template_id": template.get("template_id"),
                    "source_language": source_alias,
                    "target_language": target_alias,
                },
            }

            if keep_metadata:
                record["metadata"]["template_id"] = template.get("template_id")
                record["metadata"]["source_language"] = source_alias
                record["metadata"]["target_language"] = target_alias

            yield record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate weighted QA pairs from template JSONL and metadata JSONL/JSONL.GZ."
    )
    parser.add_argument(
        "--template-jsonl",
        type=str,
        required=True,
        help="Path to template JSONL file.",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        required=True,
        help="Path to metadata JSONL or JSONL.GZ file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output JSONL.GZ file.",
    )
    parser.add_argument(
        "--samples-per-entry",
        type=int,
        default=1,
        help="Number of QA pairs to generate per metadata entry.",
    )
    parser.add_argument(
        "--source-language",
        type=str,
        nargs="+",
        required=True,
        help="One or more aliases for the source language, e.g. Spanish Español Espanol",
    )
    parser.add_argument(
        "--source-language-weights",
        type=float,
        nargs="+",
        default=None,
        help="Optional weights for --source-language aliases.",
    )
    parser.add_argument(
        "--target-language",
        type=str,
        nargs="+",
        required=True,
        help="One or more aliases for the target language, e.g. English Inglés Ingles",
    )
    parser.add_argument(
        "--target-language-weights",
        type=float,
        nargs="+",
        default=None,
        help="Optional weights for --target-language aliases.",
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
        help="Sample templates with replacement. Default: without replacement.",
    )
    parser.add_argument(
        "--keep-metadata",
        default=True,
        action="store_true",
        help="Keep the full original metadata in output records.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be positive.")
    if not args.output.endswith(".jsonl.gz"):
        raise ValueError("--output must end with .jsonl.gz")

    source_language_alias_weights = validate_alias_weights(
        aliases=args.source_language,
        weights=args.source_language_weights,
        arg_name="--source-language",
    )
    target_language_alias_weights = validate_alias_weights(
        aliases=args.target_language,
        weights=args.target_language_weights,
        arg_name="--target-language",
    )

    rng = random.Random(args.seed)

    templates = read_jsonl(args.template_jsonl)
    metadata_records = read_jsonl(args.metadata)

    validate_templates(templates)

    if not args.with_replacement and args.samples_per_entry > len(templates):
        raise ValueError(
            f"--samples-per-entry={args.samples_per_entry} exceeds number of templates "
            f"({len(templates)}) while sampling without replacement."
        )

    generated = generate_examples(
        templates=templates,
        metadata_records=metadata_records,
        samples_per_entry=args.samples_per_entry,
        source_language_aliases=args.source_language,
        source_language_alias_weights=source_language_alias_weights,
        target_language_aliases=args.target_language,
        target_language_alias_weights=target_language_alias_weights,
        rng=rng,
        with_replacement=args.with_replacement,
        keep_metadata=args.keep_metadata,
    )

    write_jsonl_gz(args.output, generated)


if __name__ == "__main__":
    main()