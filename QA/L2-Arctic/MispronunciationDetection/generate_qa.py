#!/usr/bin/env python3
"""
Generate QA pairs for L2-Arctic / Mispronunciation Detection from a template
.jsonl file and a metadata .jsonl/.jsonl.gz file.

Output format (one JSON object per line):
    {"question": ..., "answer": ..., "metadata": {...}}

The L2-Arctic `mispronunciation` field holds a list of annotation strings:

    "{error_type}, [{start}-{end}], {correct_phone}, {perceived_phone}, {word}"
    e.g. "substitution, [0.14-0.37], AE, AA, gad"

Conventions in the source annotations:
  - error_type is one of substitution / deletion / addition
  - a deletion carries perceived_phone == "sil"   (the phone was dropped)
  - an addition carries correct_phone  == "sil"   (a phone was inserted)
  - perceived_phone == "err" marks a production the annotator could not identify
  - phones are ARPABET; the `word` field is lowercased

Only ~12.6% of utterances are annotated. The remainder have an empty list
because they were never annotated -- NOT because they were verified error-free.
Every formatter renders the empty list as NO_ERRORS, and --annotated-upsample
lets annotated utterances contribute more QA pairs than unannotated ones.

Supported answer expressions
----------------------------
    group_by_word(mispronunciation)        "his: IH -> IY; Z -> S"      (default)
    arrow_lines(mispronunciation)          "his: IH -> IY (substitution)"
    arrow_lines_timed(mispronunciation)    "[0.57-0.68] his: IH -> IY (substitution)"
    mispronounced_words(mispronunciation)  "was, his"
    prose_feedback(mispronunciation)       'In "his", IH was pronounced as IY. ...'
    error_counts(mispronunciation)         "3 substitutions, 0 additions, 0 deletions"
    verbatim_lines(mispronunciation)       the stored annotation strings, one per line

Questions may reference any metadata field via placeholders, e.g. "{text}".

Examples
--------
# Train: 4 QA pairs per annotated utterance, 1 per unannotated utterance
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/L2-Arctic/train.jsonl.gz \
  --output train.jsonl.gz \
  --mode weighted_sample \
  --num-templates-per-entry 1 \
  --annotated-upsample 4 \
  --seed 42

# Test: no upsampling, keeps the natural 11.6% annotated rate
python generate_qa.py \
  --template template.jsonl \
  --metadata /home/tseng/FullSpectrumDataset/metadata/L2-Arctic/test.jsonl.gz \
  --output test.jsonl.gz \
  --annotated-upsample 1

# Annotated utterances only
python generate_qa.py ... --skip-unannotated
"""

from __future__ import annotations

import argparse
import ast
import collections
import gzip
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence

from tqdm import tqdm


NO_ERRORS = "No mispronunciations detected."


# --------------------------------------------------------------------------- #
# L2-Arctic annotation parsing and formatters
# --------------------------------------------------------------------------- #

def parse_annotation(annotation: str) -> Dict[str, str]:
    """Split one annotation string into its five fields.

    "substitution, [0.14-0.37], AE, AA, gad"
      -> {"type": "substitution", "interval": "0.14-0.37",
          "canonical": "AE", "perceived": "AA", "word": "gad"}
    """
    parts = [p.strip() for p in str(annotation).split(",")]
    if len(parts) != 5:
        raise ValueError(
            f"Malformed mispronunciation annotation (expected 5 comma-separated "
            f"fields, got {len(parts)}): {annotation!r}"
        )
    return {
        "type": parts[0],
        "interval": parts[1].strip("[]"),
        "canonical": parts[2],
        "perceived": parts[3],
        "word": parts[4],
    }


def _as_list(mispronunciation: Any) -> List[str]:
    if not mispronunciation:
        return []
    if isinstance(mispronunciation, str):
        return [mispronunciation]
    return list(mispronunciation)


def _change_phrase(err: Dict[str, str]) -> str:
    """Human-readable phone change, e.g. 'AE -> AA', 'T deleted', 'HH inserted'."""
    if err["type"] == "deletion":
        return f"{err['canonical']} deleted"
    if err["type"] == "addition":
        return f"{err['perceived']} inserted"
    return f"{err['canonical']} -> {err['perceived']}"


