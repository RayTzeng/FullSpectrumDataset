#!/usr/bin/env python3
"""
Generate QA pairs for MediaSum / DetailedSpeechSummarization.

Task: detailed speech summarization of spoken radio interviews. The answer is
grounded in the `summary` field of the metadata manifest; a small subset of
templates serialize that same summary as JSON.

The summaries here are the expert-annotated *detailed* ones (median 59 words /
3 sentences), which is why the templates ask for a detailed summary rather than
an unmarked one -- an unmarked "summarize this" prompt maps to much shorter
targets in the sibling MediaSum/ConciseSpeechSummarization and
Spoken-DREAM/SpeechDialogueSummarization sets.

Note that one audio file carries up to 6 reference summaries (AudioSum/TextSum/
WhisperSum, x2 annotators each), so the same `path` legitimately appears in
several entries with different answers.

Template schema (template.jsonl), one JSON object per line:
    {"template_id": "...", "category": "...",
     "question_template": "...", "answer_template": "...", "weight": 0.85}

Legacy {"question": ..., "answer": ...} keys are also accepted.

Output format (.jsonl.gz), one JSON object per line:
    {"question": "...", "answer": "...", "metadata": {...}}

Examples
--------
    # default: drop entries longer than 300s
    python generate_qa.py \
        --template template.jsonl \
        --metadata /path/to/train.jsonl.gz \
        --output train.jsonl.gz \
        --num-templates-per-entry 8 \
        --seed 42

    # keep everything regardless of length
    python generate_qa.py ... --max-duration inf
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
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional

try:
    from tqdm import tqdm
except ImportError:  # progress bar is optional
    def tqdm(iterable=None, **kwargs):  # type: ignore
        return iterable if iterable is not None else []


# --------------------------------------------------------------------------- io

def open_text(path: str, mode: str = "rt"):
    """Open plain-text or gzip-compressed text files transparently."""
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """Stream JSON objects from a .jsonl or .jsonl.gz file (never loads it all)."""
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
                    f"Expected a JSON object on line {line_no} of {path}, "
                    f"got {type(obj).__name__}"
                )
            yield obj


def count_lines(path: str) -> int:
    """Count non-empty lines, for the progress bar total."""
    n = 0
    with open_text(path, "rt") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def write_jsonl(path: str, records: Iterable[Dict[str, Any]]) -> int:
    """Write records to .jsonl.gz (or .jsonl). Returns the number written."""
    n = 0
    with open_text(path, "wt") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
    return n


# ---------------------------------------------------------------- duration gate

class DurationFilter:
    """Length gate applied to metadata entries before any QA pair is emitted.

    MediaSum interviews run 16.1s to 587.0s (median 232.8s), a long tail that is
    expensive to train on and that many audio encoders cannot take in one window.
    The default cap of 300s keeps ~83% of entries.

    Entries whose `duration` is missing or unparseable are kept and counted
    separately rather than silently dropped, so a malformed manifest shows up in
    the summary line instead of quietly shrinking the output.
    """

    def __init__(self, min_duration: float = 0.0, max_duration: float = 300.0):
        if math.isnan(min_duration) or math.isnan(max_duration):
            raise ValueError("--min-duration / --max-duration must not be NaN")
        # A non-positive cap is read as "no cap", matching --max-duration inf.
        self.max_duration = math.inf if max_duration <= 0 else max_duration
        self.min_duration = max(0.0, min_duration)
        if self.min_duration > self.max_duration:
            raise ValueError(
                f"--min-duration ({self.min_duration}) exceeds "
                f"--max-duration ({self.max_duration})"
            )
        self.n_seen = 0
        self.n_kept = 0
        self.n_too_long = 0
        self.n_too_short = 0
        self.n_no_duration = 0

    @property
    def active(self) -> bool:
        return self.min_duration > 0.0 or math.isfinite(self.max_duration)

    def keep(self, metadata: Mapping[str, Any]) -> bool:
        self.n_seen += 1
        try:
            duration = float(metadata["duration"])
        except (KeyError, TypeError, ValueError):
            self.n_no_duration += 1
            self.n_kept += 1
            return True
        if not math.isfinite(duration):
            self.n_no_duration += 1
            self.n_kept += 1
            return True
        if duration > self.max_duration:
            self.n_too_long += 1
            return False
        if duration < self.min_duration:
            self.n_too_short += 1
            return False
        self.n_kept += 1
        return True

    def summary(self) -> str:
        cap = "inf" if math.isinf(self.max_duration) else f"{self.max_duration:g}s"
        parts = [
            f"duration filter [{self.min_duration:g}s, {cap}]: "
            f"kept {self.n_kept}/{self.n_seen} entries"
        ]
        if self.n_too_long:
            parts.append(f"{self.n_too_long} too long")
        if self.n_too_short:
            parts.append(f"{self.n_too_short} too short")
        if self.n_no_duration:
            parts.append(f"{self.n_no_duration} without a usable duration (kept)")
        return ", ".join(parts)


# ------------------------------------------------------------ field formatting

def norm_ws(text: Any) -> str:
    """Collapse all whitespace runs to single spaces and strip the ends."""
    return re.sub(r"\s+", " ", str(text)).strip()


def duration_adj(duration: Any) -> str:
    """Attributive duration phrase: "45-second", "2.5-minute", "4-minute".

    Under 90s rounds to the nearest 5 seconds; at or above 90s rounds to the
    nearest half minute. Verified across this manifest's full 16.1s-587.0s range
    (yielding "15-second" through "10-minute"), so it stays correct whether or
    not --max-duration is in play. Templates using this always pair it with
    "this"/"the"/"a {duration_adj}", and every value it produces begins with a
    consonant sound, so no a/an agreement problem can arise.
    """
    d = float(duration)
    if d < 90.0:
        secs = max(5, int(round(d / 5.0) * 5))
        return f"{secs}-second"
    mins = round(d / 30.0) / 2.0
    return f"{mins:g}-minute"


def duration_len(duration: Any) -> str:
    """Predicative duration phrase: "45 seconds", "2.5 minutes", "4 minutes"."""
    d = float(duration)
    if d < 90.0:
        secs = max(5, int(round(d / 5.0) * 5))
        return f"{secs} seconds"
    mins = round(d / 30.0) / 2.0
    return f"{mins:g} minutes"


# ------------------------------------------------------------ answer formatters

def json_summary(summary: Any) -> str:
    """JSON object with a single "summary" key."""
    return json.dumps({"summary": str(summary)}, ensure_ascii=False)


# --------------------------------------------------------------- safe eval

_EVAL_GLOBALS = {
    "__builtins__": {},
    # field formatters
    "norm_ws": norm_ws,
    "duration_adj": duration_adj,
    "duration_len": duration_len,
    # answer formatters
    "json_summary": json_summary,
    # a few safe builtins
    "str": str, "int": int, "float": float, "bool": bool, "len": len,
}

_ALLOWED_NODES = (
    ast.Expression, ast.Call, ast.Name, ast.Load, ast.Attribute, ast.Constant,
    ast.BinOp, ast.Add, ast.Mod, ast.JoinedStr, ast.FormattedValue,
    ast.List, ast.Tuple, ast.Dict, ast.keyword,
)

_ALLOWED_METHODS = {
    "upper", "lower", "title", "strip", "rstrip", "lstrip",
    "replace", "join", "split", "format", "capitalize",
}


def _validate_expr(expr: str) -> ast.Expression:
    """Reject anything outside a small whitelist of expression nodes."""
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(
                f"Disallowed syntax {type(node).__name__} in answer expression: {expr!r}"
            )
        if isinstance(node, ast.Attribute) and node.attr not in _ALLOWED_METHODS:
            raise ValueError(
                f"Disallowed attribute .{node.attr} in answer expression: {expr!r}"
            )
    return tree


def safe_eval(expr: str, context: Mapping[str, Any]) -> Any:
    """Evaluate a restricted answer expression against the metadata context."""
    tree = _validate_expr(expr)
    compiled = compile(tree, "<answer_template>", "eval")
    return eval(compiled, dict(_EVAL_GLOBALS), dict(context))  # noqa: S307


# ------------------------------------------------------------------ rendering

class SafeDict(dict):
    """format_map helper that leaves unknown placeholders untouched."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def build_context(metadata: Mapping[str, Any]) -> Dict[str, Any]:
    """Metadata fields plus the derived values templates may reference."""
    ctx = dict(metadata)
    if "duration" in metadata:
        try:
            ctx["duration_adj"] = duration_adj(metadata["duration"])
            ctx["duration_len"] = duration_len(metadata["duration"])
        except (TypeError, ValueError):
            pass
    return ctx


