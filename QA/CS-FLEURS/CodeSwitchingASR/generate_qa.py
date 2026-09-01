#!/usr/bin/env python3
"""
Generate Code-Switching ASR QA pairs for CS-FLEURS.

Target field: `text` — a code-switched transcript. In the `train` manifest the
embedded-language spans are wrapped in Markdown emphasis (`**span**`); in `test`
they are not. `clean()` strips those markers so both splits share one plain
transcript convention, and it is the default answer expression. A small
low-weight family (templates carrying `"requires": "has_markers"`) instead asks
for the marked form explicitly and only fires on entries that actually have
markers, so `test` entries never receive it.

Language handling is language-PAIR agnostic: `{language_pair}`,
`{language_list}`, `{matrix_language}` and `{embedded_language}` are all derived
by splitting the entry's `language` code on '-' and mapping each part through
LANGUAGE_NAMES. Nothing assumes English is one of the two members.

Output format:
{"question": "...", "answer": "...", "metadata": {...}}

Example:
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/CS-FLEURS/train.jsonl.gz \
  --output qa_train.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 2 \
  --seed 42
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import re
import sys
from typing import Any, Dict, Iterable, Iterator, List, Mapping

try:
    from tqdm import tqdm
except ImportError:  # tqdm is optional
    def tqdm(it, **kwargs):  # type: ignore
        return it


# ISO 639-3 codes seen in the CS-FLEURS `language` field. Extend this map to add
# pairs; no template hardcodes a member language, so new pairs need no template
# changes.
LANGUAGE_NAMES: Dict[str, str] = {
    "ara": "Arabic",
    "ces": "Czech",
    "cmn": "Mandarin Chinese",
    "deu": "German",
    "eng": "English",
    "fra": "French",
    "hin": "Hindi",
    "hun": "Hungarian",
    "ita": "Italian",
    "jpn": "Japanese",
    "kor": "Korean",
    "nld": "Dutch",
    "pol": "Polish",
    "por": "Portuguese",
    "rus": "Russian",
    "spa": "Spanish",
    "tur": "Turkish",
}


# Short forms used when languages are joined into a hyphenated pair name, so
# `cmn-eng` renders as 'Mandarin-English' rather than 'Mandarin Chinese-English'.
PAIR_NAMES: Dict[str, str] = {"cmn": "Mandarin"}


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


def write_jsonl_gz(path: str, records: Iterable[Dict[str, Any]]) -> int:
    """Write records to .jsonl.gz (or .jsonl if not ending with .gz). Returns count."""
    n = 0
    with open_text(path, "wt") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
    return n


def clean(text: str) -> str:
    """Strip the `**` emphasis markers train uses around embedded-language spans.

    Only literal double asterisks are removed, so a lone `*` used as a
    multiplication sign (e.g. '36mm*24mm') survives untouched.
    """
    return re.sub(r"\s+", " ", str(text).replace("**", "")).strip()


def language_names(language: str) -> List[str]:
    """['spa', 'eng'] -> ['Spanish', 'English']; unknown codes pass through."""
    parts = [p for p in str(language).strip().lower().split("-") if p]
    if not parts:
        raise ValueError(f"Empty CS-FLEURS language label: {language!r}")
    return [LANGUAGE_NAMES.get(p, p) for p in parts]


def pair_names(language: str) -> List[str]:
    """['cmn', 'eng'] -> ['Mandarin', 'English'] for hyphenated pair display."""
    parts = [p for p in str(language).strip().lower().split("-") if p]
    if not parts:
        raise ValueError(f"Empty CS-FLEURS language label: {language!r}")
    return [PAIR_NAMES.get(p, LANGUAGE_NAMES.get(p, p)) for p in parts]


def join_names(names: List[str]) -> str:
    """['Spanish', 'English'] -> 'Spanish and English'."""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def format_cascade_labeled(language: str, text: str) -> str:
    """'Language pair: <names>' on line one, 'Transcription: <text>' on line two."""
    return f"Language pair: {'-'.join(pair_names(language))}\nTranscription: {clean(text)}"


def format_cascade_sentence(language: str, text: str) -> str:
    """A sentence naming the pair, then the 'Transcription:' marker."""
    names = language_names(language)
    return (
        f"The speaker code-switches between {join_names(names)}. "
        f"Transcription: {clean(text)}"
    )


def build_context(metadata: Mapping[str, Any]) -> Dict[str, Any]:
    """Question-formatting and answer-evaluation context for one metadata entry."""
    ctx = dict(metadata)
    names = language_names(metadata.get("language", ""))
    ctx["language_pair"] = "-".join(pair_names(metadata.get("language", "")))
    ctx["language_list"] = join_names(names)
    ctx["matrix_language"] = names[0]
    ctx["embedded_language"] = names[-1]
    ctx["has_markers"] = "**" in str(metadata.get("text", ""))
    return ctx


def safe_eval(expr: str, context: Mapping[str, Any]) -> Any:
    """Evaluate a restricted answer expression against the entry context."""
    allowed_globals = {
        "__builtins__": {},
        "clean": clean,
        "format_cascade_labeled": format_cascade_labeled,
        "format_cascade_sentence": format_cascade_sentence,
        "join_names": join_names,
        "language_names": language_names,
        "pair_names": pair_names,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "len": len,
    }
    return eval(expr, allowed_globals, dict(context))  # noqa: S307


class SafeDict(dict):
    """format_map helper that leaves unknown placeholders untouched."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def instantiate_question(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    question = template_obj.get("question_template", template_obj.get("question"))
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"Template missing valid question/question_template: {template_obj}")
    try:
        return question.format_map(SafeDict(context))
    except Exception as e:
        raise ValueError(
            f"Failed to format question: {question}\nContext keys: {sorted(context.keys())}"
        ) from e


