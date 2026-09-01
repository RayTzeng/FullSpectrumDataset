#!/usr/bin/env python3
"""
Generate Target Speaker ASR QA pairs from a weighted template JSONL and a metadata JSONL(.gz).

Each metadata entry carries TWO audio inputs in a fixed order:
    paths[0] = target-speaker enrollment clip
    paths[1] = multi-talker meeting segment
Templates refer to them either by ordinal ("the first audio" / "the second audio") or by
the placeholder tags <audio_1> / <audio_2>; both are literal text here, so nothing in this
script rewrites them -- the training harness is responsible for binding audio to position.

Target field: `target_text` -- newline-separated utterances of the target speaker only.

Supported template schemas (mixed within one file is fine):
- {"question": "...", "answer": "...", "weight": ...}
- {"question_template": "...", "answer_template": "...", "weight": ...}

Output format:
{"question": "...", "answer": "...", "metadata": {...}}

Example:
python generate_qa.py \
  --template-jsonl template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/AMI/TargetSpeakerASR/train.jsonl.gz \
  --output train.jsonl.gz \
  --mode weighted_sample \
  --samples-per-entry 1 \
  --seed 42
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import json
import math
import random
import re
import sys
from typing import Any, Dict, Iterable, Iterator, List, Mapping

try:
    from tqdm import tqdm
except ImportError:  # progress is optional
    def tqdm(it, **kwargs):
        return it


# --------------------------------------------------------------------------- io

def open_text(path: str, mode: str = "rt"):
    """Open plain text or gzip-compressed text files."""
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """Yield JSON objects from a .jsonl or .jsonl.gz file, one at a time."""
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


def write_jsonl_gz(path: str, records: Iterable[Dict[str, Any]]) -> int:
    """Write records to .jsonl.gz (or .jsonl if not ending with .gz). Returns count."""
    n = 0
    with open_text(path, "wt") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
    return n


# ------------------------------------------------------------------- formatters


def flatten_target(target_text: Any) -> str:
    """All target-speaker utterances joined into one whitespace-normalised line."""
    return re.sub(r"\s+", " ", str(target_text)).strip()


def count_turns(target_text: Any) -> int:
    """Number of separate utterances the target speaker takes in the segment."""
    return len([l for l in str(target_text).split("\n") if l.strip()])


def turn_cascade(target_text: Any) -> str:
    """'The target speaker takes N turns.' then a blank line, then the transcript."""
    n = count_turns(target_text)
    lead = "The target speaker takes 1 turn." if n == 1 else f"The target speaker takes {n} turns."
    return f"{lead}\n\n{target_text}"


def turn_cascade_compact(target_text: Any) -> str:
    """'Turns: N' header line, then the transcript."""
    return f"Turns: {count_turns(target_text)}\n{target_text}"


SAFE_GLOBALS = {
    "__builtins__": {},
    "flatten_target": flatten_target,
    "count_turns": count_turns,
    "turn_cascade": turn_cascade,
    "turn_cascade_compact": turn_cascade_compact,
    "str": str, "int": int, "float": float, "bool": bool, "len": len,
    "sorted": sorted, "list": list, "set": set, "join": str.join,
}


def safe_eval(expr: str, context: Mapping[str, Any]) -> Any:
    """Evaluate a restricted answer expression over metadata fields and the formatters."""
    return eval(expr, dict(SAFE_GLOBALS), dict(context))  # noqa: S307


# --------------------------------------------------------------------- templates

class SafeDict(dict):
    """format_map helper that leaves unknown placeholders untouched."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def load_templates(path: str) -> List[Dict[str, Any]]:
    templates: List[Dict[str, Any]] = []
    for obj in iter_jsonl(path):
        question = obj.get("question_template", obj.get("question"))
        answer = obj.get("answer_template", obj.get("answer"))
        if question is None or answer is None:
            raise ValueError(f"Template missing question/answer fields: {obj}")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(f"Answer expression must be a non-empty string: {obj}")
        try:
            weight = float(obj.get("weight", 1.0))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid weight in template: {obj}") from e
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"Weight must be > 0 and finite, got {weight} in template: {obj}")
        t = dict(obj)
        t["_question"] = question
        t["_answer"] = answer
        t["_weight"] = weight
        templates.append(t)
    if not templates:
        raise ValueError(f"No templates loaded from {path}")
    return templates


