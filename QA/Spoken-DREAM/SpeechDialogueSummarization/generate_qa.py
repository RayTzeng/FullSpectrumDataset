#!/usr/bin/env python3
"""
Generate QA pairs for Spoken-DREAM / SpeechDialogueSummarization.

Task: spoken dialogue summarization. The answer is grounded in the `summary`
field of the metadata manifest; a subset of templates additionally serialize the
auxiliary `topic` field alongside it (cascade / JSON variants).

Template schema (template.jsonl), one JSON object per line:
    {"template_id": "...", "category": "...",
     "question_template": "...", "answer_template": "...", "weight": 0.85}

Legacy {"question": ..., "answer": ...} keys are also accepted.

Output format (.jsonl.gz), one JSON object per line:
    {"question": "...", "answer": "...", "metadata": {...}}

Examples
--------
    python generate_qa.py \
        --template template.jsonl \
        --metadata /path/to/train.jsonl.gz \
        --output train.jsonl.gz \
        --num-templates-per-entry 30 \
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


# ------------------------------------------------------------ field formatting

def norm_ws(text: Any) -> str:
    """Collapse all whitespace runs to single spaces and strip the ends."""
    return re.sub(r"\s+", " ", str(text)).strip()


def topic_display(topic: Any) -> str:
    """
    Presentation form of the auxiliary `topic` field.

    12/1667 topics carry leading whitespace or a stray newline, so whitespace is
    normalized. Casing is deliberately left alone: the topic vocabulary contains
    genuine proper nouns ("Abraham Lincoln", "Singapore", "Belgian food") that
    lower-casing would corrupt, and no reliable rule separates them from the
    incidentally title-cased entries.
    """
    return norm_ws(topic)


def _topic_bare(topic: Any) -> str:
    """Topic with any trailing terminal punctuation removed.

    Used where the topic is embedded mid-prose and the template supplies its own
    sentence-final period (2/1667 topics end in '.', '!' or '?').
    """
    return re.sub(r"[.!?]+$", "", topic_display(topic)).strip()


def duration_adj(duration: Any) -> str:
    """Attributive duration phrase: "35-second", "1.5-minute", "4-minute".

    Under 90s rounds to the nearest 5 seconds; at or above 90s rounds to the
    nearest half minute. Templates using this always pair it with "this"/"the",
    never an indefinite article, so no a/an agreement problem can arise.
    """
    d = float(duration)
    if d < 90.0:
        secs = max(5, int(round(d / 5.0) * 5))
        return f"{secs}-second"
    mins = round(d / 30.0) / 2.0
    return f"{mins:g}-minute"


def duration_len(duration: Any) -> str:
    """Predicative duration phrase: "35 seconds", "1.5 minutes", "4 minutes"."""
    d = float(duration)
    if d < 90.0:
        secs = max(5, int(round(d / 5.0) * 5))
        return f"{secs} seconds"
    mins = round(d / 30.0) / 2.0
    return f"{mins:g} minutes"


# ------------------------------------------------------------ answer formatters

def format_topic_summary(topic: Any, summary: Any) -> str:
    """"Topic: X" / "Summary: Y" on two lines."""
    return f"Topic: {topic_display(topic)}\nSummary: {summary}"


def format_topic_summary_inline(topic: Any, summary: Any) -> str:
    """"Topic: X. Summary: Y" on one line."""
    return f"Topic: {_topic_bare(topic)}. Summary: {summary}"


def format_summary_topic(summary: Any, topic: Any) -> str:
    """"Summary: Y" / "Topic: X" on two lines (reverse order)."""
    return f"Summary: {summary}\nTopic: {topic_display(topic)}"


def format_natural_cascade(topic: Any, summary: Any) -> str:
    """Natural prose, topic first: "It is a conversation regarding X. Y"."""
    return f"It is a conversation regarding {_topic_bare(topic)}. {summary}"


def format_natural_cascade_topic_last(summary: Any, topic: Any) -> str:
    """Natural prose, topic last: "Y The conversation is about X."."""
    return f"{summary} The conversation is about {_topic_bare(topic)}."


def json_summary(summary: Any) -> str:
    """JSON object with a single "summary" key."""
    return json.dumps({"summary": str(summary)}, ensure_ascii=False)


def json_topic_summary(topic: Any, summary: Any) -> str:
    """JSON object with "topic" and "summary" keys."""
    return json.dumps(
        {"topic": topic_display(topic), "summary": str(summary)}, ensure_ascii=False
    )


# --------------------------------------------------------------- safe eval

_EVAL_GLOBALS = {
    "__builtins__": {},
    # field formatters
    "norm_ws": norm_ws,
    "topic_display": topic_display,
    "duration_adj": duration_adj,
    "duration_len": duration_len,
    # answer formatters
    "format_topic_summary": format_topic_summary,
    "format_topic_summary_inline": format_topic_summary_inline,
    "format_summary_topic": format_summary_topic,
    "format_natural_cascade": format_natural_cascade,
    "format_natural_cascade_topic_last": format_natural_cascade_topic_last,
    "json_summary": json_summary,
    "json_topic_summary": json_topic_summary,
    # a few safe builtins
    "str": str, "int": int, "float": float, "bool": bool, "len": len,
}

_ALLOWED_NODES = (
    ast.Expression, ast.Call, ast.Name, ast.Load, ast.Attribute, ast.Constant,
    ast.BinOp, ast.Add, ast.Mod, ast.Str, ast.JoinedStr, ast.FormattedValue,
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
    if "topic" in metadata:
        ctx["topic_display"] = topic_display(metadata["topic"])
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
        description="Generate spoken-dialogue-summarization QA pairs from "
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
        total=total,
    )

    written = write_jsonl(args.output, records)
    print(
        f"[generate_qa] wrote {written} QA pairs from {total} entries -> {args.output}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
