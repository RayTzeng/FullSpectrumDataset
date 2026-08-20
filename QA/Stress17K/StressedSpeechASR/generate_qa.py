#!/usr/bin/env python3
"""
Generate QA pairs for Stress17K / Stressed Speech ASR from a template .jsonl
file and a metadata .jsonl/.jsonl.gz file.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

The Stress17K `text` field stores the transcription with the prosodically
stressed span wrapped in Markdown-style double asterisks, e.g.

    "**the play** inspired the audience to act."
    "is the theater supposed to challenge the **audience**?"

Unlike TinyStress, every well-formed Stress17K utterance carries exactly *one*
stressed span, and that span is often several words long ("**the play**",
"**your mental well-being**"). Hyphens inside a span are part of the word
("**thought-provoking**") and are preserved; only leading/trailing punctuation
is trimmed when the span is reported on its own.

Supported answer expressions
----------------------------
    text                              transcript with the original ** markers
    stressed_span(text)               "the play"      (outer punctuation stripped)
    stressed_span_quoted(text)        "\"the play\""
    stressed_span_bracketed(text)     "[the play]"
    mark_upper(text)                  stressed span in ALL CAPS
    mark_brackets(text)               stressed span in [square brackets]
    mark_em(text)                     stressed span in <em>...</em>
    mark_single_star(text)            stressed span in *single asterisks*
    plain_transcript(text)            markers removed
    cascade_plain_then_span(text)     "Transcription: ...\nStressed: ..."
    cascade_marked_then_span(text)    same, but the transcript keeps ** markers

plus the generic deterministic expressions supported by the safe evaluator
(`text.lower()`, `text.upper()`, `' '.join(text.split())`, ...).

Notes
-----
- `question` is treated as a plain string. If it contains Python-style format
  placeholders like "{text}" or "{id}", they will be filled from metadata.
- `answer` is evaluated with a restricted expression evaluator rather than raw eval.
- If `weight` exists in the template file, it is used for weighted sampling.
- A small number of upstream `train` entries carry a malformed annotation
  (`"<e{our} company's> impact ..."`) instead of a `**...**` span. Those entries
  have no recoverable stress marking, so by default they are skipped and counted;
  pass --keep-unmarked to emit them anyway.

Examples
--------
# 1) Sample one template per metadata entry using template weights
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/Stress17K/StressedSpeechASR/train.jsonl.gz \
  --output train.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --seed 42

# 2) Generate the full Cartesian product (every template x every metadata entry)
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/Stress17K/StressedSpeechASR/test.jsonl.gz \
  --output test.jsonl.gz \
  --mode cartesian
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import math
import random
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence

from tqdm import tqdm


# --------------------------------------------------------------------------- #
# Stress17K-specific formatters
# --------------------------------------------------------------------------- #

STRESS_RE = re.compile(r"\*\*(.+?)\*\*")

# Fields copied into the emitted `metadata` block. The upstream manifest also
# carries `description`, `possible_answers` and `label`, which are the answer key
# for the sibling StressedSpeechUnderstanding task; they are dropped here so the
# two QA sets stay disjoint. Pass --metadata-fields all to keep everything.
DEFAULT_METADATA_FIELDS = ("id", "path", "sampling_rate", "duration", "dataset", "text")


def _stressed_tokens(text: str) -> List[str]:
    """Raw spans inside ** ** markers, in spoken order (punctuation included)."""
    return STRESS_RE.findall(str(text))


def _strip_punct(token: str) -> str:
    """Drop leading/trailing punctuation.

    Apostrophes and hyphens are kept when they sit inside the span, so
    "thought-provoking" and "Lily's" survive intact.
    """
    return re.sub(r"^[^\w']+|[^\w']+$", "", token, flags=re.UNICODE)


def has_stress_span(text: Any) -> bool:
    """True when the transcript carries at least one well-formed ** span."""
    return bool(_stressed_tokens(text))


def plain_transcript(text: str) -> str:
    """Transcript with the ** markers removed."""
    return STRESS_RE.sub(lambda m: m.group(1), str(text))


def stressed_span(text: str) -> str:
    """The emphasized span, outer punctuation stripped.

    Stress17K utterances carry a single span; if several were ever present they
    are joined with ", " in spoken order.
    """
    spans = [s for s in (_strip_punct(t) for t in _stressed_tokens(text)) if s]
    return ", ".join(spans)


def stressed_span_quoted(text: str) -> str:
    """The emphasized span in double quotes: "the play"."""
    return '"' + stressed_span(text) + '"'


def stressed_span_bracketed(text: str) -> str:
    """The emphasized span in square brackets: [the play]."""
    return "[" + stressed_span(text) + "]"


def mark_upper(text: str) -> str:
    """Stressed span in ALL CAPS instead of ** markers."""
    return STRESS_RE.sub(lambda m: m.group(1).upper(), str(text))


def mark_brackets(text: str) -> str:
    """Stressed span in [square brackets] instead of ** markers."""
    return STRESS_RE.sub(lambda m: "[" + m.group(1) + "]", str(text))


def mark_em(text: str) -> str:
    """Stressed span in <em>...</em> instead of ** markers."""
    return STRESS_RE.sub(lambda m: "<em>" + m.group(1) + "</em>", str(text))


def mark_single_star(text: str) -> str:
    """Stressed span in *single asterisks* instead of ** markers."""
    return STRESS_RE.sub(lambda m: "*" + m.group(1) + "*", str(text))


def cascade_plain_then_span(text: str) -> str:
    """Unmarked transcript, then the stressed span on a second line."""
    return (
        "Transcription: "
        + plain_transcript(text)
        + "\nStressed: "
        + stressed_span(text)
    )


def cascade_marked_then_span(text: str) -> str:
    """Stress-marked transcript, then the stressed span on a second line."""
    return (
        "Transcription: "
        + str(text)
        + "\nStressed: "
        + stressed_span(text)
    )


STRESS17K_HELPERS = {
    "plain_transcript": plain_transcript,
    "stressed_span": stressed_span,
    "stressed_span_quoted": stressed_span_quoted,
    "stressed_span_bracketed": stressed_span_bracketed,
    "mark_upper": mark_upper,
    "mark_brackets": mark_brackets,
    "mark_em": mark_em,
    "mark_single_star": mark_single_star,
    "cascade_plain_then_span": cascade_plain_then_span,
    "cascade_marked_then_span": cascade_marked_then_span,
}


# --------------------------------------------------------------------------- #
# Safe expression evaluation
# --------------------------------------------------------------------------- #

class SafeDict(dict):
    """Return the original placeholder when a key is missing."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