def render_question(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    """Render the question. Literal braces in templates are doubled ({{ }})."""
    question = template_obj.get("question_template", template_obj.get("question"))
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"Template missing a usable question: {template_obj}")
    try:
        return question.format_map(SafeDict(context))
    except Exception as e:
        raise ValueError(
            f"Failed to render question {question!r} "
            f"(context keys: {sorted(context)}): {e}"
        ) from e


def render_answer(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    """Evaluate the answer expression against the metadata context."""
    expr = template_obj.get("answer_template", template_obj.get("answer"))
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError(f"Template missing a usable answer expression: {template_obj}")
    expr = expr.strip()

    if expr in context:  # fast path: bare field reference
        value = context[expr]
        return "" if value is None else str(value)

    try:
        value = safe_eval(expr, context)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression {expr!r} "
            f"(context keys: {sorted(context)}): {e}"
        ) from e
    return "" if value is None else str(value)


# ------------------------------------------------------------------ templates

def load_templates(path: str) -> List[Dict[str, Any]]:
    """Load and validate template.jsonl."""
    templates: List[Dict[str, Any]] = []
    for idx, obj in enumerate(iter_jsonl(path), start=1):
        question = obj.get("question_template", obj.get("question"))
        answer = obj.get("answer_template", obj.get("answer"))
        if question is None or answer is None:
            raise ValueError(f"Template #{idx} missing question/answer: {obj}")

        try:
            weight = float(obj.get("weight", 1.0))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Template #{idx} has a non-numeric weight: {obj}") from e
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"Template #{idx} weight must be finite and > 0: {obj}")

        _validate_expr(str(answer).strip())  # fail fast on a bad expression
        obj["weight"] = weight
        templates.append(obj)

    if not templates:
        raise ValueError(f"No templates loaded from {path}")
    return templates


