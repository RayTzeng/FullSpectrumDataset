#!/usr/bin/env python3
"""
Generate QA pairs for ParaSpeechCaps F0 Estimation.

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
         "sampling_rate": 44100,
         "duration": 17.76,
         "dataset": "ParaSpeechCaps",
         "F0": 105
       }

Output:
  output.jsonl.gz
  Each line:
       {
         "question": "...",
         "answer": "...",
         "metadata": {...}
       }

Example:
  python generate_stage1_qa.py \
    --template-jsonl stage1_template.jsonl \
    --metadata paraspeechcaps_f0.jsonl.gz \
    --output stage1_f0_qa.jsonl.gz \
    --samples-per-entry 1 \
    --seed 42
"""

import argparse
import ast
import gzip
import json
import random
from copy import deepcopy
from typing import Any, Dict, List


def open_text(path: str, mode: str):
    """Open plain text or gzip text file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode + "t", encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records = []
    with open_text(path, "r") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}: {e}") from e
    return records


def iter_jsonl(path: str):
    with open_text(path, "r") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_no, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}: {e}") from e


def validate_templates(templates: List[Dict[str, Any]]) -> None:
    if not templates:
        raise ValueError("No templates found.")

    for i, tmpl in enumerate(templates):
        for key in ["question_template", "answer_template"]:
            if key not in tmpl:
                raise ValueError(f"Template index {i} is missing required key: {key}")

        weight = tmpl.get("weight", 1.0)
        try:
            weight = float(weight)
        except Exception as e:
            raise ValueError(f"Template index {i} has non-numeric weight: {tmpl.get('weight')}") from e

        if weight <= 0:
            raise ValueError(f"Template index {i} has non-positive weight: {weight}")

        tmpl["weight"] = weight


def weighted_sample_templates(
    templates: List[Dict[str, Any]],
    k: int,
    replace: bool,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    """Sample templates according to their weight."""
    if k <= 0:
        return []

    if replace:
        weights = [t["weight"] for t in templates]
        return rng.choices(templates, weights=weights, k=k)

    if k > len(templates):
        raise ValueError(
            f"Cannot sample {k} templates without replacement from only "
            f"{len(templates)} templates. Use --replace."
        )

    # Weighted sampling without replacement.
    remaining = list(templates)
    selected = []

    for _ in range(k):
        weights = [t["weight"] for t in remaining]
        total = sum(weights)
        r = rng.random() * total

        upto = 0.0
        chosen_idx = None
        for idx, w in enumerate(weights):
            upto += w
            if upto >= r:
                chosen_idx = idx
                break

        if chosen_idx is None:
            chosen_idx = len(remaining) - 1

        selected.append(remaining.pop(chosen_idx))

    return selected


def safe_eval_answer_template(answer_template: str, context: Dict[str, Any]) -> str:
    """
    Evaluate an answer template.

    Supported forms:
      "{F0} Hz"
      "{F0}"
      "F0: {F0} Hz"
      "{\"F0_Hz\": {F0}}"

    This function uses Python str.format_map, not arbitrary eval.
    It is intentionally conservative for Stage-1 templates.
    """
    try:
        return answer_template.format_map(context)
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(
            f"Answer template references missing metadata field or variable: {missing}. "
            f"Template: {answer_template}"
        ) from e


def instantiate_question(question_template: str, context: Dict[str, Any]) -> str:
    """Instantiate question template using metadata/config context."""
    try:
        return question_template.format_map(context)
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(
            f"Question template references missing metadata field or variable: {missing}. "
            f"Template: {question_template}"
        ) from e


def normalize_f0_value(record: Dict[str, Any]) -> None:
    """
    Ensure F0 is available and clean.

    The task target field is `F0`, already rounded to nearest 5 Hz.
    We preserve the metadata value rather than re-rounding it.
    """
    if "F0" not in record:
        raise KeyError(f"Metadata entry is missing target field `F0`: {record.get('id', '<no id>')}")

    try:
        f0 = float(record["F0"])
    except Exception as e:
        raise ValueError(
            f"Invalid F0 value for entry {record.get('id', '<no id>')}: {record['F0']}"
        ) from e

    if f0 <= 0:
        raise ValueError(
            f"Non-positive F0 value for entry {record.get('id', '<no id>')}: {record['F0']}"
        )

    # Keep integer-looking values as int for cleaner formatting: 105 instead of 105.0.
    if f0.is_integer():
        record["F0"] = int(f0)
    else:
        record["F0"] = f0


def build_context(record: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build formatting context.

    Stage-1 F0 templates only need metadata fields.
    Template fields are also included in case you later want to reference template_id.
    """
    context = {}
    context.update(record)
    context.update(template)
    return context


def generate_qa_pairs(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    replace: bool,
    keep_metadata: bool,
) -> None:
    rng = random.Random(seed)

    templates = load_jsonl(template_jsonl)
    validate_templates(templates)

    n_in = 0
    n_out = 0

    with open_text(output_path, "w") as fout:
        for line_no, record in iter_jsonl(metadata_path):
            n_in += 1

            try:
                normalize_f0_value(record)
            except Exception as e:
                raise ValueError(f"Error in metadata line {line_no}: {e}") from e

            sampled_templates = weighted_sample_templates(
                templates=templates,
                k=samples_per_entry,
                replace=replace,
                rng=rng,
            )

            for tmpl in sampled_templates:
                context = build_context(record, tmpl)

                question = instantiate_question(tmpl["question_template"], context)
                answer = safe_eval_answer_template(tmpl["answer_template"], context)

                metadata = deepcopy(record) if keep_metadata else {}
                metadata["template_id"] = tmpl.get("template_id")
                metadata["template_weight"] = tmpl.get("weight")

                qa = {
                    "question": question,
                    "answer": answer,
                    "metadata": metadata,
                }

                fout.write(json.dumps(qa, ensure_ascii=False) + "\n")
                n_out += 1

    print(f"Loaded templates: {len(templates)}")
    print(f"Processed metadata entries: {n_in}")
    print(f"Wrote QA pairs: {n_out}")
    print(f"Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Stage-1 QA pairs for ParaSpeechCaps F0 Estimation."
    )

    parser.add_argument(
        "--template-jsonl",
        required=True,
        help="Path to weighted template JSONL file.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to metadata JSONL or JSONL.GZ file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output JSONL.GZ or JSONL file.",
    )
    parser.add_argument(
        "--samples-per-entry",
        type=int,
        default=1,
        help="Number of QA pairs to generate per metadata entry.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Sample templates with replacement for each metadata entry.",
    )
    parser.add_argument(
        "--no-keep-metadata",
        action="store_true",
        help="Do not keep original metadata fields in output. Template metadata is still included.",
    )

    args = parser.parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be positive.")

    generate_qa_pairs(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        replace=args.replace,
        keep_metadata=not args.no_keep_metadata,
    )


if __name__ == "__main__":
    main()