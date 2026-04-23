#!/usr/bin/env python3
"""
Generate Stage-2 QA pairs for ParaSpeechCaps F0 Estimation.

Input template JSONL:
  Each line should contain:
    {
      "template_id": "...",
      "question_template": "...",
      "answer_template": "...",
      "sampling_config": {...},   # optional
      "weight": 0.9
    }

Input metadata JSONL.GZ:
  Each line should contain at least:
    {
      "id": "...",
      "path": "...",
      "sampling_rate": 44100,
      "duration": 17.76,
      "dataset": "ParaSpeechCaps",
      "F0": 105
    }

Output JSONL.GZ:
  Each line:
    {
      "question": "...",
      "answer": "...",
      "metadata": {...}
    }

Example:
  python generate_stage2_qa.py \
    --template-jsonl stage2_f0_template.jsonl \
    --metadata paraspeechcaps_f0_metadata.jsonl.gz \
    --output paraspeechcaps_f0_stage2_qa.jsonl.gz \
    --samples-per-entry 3 \
    --seed 42
"""

import argparse
import gzip
import json
import random
import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional


class SafeFormatDict(dict):
    """A format dictionary that raises a clearer error for missing fields."""

    def __missing__(self, key: str) -> Any:
        raise KeyError(f"Missing field or sampled variable: {key}")