def weighted_choices_without_replacement(
    templates: List[Dict[str, Any]], k: int, rng: random.Random
) -> List[Dict[str, Any]]:
    """
    Draw k distinct templates with probability proportional to weight.

    Uses the Efraimidis-Spirakis exponential-race trick: key_i = -ln(U_i)/w_i,
    then take the k smallest keys. Keeps repeats of the same audio entry from
    landing on the same prompt twice.
    """
    if k >= len(templates):
        return list(templates)
    keyed = []
    for t in templates:
        u = rng.random()
        while u <= 0.0:  # guard against log(0)
            u = rng.random()
        keyed.append((-math.log(u) / float(t["weight"]), t))
    keyed.sort(key=lambda pair: pair[0])
    return [t for _, t in keyed[:k]]


def select_templates(
    templates: List[Dict[str, Any]],
    k: int,
    mode: str,
    rng: random.Random,
    replace: bool,
) -> List[Dict[str, Any]]:
    """Pick k templates for one metadata entry according to --mode."""
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        if replace or k > len(templates):
            return [rng.choice(templates) for _ in range(k)]
        return rng.sample(templates, k)
    # weighted_sample (default)
    if replace or k > len(templates):
        weights = [t["weight"] for t in templates]
        return rng.choices(templates, weights=weights, k=k)
    return weighted_choices_without_replacement(templates, k, rng)