def group_by_word(mispronunciation: Any) -> str:
    """Default format: one line per affected word, errors joined by '; '.

        was: Z -> S
        his: IH -> IY; Z -> S
    """
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    grouped: "collections.OrderedDict[str, List[str]]" = collections.OrderedDict()
    for annotation in errors:
        err = parse_annotation(annotation)
        grouped.setdefault(err["word"], []).append(_change_phrase(err))
    return "\n".join(f"{word}: {'; '.join(changes)}" for word, changes in grouped.items())


def arrow_lines(mispronunciation: Any) -> str:
    """One line per error, typed, without timestamps.

        his: IH -> IY (substitution)
    """
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    out = []
    for annotation in errors:
        err = parse_annotation(annotation)
        out.append(f"{err['word']}: {_change_phrase(err)} ({err['type']})")
    return "\n".join(out)


def arrow_lines_timed(mispronunciation: Any) -> str:
    """One line per error, typed, prefixed with the [start-end] interval.

        [0.57-0.68] his: IH -> IY (substitution)
    """
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    out = []
    for annotation in errors:
        err = parse_annotation(annotation)
        out.append(f"[{err['interval']}] {err['word']}: {_change_phrase(err)} ({err['type']})")
    return "\n".join(out)


def mispronounced_words(mispronunciation: Any) -> str:
    """Comma-separated affected words, de-duplicated, in spoken order."""
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    seen: List[str] = []
    for annotation in errors:
        word = parse_annotation(annotation)["word"]
        if word not in seen:
            seen.append(word)
    return ", ".join(seen)


def prose_feedback(mispronunciation: Any) -> str:
    """One sentence per error.

        In "his", IH was pronounced as IY.
    """
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    out = []
    for annotation in errors:
        err = parse_annotation(annotation)
        word = err["word"]
        if err["type"] == "deletion":
            out.append(f'In "{word}", {err["canonical"]} was dropped.')
        elif err["type"] == "addition":
            out.append(f'In "{word}", an extra {err["perceived"]} was inserted.')
        else:
            out.append(f'In "{word}", {err["canonical"]} was pronounced as {err["perceived"]}.')
    return " ".join(out)


def error_counts(mispronunciation: Any) -> str:
    """Tally by error type: '3 substitutions, 1 addition, 1 deletion'."""
    errors = _as_list(mispronunciation)
    counts = collections.Counter(parse_annotation(a)["type"] for a in errors)

    def plural(n: int, noun: str) -> str:
        return f"{n} {noun}" + ("" if n == 1 else "s")

    return ", ".join([
        plural(counts.get("substitution", 0), "substitution"),
        plural(counts.get("addition", 0), "addition"),
        plural(counts.get("deletion", 0), "deletion"),
    ])


def verbatim_lines(mispronunciation: Any) -> str:
    """The stored annotation strings, one per line."""
    errors = _as_list(mispronunciation)
    if not errors:
        return NO_ERRORS
    return "\n".join(str(a) for a in errors)


L2ARCTIC_HELPERS = {
    "group_by_word": group_by_word,
    "arrow_lines": arrow_lines,
    "arrow_lines_timed": arrow_lines_timed,
    "mispronounced_words": mispronounced_words,
    "prose_feedback": prose_feedback,
    "error_counts": error_counts,
    "verbatim_lines": verbatim_lines,
    "parse_annotation": parse_annotation,
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
    "lower", "upper", "title", "strip", "lstrip", "rstrip", "replace",
    "capitalize", "casefold", "split", "rsplit", "join", "startswith",
    "endswith", "removeprefix", "removesuffix", "count",
}

SAFE_LIST_METHODS = {"count", "index"}
SAFE_DICT_METHODS = {"get", "keys", "values", "items"}