def open_text(path: str, mode: str):
    """Open plain text or gzip text file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode + "t", encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str) -> Iterable[tuple[int, Dict[str, Any]]]:
    with open_text(path, "r") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_no, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}: {e}") from e


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    return [record for _, record in iter_jsonl(path)]


def validate_templates(templates: List[Dict[str, Any]]) -> None:
    if not templates:
        raise ValueError("No templates were loaded.")

    for idx, tmpl in enumerate(templates):
        for key in ("question_template", "answer_template"):
            if key not in tmpl:
                raise ValueError(f"Template index {idx} is missing required key `{key}`.")

        weight = tmpl.get("weight", 1.0)
        try:
            weight = float(weight)
        except Exception as e:
            raise ValueError(
                f"Template index {idx} has a non-numeric weight: {weight}"
            ) from e

        if weight <= 0:
            raise ValueError(f"Template index {idx} has non-positive weight: {weight}")

        tmpl["weight"] = weight

        sampling_config = tmpl.get("sampling_config", {})
        if sampling_config is not None and not isinstance(sampling_config, dict):
            raise ValueError(
                f"Template index {idx} has invalid sampling_config; expected dict."
            )


def normalize_f0(record: Dict[str, Any]) -> None:
    if "F0" not in record:
        raise KeyError(f"Metadata entry is missing target field `F0`: {record}")

    try:
        f0 = float(record["F0"])
    except Exception as e:
        raise ValueError(f"Invalid F0 value: {record.get('F0')}") from e

    if f0 <= 0:
        raise ValueError(f"F0 must be positive, got {record.get('F0')}")

    # Keep values such as 105 as integer-looking.
    record["F0"] = int(f0) if f0.is_integer() else f0


def weighted_sample_templates(
    templates: List[Dict[str, Any]],
    k: int,
    rng: random.Random,
    replace: bool,
) -> List[Dict[str, Any]]:
    if k <= 0:
        return []

    if replace:
        return rng.choices(
            templates,
            weights=[t["weight"] for t in templates],
            k=k,
        )

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

        acc = 0.0
        chosen_idx = len(remaining) - 1
        for i, w in enumerate(weights):
            acc += w
            if acc >= r:
                chosen_idx = i
                break

        selected.append(remaining.pop(chosen_idx))

    return selected


def sample_from_config(
    sampling_config: Optional[Dict[str, Any]],
    rng: random.Random,
) -> Dict[str, Any]:
    """
    Sample variables from template sampling_config.

    Supported:
      {
        "threshold": {
          "type": "choice",
          "values": [80, 100, 120]
        }
      }

      {
        "interval": {
          "type": "choice",
          "values": [{"lower": 80, "upper": 120}, ...],
          "unpack": true
        }
      }

    If unpack=true and sampled value is a dict, its keys are merged into context.
    Otherwise, sampled value is assigned to the sampling_config key.
    """
    sampled: Dict[str, Any] = {}

    if not sampling_config:
        return sampled

    for name, spec in sampling_config.items():
        if not isinstance(spec, dict):
            raise ValueError(f"Invalid sampling spec for `{name}`: expected dict.")

        spec_type = spec.get("type")
        if spec_type != "choice":
            raise ValueError(
                f"Unsupported sampling_config type for `{name}`: {spec_type}. "
                "Currently only type='choice' is supported."
            )

        values = spec.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError(f"Sampling spec `{name}` must contain a non-empty values list.")

        value = deepcopy(rng.choice(values))

        if spec.get("unpack", False):
            if not isinstance(value, dict):
                raise ValueError(
                    f"Sampling spec `{name}` has unpack=true, but sampled value is not a dict."
                )
            sampled.update(value)
        else:
            sampled[name] = value

    return sampled


def format_question(question_template: str, context: Mapping[str, Any]) -> str:
    try:
        return question_template.format_map(SafeFormatDict(context))
    except Exception as e:
        raise ValueError(
            f"Failed to instantiate question template:\n"
            f"  template: {question_template}\n"
            f"  context keys: {sorted(context.keys())}\n"
            f"  error: {e}"
        ) from e


def looks_like_expression(answer_template: str) -> bool:
    """
    Stage-2 answer templates are usually Python expressions, e.g.
      {'yes' if F0 >= threshold else 'no'}
      f'{abs(F0 - target)} Hz'

    Stage-1 templates may be format strings, e.g.
      {F0} Hz

    This function decides whether to eval or format.
    """
    stripped = answer_template.strip()

    if stripped.startswith("f'") or stripped.startswith('f"'):
        return True

    expression_markers = [
        " if ",
        " else ",
        "abs(",
        "round(",
        "min(",
        "max(",
        "F0 -",
        "- target",
        "lower <=",
        "F0 <",
        "F0 >",
        "F0 >=",
        "F0 <=",
    ]

    return any(marker in stripped for marker in expression_markers)


def safe_eval_answer(answer_template: str, context: Mapping[str, Any]) -> str:
    """
    Evaluate a deterministic answer template.

    Supports both:
      - Python expression templates:
          {'yes' if F0 >= threshold else 'no'}
          f'{abs(F0 - target)} Hz'
      - Simple format templates:
          {F0} Hz
          F0: {F0} Hz

    The eval namespace is restricted to simple deterministic functions.
    """
    if not looks_like_expression(answer_template):
        try:
            return str(answer_template.format_map(SafeFormatDict(context)))
        except Exception as e:
            raise ValueError(
                f"Failed to format answer template:\n"
                f"  template: {answer_template}\n"
                f"  context keys: {sorted(context.keys())}\n"
                f"  error: {e}\n"
                f"If the template contains literal JSON braces, escape them as '{{' and '}}'."
            ) from e

    safe_globals = {
        "__builtins__": {},
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "int": int,
        "float": float,
        "str": str,
    }

    safe_locals = dict(context)

    try:
        value = eval(answer_template, safe_globals, safe_locals)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer template:\n"
            f"  template: {answer_template}\n"
            f"  context keys: {sorted(context.keys())}\n"
            f"  error: {e}"
        ) from e

    return str(value)


def build_output_metadata(
    record: Dict[str, Any],
    template: Dict[str, Any],
    sampled_vars: Dict[str, Any],
    keep_metadata: bool,
) -> Dict[str, Any]:
    metadata = deepcopy(record) if keep_metadata else {}

    metadata["template_id"] = template.get("template_id")
    metadata["template_weight"] = template.get("weight")

    if sampled_vars:
        metadata["sampled_variables"] = deepcopy(sampled_vars)

    return metadata


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

    n_entries = 0
    n_written = 0

    with open_text(output_path, "w") as fout:
        for line_no, record in iter_jsonl(metadata_path):
            n_entries += 1

            try:
                normalize_f0(record)
            except Exception as e:
                raise ValueError(f"Invalid metadata at line {line_no}: {e}") from e

            selected_templates = weighted_sample_templates(
                templates=templates,
                k=samples_per_entry,
                rng=rng,
                replace=replace,
            )

            for template in selected_templates:
                sampled_vars = sample_from_config(
                    template.get("sampling_config", {}),
                    rng=rng,
                )

                context: Dict[str, Any] = {}
                context.update(record)
                context.update(sampled_vars)

                question = format_question(template["question_template"], context)
                answer = safe_eval_answer(template["answer_template"], context)

                output_record = {
                    "question": question,
                    "answer": answer,
                    "metadata": build_output_metadata(
                        record=record,
                        template=template,
                        sampled_vars=sampled_vars,
                        keep_metadata=keep_metadata,
                    ),
                }

                fout.write(json.dumps(output_record, ensure_ascii=False) + "\n")
                n_written += 1

    print(f"Loaded templates: {len(templates)}")
    print(f"Processed metadata entries: {n_entries}")
    print(f"Wrote QA pairs: {n_written}")
    print(f"Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Stage-2 QA pairs for ParaSpeechCaps F0 Estimation."
    )
    parser.add_argument(
        "--template-jsonl",
        required=True,
        help="Path to weighted Stage-2 template JSONL.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to metadata JSONL or JSONL.GZ.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output JSONL or JSONL.GZ.",
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
        help="Do not keep original metadata fields. Template metadata is still included.",
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