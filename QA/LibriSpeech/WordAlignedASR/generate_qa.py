#!/usr/bin/env python3
import argparse
import gzip
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def smart_open(path: str, mode: str = "rt"):
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with smart_open(path, "rt") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON on line {line_no} of {path}: {e}") from e
    return records


def write_jsonl_gz(path: str, records: Iterable[Dict[str, Any]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_templates(raw_templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    templates: List[Dict[str, Any]] = []
    for i, t in enumerate(raw_templates):
        if "question" not in t or "answer" not in t:
            raise ValueError(f"Template index {i} must contain 'question' and 'answer'.")

        weight = t.get("weight", 1.0)
        if not isinstance(weight, (int, float)) or weight <= 0:
            raise ValueError(
                f"Template index {i} has invalid weight={weight!r}. "
                "Weights must be numeric and > 0."
            )

        templates.append(
            {
                "question": t["question"],
                "answer": t["answer"],
                "weight": float(weight),
                "template_id": t.get("template_id"),
            }
        )
    return templates


def weighted_choice_indices(
    rng: random.Random,
    weights: List[float],
    k: int,
) -> List[int]:
    if k <= 0:
        return []
    population = list(range(len(weights)))
    return rng.choices(population=population, weights=weights, k=k)


def render_question(template_question: str, metadata: Dict[str, Any]) -> str:
    try:
        return template_question.format(**metadata)
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(
            f"Missing metadata field '{missing}' required by question template: {template_question}"
        ) from e
    except Exception as e:
        raise ValueError(
            f"Failed to render question template: {template_question}\nError: {e}"
        ) from e


def safe_eval_answer(expr: str, metadata: Dict[str, Any]) -> Any:
    """
    Evaluate answer expressions like:
      aligned_text
      aligned_text.upper()
      aligned_text.replace('\\n', '; ')
      '\\n'.join(f'{i+1}. {line}' for i, line in enumerate(aligned_text.split('\\n')))
    """
    safe_globals: Dict[str, Any] = {
        "__builtins__": {},
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "enumerate": enumerate,
        "range": range,
        "zip": zip,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "list": list,
        "tuple": tuple,
        "set": set,
        "dict": dict,
        "abs": abs,
        "round": round,
        "math": math,
    }

    context = dict(metadata)

    try:
        # Pass the same context as locals so comprehensions/f-strings can see metadata fields.
        return eval(expr, safe_globals, context)
    except NameError:
        # If answer is a bare field name stored as a string, return it directly when possible.
        if expr in metadata:
            return metadata[expr]
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression: {expr}\nError: {e}"
        ) from e


def build_output_record(
    template: Dict[str, Any],
    metadata: Dict[str, Any],
    include_template_id: bool = False,
) -> Dict[str, Any]:
    question = render_question(template["question"], metadata)
    answer_value = safe_eval_answer(template["answer"], metadata)

    if not isinstance(answer_value, str):
        answer_value = str(answer_value)

    out: Dict[str, Any] = {
        "question": question,
        "answer": answer_value,
        "metadata": metadata,
    }

    if include_template_id and template.get("template_id") is not None:
        out["template_id"] = template["template_id"]

    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate QA pairs from a template JSONL and metadata JSONL(.gz), "
            "sampling templates according to their weights."
        )
    )
    parser.add_argument(
        "--template-jsonl",
        required=True,
        help="Path to template JSONL file.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to metadata JSONL or JSONL.GZ file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output .jsonl.gz file.",
    )
    parser.add_argument(
        "--samples-per-entry",
        type=int,
        default=1,
        help="Number of QA pairs to sample per metadata entry. Default: 1",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed. Default: 42",
    )
    parser.add_argument(
        "--include-template-id",
        action="store_true",
        help="Include template_id in each output record when available.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Fail immediately on template rendering/evaluation errors. "
            "By default, problematic samples are skipped with a warning."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be > 0")

    if not args.output.endswith(".jsonl.gz"):
        raise ValueError("--output must end with .jsonl.gz")

    rng = random.Random(args.seed)

    raw_templates = read_jsonl(args.template_jsonl)
    templates = normalize_templates(raw_templates)
    metadata_records = read_jsonl(args.metadata)

    if not templates:
        raise ValueError("No templates found.")
    if not metadata_records:
        raise ValueError("No metadata records found.")

    weights = [t["weight"] for t in templates]
    chosen_indices_per_entry = [
        weighted_choice_indices(rng, weights, args.samples_per_entry)
        for _ in metadata_records
    ]

    total_written = 0
    total_skipped = 0

    def record_stream():
        nonlocal total_written, total_skipped
        for meta_idx, metadata in enumerate(metadata_records):
            chosen_indices = chosen_indices_per_entry[meta_idx]
            for template_idx in chosen_indices:
                template = templates[template_idx]
                try:
                    record = build_output_record(
                        template=template,
                        metadata=metadata,
                        include_template_id=args.include_template_id,
                    )
                    total_written += 1
                    yield record
                except Exception as e:
                    total_skipped += 1
                    msg = (
                        f"[WARN] Skipping sample for metadata index {meta_idx}, "
                        f"template index {template_idx}: {e}"
                    )
                    if args.strict:
                        raise RuntimeError(msg) from e
                    print(msg, file=sys.stderr)

    write_jsonl_gz(args.output, record_stream())

    print(
        f"Done. Wrote {total_written} QA pairs to {args.output}. "
        f"Skipped {total_skipped} problematic samples.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()