ALLOWED_AST_NODES = (
    ast.Expression, ast.Name, ast.Load, ast.Constant, ast.List, ast.Tuple,
    ast.Dict, ast.Set, ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.BinOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.NotEq, ast.Lt,
    ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.IfExp, ast.Call,
    ast.Attribute, ast.Subscript, ast.Slice,
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
            if node.id in L2ARCTIC_HELPERS:
                return L2ARCTIC_HELPERS[node.id]
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
            return {self._eval_node(k): self._eval_node(v)
                    for k, v in zip(node.keys, node.values)}

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
            return value[self._eval_node(node.slice)]

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
    evaluator = SafeEvaluator(metadata)
    try:
        return evaluator.eval(answer_expr)
    except Exception as e:
        raise ValueError(
            f"Failed to evaluate answer expression: {answer_expr!r}\n"
            f"Entry id: {metadata.get('id')!r}\n"
            f"Available metadata keys: {sorted(metadata.keys())}\n"
            f"Available helpers: {sorted(L2ARCTIC_HELPERS)}"
        ) from e


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
        scored.append((math.log(u) / w, tpl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [tpl for _, tpl in scored[:k]]


def select_templates(
    templates: Sequence[Dict[str, Any]],
    mode: str,
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if mode == "cartesian":
        return list(templates)
    if mode == "random_sample":
        return rng.sample(list(templates), min(k, len(templates)))
    if mode == "weighted_sample":
        return weighted_sample_without_replacement(templates, k, rng)
    raise ValueError(f"Unknown mode: {mode}")


def is_annotated(metadata: Dict[str, Any]) -> bool:
    return bool(metadata.get("mispronunciation"))


def generate(
    template_path: str,
    metadata_path: str,
    output_path: str,
    mode: str,
    num_templates_per_entry: int,
    annotated_upsample: int,
    skip_unannotated: bool,
    seed: int,
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
    num_annotated = 0
    num_skipped = 0
    written_annotated = 0

    # Ensure output path ends with .jsonl.gz
    if not output_path.endswith(".jsonl.gz"):
        output_path = str(Path(output_path).with_suffix("")) + ".jsonl.gz"

    with gzip.open(output_path, "wt", encoding="utf-8") as out_f:
        for metadata in tqdm(iter_jsonl(metadata_path), desc="Processing metadata"):
            num_metadata += 1
            annotated = is_annotated(metadata)

            if annotated:
                num_annotated += 1
                k = num_templates_per_entry * annotated_upsample
            else:
                if skip_unannotated:
                    num_skipped += 1
                    continue
                k = num_templates_per_entry

            for tpl in select_templates(templates, mode, k, rng):
                record = {
                    "question": render_question(str(tpl["question"]), metadata),
                    "answer": render_answer(tpl["answer"], metadata),
                    "metadata": metadata,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_written += 1
                if annotated:
                    written_annotated += 1

    positive_rate = (100.0 * written_annotated / num_written) if num_written else 0.0
    print(f"Loaded templates: {len(templates)}")
    print(f"Processed metadata entries: {num_metadata} "
          f"({num_annotated} annotated, {num_metadata - num_annotated} unannotated)")
    if skip_unannotated:
        print(f"Skipped unannotated entries: {num_skipped}")
    print(f"Wrote QA pairs: {num_written} "
          f"({written_annotated} from annotated entries, {positive_rate:.1f}%)")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate L2-Arctic mispronunciation-detection QA JSONL "
                    "from template JSONL and metadata JSONL(.gz)."
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
        help="Templates sampled per metadata entry (before upsampling).",
    )
    parser.add_argument(
        "--annotated-upsample",
        type=int,
        default=4,
        help=(
            "Multiplier applied to --num-templates-per-entry for utterances that "
            "carry mispronunciation annotations. Only ~12.6%% of L2-Arctic is "
            "annotated, so upsampling raises the share of QA pairs with real "
            "errors. Use 1 to disable (recommended for the test split)."
        ),
    )
    parser.add_argument(
        "--skip-unannotated",
        action="store_true",
        help=(
            "Drop utterances with an empty mispronunciation list instead of "
            "answering 'No mispronunciations detected.' Those utterances were "
            "never annotated, so the negative label is unverified."
        ),
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.num_templates_per_entry <= 0:
        raise SystemExit("--num-templates-per-entry must be >= 1")
    if args.annotated_upsample <= 0:
        raise SystemExit("--annotated-upsample must be >= 1")
    generate(
        template_path=args.template,
        metadata_path=args.metadata,
        output_path=args.output,
        mode=args.mode,
        num_templates_per_entry=args.num_templates_per_entry,
        annotated_upsample=args.annotated_upsample,
        skip_unannotated=args.skip_unannotated,
        seed=args.seed,
    )