def instantiate_question(template: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    question = template["_question"]
    try:
        return question.format_map(SafeDict(context))
    except Exception as e:
        raise ValueError(f"Failed to format question: {question}") from e


def instantiate_answer(template: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    expr = template["_answer"].strip()
    if expr in context:  # fast path: bare field name
        value = context[expr]
        return "" if value is None else str(value)
    try:
        value = safe_eval(expr, context)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression: {expr}\n"
            f"Available context keys: {sorted(context.keys())}"
        ) from e
    return "" if value is None else str(value)


# ---------------------------------------------------------------------- sampling

class WeightedPicker:
    """Weighted sampling without replacement inside a single metadata entry."""

    def __init__(self, templates: List[Dict[str, Any]], uniform: bool = False):
        self.templates = templates
        weights = [1.0 if uniform else t["_weight"] for t in templates]
        self.cum: List[float] = []
        running = 0.0
        for w in weights:
            running += w
            self.cum.append(running)
        self.total = running

    def _draw(self, rng: random.Random) -> int:
        return bisect.bisect_right(self.cum, rng.random() * self.total)

    def pick(self, k: int, rng: random.Random) -> List[Dict[str, Any]]:
        if k >= len(self.templates):
            return list(self.templates)
        chosen: List[int] = []
        seen = set()
        attempts = 0
        max_attempts = 40 * k
        while len(chosen) < k and attempts < max_attempts:
            attempts += 1
            i = min(self._draw(rng), len(self.templates) - 1)
            if i not in seen:
                seen.add(i)
                chosen.append(i)
        while len(chosen) < k:  # pathological fallback: fill uniformly
            i = rng.randrange(len(self.templates))
            if i not in seen:
                seen.add(i)
                chosen.append(i)
        return [self.templates[i] for i in chosen]


# -------------------------------------------------------------------- generation

def generate_records(
    templates: List[Dict[str, Any]],
    metadata_path: str,
    mode: str,
    samples_per_entry: int,
    rng: random.Random,
    target_field: str,
    keep_metadata: bool,
    stats: Dict[str, int],
) -> Iterator[Dict[str, Any]]:
    picker = WeightedPicker(templates, uniform=(mode == "random_sample"))

    for entry in tqdm(iter_jsonl(metadata_path), desc="entries", unit="seg"):
        stats["entries"] += 1
        target = entry.get(target_field)
        if target is None:
            stats["missing_target"] += 1
            continue
        if not str(target).strip():
            stats["empty_target"] += 1
            continue

        context = dict(entry)
        chosen = templates if mode == "cartesian" else picker.pick(samples_per_entry, rng)

        for template in chosen:
            yield {
                "question": instantiate_question(template, context),
                "answer": instantiate_answer(template, context),
                "metadata": dict(entry) if keep_metadata else {},
            }
            stats["records"] += 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate Target Speaker ASR QA pairs from templates and metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--template-jsonl", "--template", dest="template_jsonl", required=True,
                   help="Path to template .jsonl file.")
    p.add_argument("--metadata", required=True,
                   help="Path to metadata .jsonl or .jsonl.gz file.")
    p.add_argument("--output", required=True,
                   help="Path to output .jsonl.gz (or .jsonl).")
    p.add_argument("--mode", choices=["weighted_sample", "random_sample", "cartesian"],
                   default="weighted_sample",
                   help="weighted_sample: sample by template weight; random_sample: uniform; "
                        "cartesian: every template for every entry.")
    p.add_argument("--samples-per-entry", "--num-templates-per-entry", dest="samples_per_entry",
                   type=int, default=1,
                   help="Templates drawn per metadata entry (ignored in cartesian mode).")
    p.add_argument("--target-field", default="target_text",
                   help="Metadata field holding the reference target; entries missing it are skipped.")
    p.add_argument("--seed", type=int, default=42, help="Random seed.")
    p.add_argument("--no-keep-metadata", action="store_true",
                   help="Emit an empty metadata object instead of the full entry.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.samples_per_entry <= 0:
        raise SystemExit("--samples-per-entry must be >= 1")

    try:
        templates = load_templates(args.template_jsonl)
    except (OSError, ValueError) as e:
        raise SystemExit(f"Could not load templates from {args.template_jsonl}: {e}")

    if args.mode != "cartesian" and args.samples_per_entry > len(templates):
        print(f"[warn] --samples-per-entry {args.samples_per_entry} exceeds the "
              f"{len(templates)} available templates; every template will be used per entry.",
              file=sys.stderr)

    rng = random.Random(args.seed)
    stats = {"entries": 0, "records": 0, "empty_target": 0, "missing_target": 0}

    try:
        n = write_jsonl_gz(args.output, generate_records(
            templates=templates,
            metadata_path=args.metadata,
            mode=args.mode,
            samples_per_entry=args.samples_per_entry,
            rng=rng,
            target_field=args.target_field,
            keep_metadata=not args.no_keep_metadata,
            stats=stats,
        ))
    except (OSError, ValueError) as e:
        raise SystemExit(f"Generation failed: {e}")

    print(f"{args.output}: {n} QA pairs from {stats['entries']} entries "
          f"({len(templates)} templates, mode={args.mode}, "
          f"samples/entry={args.samples_per_entry}, seed={args.seed})")
    if stats["empty_target"] or stats["missing_target"]:
        print(f"  skipped: {stats['empty_target']} entries with an empty "
              f"'{args.target_field}', {stats['missing_target']} missing it entirely")


if __name__ == "__main__":
    main()