# ------------------------------------------------------------------ generation

CORE_METADATA_FIELDS = ("id", "path", "sampling_rate", "duration", "dataset")


def project_metadata(metadata: Mapping[str, Any], keep: str) -> Dict[str, Any]:
    if keep == "core":
        return {k: metadata[k] for k in CORE_METADATA_FIELDS if k in metadata}
    if keep == "none":
        return {}
    return dict(metadata)


def generate_records(
    template_path: str,
    metadata_path: str,
    num_per_entry: int,
    mode: str,
    rng: random.Random,
    keep_metadata: str,
    replace: bool,
    duration_filter: DurationFilter,
    total: Optional[int] = None,
) -> Iterator[Dict[str, Any]]:
    templates = load_templates(template_path)
    print(
        f"[generate_qa] {len(templates)} templates | mode={mode} | "
        f"{num_per_entry} per entry | replace={replace}",
        file=sys.stderr,
    )

    for metadata in tqdm(
        iter_jsonl(metadata_path), total=total, desc="entries", unit="entry"
    ):
        if not duration_filter.keep(metadata):
            continue
        context = build_context(metadata)
        chosen = select_templates(templates, num_per_entry, mode, rng, replace)
        for template_obj in chosen:
            yield {
                "question": render_question(template_obj, context),
                "answer": render_answer(template_obj, context),
                "metadata": project_metadata(metadata, keep_metadata),
            }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate detailed-speech-summarization QA pairs from "
                    "weighted templates and a metadata manifest.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--template", "--template-jsonl", dest="template", required=True,
                   help="Path to template.jsonl.")
    p.add_argument("--metadata", required=True,
                   help="Path to the metadata .jsonl or .jsonl.gz manifest.")
    p.add_argument("--output", required=True,
                   help="Output path; .gz enables gzip compression.")
    p.add_argument("--num-templates-per-entry", "--samples-per-entry",
                   dest="num_per_entry", type=int, default=1,
                   help="QA pairs to emit per metadata entry (ignored for cartesian).")
    p.add_argument("--mode", choices=("weighted_sample", "random_sample", "cartesian"),
                   default="weighted_sample",
                   help="Template selection strategy.")
    p.add_argument("--max-duration", type=float, default=300.0,
                   help="Drop entries longer than this many seconds. "
                        "Pass 'inf' (or any non-positive value) to disable the cap.")
    p.add_argument("--min-duration", type=float, default=0.0,
                   help="Drop entries shorter than this many seconds.")
    p.add_argument("--replace", action="store_true",
                   help="Sample with replacement. By default repeats of the same "
                        "entry draw distinct templates.")
    p.add_argument("--keep-metadata", choices=("all", "core", "none"), default="all",
                   help="Metadata fields to carry into the output records.")
    p.add_argument("--seed", type=int, default=42, help="Random seed.")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode != "cartesian" and args.num_per_entry <= 0:
        raise SystemExit("--num-templates-per-entry must be >= 1")

    try:
        duration_filter = DurationFilter(
            min_duration=args.min_duration, max_duration=args.max_duration
        )
    except ValueError as e:
        raise SystemExit(str(e))

    rng = random.Random(args.seed)

    try:
        total = count_lines(args.metadata)
    except OSError as e:
        raise SystemExit(f"Cannot read --metadata {args.metadata}: {e}")

    records = generate_records(
        template_path=args.template,
        metadata_path=args.metadata,
        num_per_entry=args.num_per_entry,
        mode=args.mode,
        rng=rng,
        keep_metadata=args.keep_metadata,
        replace=args.replace,
        duration_filter=duration_filter,
        total=total,
    )

    written = write_jsonl(args.output, records)
    if duration_filter.active:
        print(f"[generate_qa] {duration_filter.summary()}", file=sys.stderr)
    print(
        f"[generate_qa] wrote {written} QA pairs from "
        f"{duration_filter.n_kept} entries -> {args.output}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