SAFE_BUILTINS = {
    "len": len,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "round": round,
    "min": min,
    "max": max,
    "abs": abs,
    "sum": sum,
    "sorted": sorted,
}

SAFE_STR_METHODS = {
    "lower",
    "upper",
    "title",
    "strip",
    "lstrip",
    "rstrip",
    "replace",
    "capitalize",
    "casefold",
    "split",
    "rsplit",
    "join",
    "startswith",
    "endswith",
    "removeprefix",
    "removesuffix",
    "count",
}

SAFE_LIST_METHODS = {"count", "index"}
SAFE_DICT_METHODS = {"get", "keys", "values", "items"}

ALLOWED_AST_NODES = (
    ast.Expression,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Set,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.IfExp,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Slice,
)


class SafeEvaluator:
    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def eval(self, expr: str) -> Any:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_AST_NODES):
                raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            if node.id in STRESS17K_HELPERS:
                return STRESS17K_HELPERS[node.id]
            if node.id in SAFE_BUILTINS:
                return SAFE_BUILTINS[node.id]
            raise KeyError(f"Unknown name in expression: {node.id}")

        if isinstance(node, ast.List):
            return [self._eval_node(elt) for elt in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt) for elt in node.elts)

        if isinstance(node, ast.Set):
            return {self._eval_node(elt) for elt in node.elts}

        if isinstance(node, ast.Dict):
            return {
                self._eval_node(k): self._eval_node(v)
                for k, v in zip(node.keys, node.values)
            }

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.Not):
                return not operand
            raise ValueError("Unsupported unary operator")

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise ValueError("Unsupported binary operator")

        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(v) for v in node.values]
            if isinstance(node.op, ast.And):
                result = True
                for v in values:
                    result = result and v
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for v in values:
                    result = result or v
                return result
            raise ValueError("Unsupported boolean operator")

        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator)
                if isinstance(op, ast.Eq):
                    ok = left == right
                elif isinstance(op, ast.NotEq):
                    ok = left != right
                elif isinstance(op, ast.Lt):
                    ok = left < right
                elif isinstance(op, ast.LtE):
                    ok = left <= right
                elif isinstance(op, ast.Gt):
                    ok = left > right
                elif isinstance(op, ast.GtE):
                    ok = left >= right
                elif isinstance(op, ast.In):
                    ok = left in right
                elif isinstance(op, ast.NotIn):
                    ok = left not in right
                else:
                    raise ValueError("Unsupported comparison operator")
                if not ok:
                    return False
                left = right
            return True

        if isinstance(node, ast.IfExp):
            return self._eval_node(node.body) if self._eval_node(node.test) else self._eval_node(node.orelse)

        if isinstance(node, ast.Subscript):
            value = self._eval_node(node.value)
            if isinstance(node.slice, ast.Slice):
                lower = self._eval_node(node.slice.lower) if node.slice.lower is not None else None
                upper = self._eval_node(node.slice.upper) if node.slice.upper is not None else None
                step = self._eval_node(node.slice.step) if node.slice.step is not None else None
                return value[slice(lower, upper, step)]
            index = self._eval_node(node.slice)
            return value[index]

        if isinstance(node, ast.Attribute):
            value = self._eval_node(node.value)
            attr = node.attr
            if isinstance(value, str) and attr in SAFE_STR_METHODS:
                return getattr(value, attr)
            if isinstance(value, list) and attr in SAFE_LIST_METHODS:
                return getattr(value, attr)
            if isinstance(value, dict) and attr in SAFE_DICT_METHODS:
                return getattr(value, attr)
            raise ValueError(f"Attribute access not allowed: {type(value).__name__}.{attr}")

        if isinstance(node, ast.Call):
            func = self._eval_node(node.func)
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)

        raise ValueError(f"Unsupported AST node: {type(node).__name__}")


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #

def open_text_auto(path: str):
    path_obj = Path(path)
    if path_obj.suffix == ".gz":
        return gzip.open(path_obj, "rt", encoding="utf-8")
    return open(path_obj, "r", encoding="utf-8")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    with open_text_auto(path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {e}") from e
    return items


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    with open_text_auto(path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {e}") from e


# --------------------------------------------------------------------------- #
# Rendering / sampling
# --------------------------------------------------------------------------- #

def render_question(question_template: str, metadata: Dict[str, Any]) -> str:
    return question_template.format_map(SafeDict(metadata))


def render_answer(answer_expr: Any, metadata: Dict[str, Any]) -> Any:
    if not isinstance(answer_expr, str):
        return answer_expr
    # Fast path: a bare metadata field name.
    if answer_expr in metadata:
        value = metadata[answer_expr]
        return "" if value is None else value
    evaluator = SafeEvaluator(metadata)
    try:
        return evaluator.eval(answer_expr)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression: {answer_expr!r}\n"
            f"Available metadata keys: {sorted(metadata.keys())}\n"
            f"Available helpers: {sorted(STRESS17K_HELPERS)}"
        ) from e


def project_metadata(
    metadata: Dict[str, Any],
    fields: Sequence[str] | None,
) -> Dict[str, Any]:
    """Restrict the emitted metadata block to `fields` (None keeps everything)."""
    if fields is None:
        return metadata
    return {k: metadata[k] for k in fields if k in metadata}


def positive_weight(template: Dict[str, Any]) -> float:
    try:
        w = float(template.get("weight", 1.0))
    except (TypeError, ValueError):
        w = 1.0
    return max(w, 0.0)


def weighted_sample_without_replacement(
    templates: Sequence[Dict[str, Any]],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    candidates = [(tpl, positive_weight(tpl)) for tpl in templates]
    candidates = [(tpl, w) for tpl, w in candidates if w > 0]
    if k <= 0 or not candidates:
        return []
    if k >= len(candidates):
        return [tpl for tpl, _ in candidates]

    # Efraimidis-Spirakis weighted sampling without replacement.
    scored: List[tuple] = []
    for tpl, w in candidates:
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        key = math.log(u) / w  # larger (closer to 0) is better
        scored.append((key, tpl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [tpl for _, tpl in scored[:k]]


def select_templates(
    templates: Sequence[Dict[str, Any]],
    mode: str,
    num_templates_per_entry: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        k = min(num_templates_per_entry, len(templates))
        return rng.sample(list(templates), k)
    if mode == "weighted_sample":
        return weighted_sample_without_replacement(templates, num_templates_per_entry, rng)
    raise ValueError(f"Unknown mode: {mode}")


def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    mode: str,
    num_templates_per_entry: int,
    seed: int,
    keep_unmarked: bool = False,
    metadata_fields: Sequence[str] | None = DEFAULT_METADATA_FIELDS,
) -> None:
    templates = load_jsonl(template_path)
    if not templates:
        raise ValueError("No templates found.")

    required_keys = {"question", "answer"}
    for i, tpl in enumerate(templates):
        missing = required_keys - tpl.keys()
        if missing:
            raise ValueError(f"Template #{i} is missing required keys: {sorted(missing)}")

    rng = random.Random(seed)
    num_written = 0
    num_metadata = 0
    num_skipped = 0

    # Ensure output path ends with .jsonl.gz
    output_path_obj = Path(output_path)
    if not output_path.endswith(".jsonl.gz"):
        output_path = str(output_path_obj.with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1

            # Entries without a well-formed ** span carry no usable stress
            # annotation; emitting them would teach the malformed markup.
            if not keep_unmarked and not has_stress_span(metadata.get("text", "")):
                num_skipped += 1
                continue

            chosen_templates = select_templates(
                templates=templates,
                mode=mode,
                num_templates_per_entry=num_templates_per_entry,
                rng=rng,
            )
            emitted_metadata = project_metadata(metadata, metadata_fields)
            for tpl in chosen_templates:
                question = render_question(str(tpl["question"]), metadata)
                answer = render_answer(tpl["answer"], metadata)
                record = {
                    "question": question,
                    "answer": answer,
                    "metadata": emitted_metadata,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1

    print(f"Loaded templates: {len(templates)}")
    print(f"Processed metadata entries: {num_metadata}")
    if num_skipped:
        print(f"Skipped entries without a ** stress span: {num_skipped}")
    print(f"Wrote QA pairs: {num_written}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Stress17K Stressed-Speech-ASR QA JSONL from template JSONL and metadata JSONL(.gz)."
    )
    parser.add_argument("--template", required=True, help="Path to template .jsonl")
    parser.add_argument("--metadata", required=True, help="Path to metadata .jsonl or .jsonl.gz")
    parser.add_argument("--output", required=True, help="Path to output .jsonl.gz")
    parser.add_argument(
        "--mode",
        default="weighted_sample",
        choices=["cartesian", "random_sample", "weighted_sample"],
        help=(
            "Generation mode: cartesian = every template x every metadata entry; "
            "random_sample = uniform random templates per metadata entry; "
            "weighted_sample = sample using template 'weight'."
        ),
    )
    parser.add_argument(
        "--num-templates-per-entry",
        type=int,
        default=1,
        help="How many templates to sample per metadata entry in random_sample / weighted_sample mode.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--keep-unmarked",
        action="store_true",
        help=(
            "Keep metadata entries whose 'text' has no **stress** span. "
            "Off by default: such entries are malformed upstream and would yield "
            "answers with no stress annotation."
        ),
    )
    parser.add_argument(
        "--metadata-fields",
        default=",".join(DEFAULT_METADATA_FIELDS),
        help=(
            "Comma-separated metadata fields to copy into each output record, or "
            "'all' to pass the source record through unchanged. Default drops "
            "description/possible_answers/label, which belong to the sibling "
            "StressedSpeechUnderstanding task."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.metadata_fields.strip().lower() == "all":
        fields = None
    else:
        fields = [f.strip() for f in args.metadata_fields.split(",") if f.strip()]
    generate(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        mode=args.mode,
        num_templates_per_entry=args.num_templates_per_entry,
        seed=args.seed,
        keep_unmarked=args.keep_unmarked,
        metadata_fields=fields,
    )