def instantiate_answer(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    answer_expr = template_obj.get("answer_template", template_obj.get("answer"))
    if answer_expr is None:
        raise ValueError(f"Template missing answer/answer_template: {template_obj}")
    if not isinstance(answer_expr, str) or not answer_expr.strip():
        raise ValueError(f"Invalid answer expression in template: {template_obj}")

    answer_expr = answer_expr.strip()
    if answer_expr in context:  # fast path: bare field name
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


def load_templates(path: str) -> List[Dict[str, Any]]:
    templates: List[Dict[str, Any]] = []
    for obj in iter_jsonl(path):
        question = obj.get("question_template", obj.get("question"))
        answer = obj.get("answer_template", obj.get("answer"))
        if question is None or answer is None:
            raise ValueError(f"Template missing question/answer fields: {obj}")
        try:
            weight = float(obj.get("weight", 1.0))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid weight in template: {obj}") from e
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"Weight must be > 0 and finite, got {weight} in template: {obj}")
        templates.append(dict(obj))
    if not templates:
        raise ValueError(f"No templates loaded from {path}")
    return templates


def template_applies(template_obj: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
    """Honour an optional `requires` predicate naming a truthy context flag.

    The marker-annotated family sets `"requires": "has_markers"` so it is only
    offered for entries whose stored transcript really carries `**` spans.
    """
    requires = template_obj.get("requires")
    if not requires:
        return True
    return bool(context.get(requires, False))


def keep_entry(metadata: Mapping[str, Any], min_duration: float) -> bool:
    if not str(metadata.get("text", "")).strip():
        return False
    try:
        duration = float(metadata.get("duration", 0.0))
    except (TypeError, ValueError):
        return False
    return duration >= min_duration


def weighted_sample_no_replacement(
    pool: List[Dict[str, Any]],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    """Draw k distinct templates, weighted, so repeats of one entry never collide.

    Falls back to drawing with replacement only once the pool is exhausted
    (k > len(pool)), which the shipped template files never hit.
    """
    remaining = list(pool)
    weights = [float(t.get("weight", 1.0)) for t in remaining]
    chosen: List[Dict[str, Any]] = []
    for _ in range(min(k, len(remaining))):
        i = rng.choices(range(len(remaining)), weights=weights, k=1)[0]
        chosen.append(remaining.pop(i))
        weights.pop(i)
    while len(chosen) < k:  # pool exhausted
        weights_all = [float(t.get("weight", 1.0)) for t in pool]
        chosen.append(rng.choices(pool, weights=weights_all, k=1)[0])
    return chosen


def select_templates(
    templates: List[Dict[str, Any]],
    context: Mapping[str, Any],
    mode: str,
    n: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    pool = [t for t in templates if template_applies(t, context)]
    if not pool:
        return []
    if mode == "cartesian":
        return pool
    if mode == "random_sample":
        return [rng.choice(pool) for _ in range(n)]
    return weighted_sample_no_replacement(pool, n, rng)


def generate_records(
    template_path: str,
    metadata_path: str,
    mode: str,
    num_per_entry: int,
    rng: random.Random,
    keep_metadata: bool,
    min_duration: float,
    stats: Dict[str, int],
) -> Iterator[Dict[str, Any]]:
    templates = load_templates(template_path)

    for metadata in tqdm(iter_jsonl(metadata_path), desc="entries", unit=" entry"):
        stats["read"] += 1
        if not keep_entry(metadata, min_duration):
            stats["filtered"] += 1
            continue
        stats["kept"] += 1

        context = build_context(metadata)
        for template_obj in select_templates(templates, context, mode, num_per_entry, rng):
            yield {
                "question": instantiate_question(template_obj, context),
                "answer": instantiate_answer(template_obj, context),
                "metadata": dict(metadata) if keep_metadata else {},
            }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate CS-FLEURS code-switching ASR QA pairs from templates and metadata."
    )
    p.add_argument("--template", "--template-jsonl", dest="template", required=True,
                   help="Path to template .jsonl file.")
    p.add_argument("--metadata", required=True,
                   help="Path to metadata .jsonl or .jsonl.gz file.")
    p.add_argument("--output", required=True,
                   help="Path to output .jsonl.gz (or .jsonl).")
    p.add_argument("--mode", choices=["weighted_sample", "random_sample", "cartesian"],
                   default="weighted_sample",
                   help="Template selection strategy (default: weighted_sample).")
    p.add_argument("--num-templates-per-entry", "--samples-per-entry", dest="num_per_entry",
                   type=int, default=1,
                   help="QA pairs per kept entry; ignored in cartesian mode (default: 1).")
    p.add_argument("--seed", type=int, default=0, help="Random seed (default: 0).")
    p.add_argument("--min-duration", type=float, default=0.0,
                   help="Drop entries shorter than this many seconds (default: 0.0, no filter).")
    p.add_argument("--no-keep-metadata", action="store_true",
                   help="Emit an empty metadata object instead of the full entry.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.num_per_entry <= 0:
        raise ValueError("--num-templates-per-entry must be >= 1")

    rng = random.Random(args.seed)
    stats = {"read": 0, "kept": 0, "filtered": 0}

    records = generate_records(
        template_path=args.template,
        metadata_path=args.metadata,
        mode=args.mode,
        num_per_entry=args.num_per_entry,
        rng=rng,
        keep_metadata=not args.no_keep_metadata,
        min_duration=args.min_duration,
        stats=stats,
    )
    written = write_jsonl_gz(args.output, records)

    print(
        f"entries read={stats['read']} kept={stats['kept']} filtered={stats['filtered']}; "
        f"QA pairs written={written} -> {args.output}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
