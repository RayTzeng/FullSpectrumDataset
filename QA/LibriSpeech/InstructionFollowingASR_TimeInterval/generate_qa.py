#!/usr/bin/env python3
"""
Generate QA pairs for Instruction-Following ASR (Time Interval) by:
1. reading a template JSONL file
2. reading metadata from a .jsonl.gz file
3. routing each metadata entry to the correct scenario based on time_interval
4. sampling templates according to per-template weights
5. rendering question/answer pairs
6. writing output to a .jsonl.gz file

Output format:
{"question": ..., "answer": ..., "metadata": {...}}

Expected template schema:
{
  "template_id": "...",
  "scenario": "after" | "before" | "between",
  "question_template": "...",
  "answer_template": "text",
  "weight": 0.87
}

Expected metadata fields:
{
  "time_interval": [start, end],
  "text": "..."
}

Scenario routing:
- after   : [start, -1]
- before  : [-1, end]
- between : [start, end]
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple


@dataclass
class Template:
    template_id: str
    scenario: str
    question_template: str
    answer_template: str
    weight: float


_VALID_SCENARIOS = {"after", "before", "between"}
_PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate weighted QA pairs for Instruction-Following ASR (Time Interval)."
    )
    parser.add_argument(
        "--template-jsonl",
        required=True,
        help="Path to template JSONL file.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to input metadata .jsonl.gz file.",
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
        help="Number of QA pairs to generate per metadata entry. Default: 1",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed. Default: 42",
    )
    parser.add_argument(
        "--keep-metadata",
        default=True,
        action="store_true",
        help="Keep the full original metadata in the output. If not set, output still uses the key 'metadata' but only stores the original entry unchanged as well. This flag is included for CLI compatibility.",
    )
    parser.add_argument(
        "--deduplicate-templates-per-entry",
        default=True,
        action="store_true",
        help="If set, avoid sampling the same template_id more than once for the same metadata entry when possible.",
    )
    return parser.parse_args()


def open_text(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def open_text_write(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "wt", encoding="utf-8")
    return open(path, "w", encoding="utf-8")


def load_templates(path: str) -> Dict[str, List[Template]]:
    templates_by_scenario: Dict[str, List[Template]] = defaultdict(list)

    with open_text(path) as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in template file at line {line_num}: {e}") from e

            template_id = obj.get("template_id")
            scenario = obj.get("scenario")
            question_template = obj.get("question_template")
            answer_template = obj.get("answer_template")
            weight = obj.get("weight", 1.0)

            if not isinstance(template_id, str) or not template_id:
                raise ValueError(f"Template line {line_num}: missing or invalid template_id")
            if scenario not in _VALID_SCENARIOS:
                raise ValueError(
                    f"Template line {line_num}: scenario must be one of {_VALID_SCENARIOS}, got {scenario!r}"
                )
            if not isinstance(question_template, str) or not question_template:
                raise ValueError(f"Template line {line_num}: missing or invalid question_template")
            if not isinstance(answer_template, str) or not answer_template:
                raise ValueError(f"Template line {line_num}: missing or invalid answer_template")
            if not isinstance(weight, (int, float)) or weight <= 0:
                raise ValueError(f"Template line {line_num}: weight must be a positive number")

            templates_by_scenario[scenario].append(
                Template(
                    template_id=template_id,
                    scenario=scenario,
                    question_template=question_template,
                    answer_template=answer_template,
                    weight=float(weight),
                )
            )

    for scenario in _VALID_SCENARIOS:
        if not templates_by_scenario.get(scenario):
            print(f"Warning: no templates found for scenario '{scenario}'", file=sys.stderr)

    return dict(templates_by_scenario)


def infer_scenario(entry: Dict[str, Any]) -> str:
    time_interval = entry.get("time_interval")
    if (
        not isinstance(time_interval, list)
        or len(time_interval) != 2
        or not all(isinstance(x, (int, float)) for x in time_interval)
    ):
        raise ValueError(f"Invalid time_interval: {time_interval!r}")

    start, end = time_interval

    if start == -1 and end == -1:
        raise ValueError(f"Ambiguous time_interval with both endpoints unbounded: {time_interval!r}")
    if end == -1:
        return "after"
    if start == -1:
        return "before"
    return "between"


def format_time_value(x: float) -> str:
    # Keep integers clean, preserve concise decimals otherwise.
    if float(x).is_integer():
        return str(int(x))
    return f"{x:g}"


def build_render_context(entry: Dict[str, Any]) -> Dict[str, Any]:
    ctx = dict(entry)

    time_interval = entry["time_interval"]
    start, end = time_interval

    ctx["start_time"] = format_time_value(start) if start != -1 else "-1"
    ctx["end_time"] = format_time_value(end) if end != -1 else "-1"

    return ctx


def render_question(template: str, context: Dict[str, Any]) -> str:
    try:
        return template.format(**context)
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(f"Missing placeholder '{missing}' required by question_template: {template!r}") from e


def safe_eval_answer(expr: str, context: Dict[str, Any]) -> Any:
    """
    Evaluate answer_template in a restricted environment.

    Typical usage:
    - "text"
    - "text.lower()"
    - "text.upper()"
    """

    safe_globals = {
        "__builtins__": {},
        "str": str,
        "int": int,
        "float": float,
        "len": len,
        "min": min,
        "max": max,
        "round": round,
        "sorted": sorted,
    }

    try:
        return eval(expr, safe_globals, context)
    except Exception as e:
        raise ValueError(f"Failed to evaluate answer_template {expr!r}: {e}") from e


def weighted_sample_templates(
    templates: List[Template],
    k: int,
    rng: random.Random,
    deduplicate: bool = False,
) -> List[Template]:
    if not templates:
        raise ValueError("No templates available for sampling")

    if not deduplicate or k <= 1:
        weights = [t.weight for t in templates]
        return rng.choices(templates, weights=weights, k=k)

    # Weighted sampling without replacement when possible.
    # If k > len(templates), sample all once, then sample the remainder with replacement.
    selected: List[Template] = []
    remaining = templates[:]

    draws_without_replacement = min(k, len(remaining))
    for _ in range(draws_without_replacement):
        weights = [t.weight for t in remaining]
        chosen = rng.choices(remaining, weights=weights, k=1)[0]
        selected.append(chosen)
        remaining = [t for t in remaining if t.template_id != chosen.template_id]

    remainder = k - len(selected)
    if remainder > 0:
        weights = [t.weight for t in templates]
        selected.extend(rng.choices(templates, weights=weights, k=remainder))

    return selected


def validate_metadata_entry(entry: Dict[str, Any], line_num: int) -> None:
    if not isinstance(entry, dict):
        raise ValueError(f"Metadata line {line_num}: expected JSON object")
    if "time_interval" not in entry:
        raise ValueError(f"Metadata line {line_num}: missing time_interval")
    if "text" not in entry:
        raise ValueError(f"Metadata line {line_num}: missing text")


def generate(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    keep_metadata: bool,
    deduplicate_templates_per_entry: bool,
) -> None:
    rng = random.Random(seed)
    templates_by_scenario = load_templates(template_jsonl)

    num_entries = 0
    num_outputs = 0

    with open_text(metadata_path) as fin, open_text_write(output_path) as fout:
        for line_num, raw_line in enumerate(fin, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in metadata file at line {line_num}: {e}") from e

            validate_metadata_entry(entry, line_num)
            scenario = infer_scenario(entry)

            scenario_templates = templates_by_scenario.get(scenario, [])
            if not scenario_templates:
                raise ValueError(f"No templates available for scenario '{scenario}'")

            context = build_render_context(entry)
            chosen_templates = weighted_sample_templates(
                templates=scenario_templates,
                k=samples_per_entry,
                rng=rng,
                deduplicate=deduplicate_templates_per_entry,
            )

            for template in chosen_templates:
                question = render_question(template.question_template, context)
                answer = safe_eval_answer(template.answer_template, context)

                if not isinstance(answer, str):
                    answer = str(answer)

                output_obj = {
                    "question": question,
                    "answer": answer,
                    "metadata": entry if keep_metadata or True else {},
                }
                fout.write(json.dumps(output_obj, ensure_ascii=False) + "\n")
                num_outputs += 1

            num_entries += 1

    print(
        f"Done. Processed {num_entries} metadata entries and wrote {num_outputs} QA pairs to {output_path}",
        file=sys.stderr,
    )


def main() -> None:
    args = parse_args()
    generate(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        keep_metadata=args.keep_metadata,
        deduplicate_templates_per_entry=args.deduplicate_templates_per_entry,
    )


if __name__ == "__main__":
    main()