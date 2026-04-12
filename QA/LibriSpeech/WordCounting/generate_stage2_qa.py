#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List

try:
    from num2words import num2words
except ImportError:
    num2words = None


EXPR_RE = re.compile(r"\{([^{}]+)\}")
ESCAPED_LBRACE = "__ESCAPED_LBRACE__"
ESCAPED_RBRACE = "__ESCAPED_RBRACE__"


def open_text(path: str | Path, mode: str = "rt"):
    path = str(path)
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str | Path) -> Iterator[Dict[str, Any]]:
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}") from exc


def write_jsonl(path: str | Path, rows: Iterable[Dict[str, Any]]) -> None:
    with open_text(path, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def round_half_up(value: float | int | str, ndigits: int = 0) -> int | float:
    q = Decimal("1") if ndigits == 0 else Decimal("1." + ("0" * ndigits))
    out = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    if ndigits == 0:
        return int(out)
    return float(out)


def format_fixed(value: float | int | str, ndigits: int) -> str:
    q = Decimal("1") if ndigits == 0 else Decimal("1." + ("0" * ndigits))
    out = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    return f"{out:.{ndigits}f}"


def digitwise_num2words(value: float | int | str) -> str:
    mapping = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        ".": "point",
        "-": "minus",
    }
    s = str(value)
    return " ".join(mapping[ch] for ch in s)


def _require_num2words() -> None:
    if num2words is None:
        raise ImportError(
            "This template requires num2words, but the package is not installed. "
            "Install it with: pip install num2words"
        )


def num2words_value(value: float | int | str) -> str:
    _require_num2words()
    s = str(value)

    if "." not in s:
        return num2words(int(s))

    left, right = s.split(".", 1)
    right = right.rstrip("0")
    if not right:
        return num2words(int(left))

    return f"{num2words(int(left))} point " + " ".join(num2words(int(ch)) for ch in right)


def get_template_weight(template_obj: Dict[str, Any], index: int) -> float:
    if "weight" not in template_obj:
        raise ValueError(f"Template row {index} is missing required key 'weight'.")
    weight = float(template_obj["weight"])
    if not (0.0 < weight <= 1.0):
        raise ValueError(
            f"Template row {index} has invalid weight {weight}. Expected a value in (0, 1]."
        )
    return weight


def sample_from_spec(spec: Dict[str, Any], rng: random.Random) -> Any:
    if "type" not in spec:
        raise ValueError(f"Sampling spec is missing 'type': {spec}")

    spec_type = spec["type"]

    if spec_type == "choice":
        values = spec.get("values", [])
        if not values:
            raise ValueError(f"Choice spec has empty values: {spec}")
        return rng.choice(values)

    if spec_type == "randint":
        return rng.randint(int(spec["min"]), int(spec["max"]))

    if spec_type == "uniform":
        value = rng.uniform(float(spec["min"]), float(spec["max"]))
        if "round" in spec:
            value = round_half_up(value, int(spec["round"]))
        return value

    raise ValueError(f"Unsupported sampling type: {spec_type}")


def sample_template_config(template_obj: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    cfg = template_obj.get("sampling_config", {})
    if not cfg:
        return {}

    sampled: Dict[str, Any] = {}
    for var_name, spec in cfg.items():
        sampled_value = sample_from_spec(spec, rng)

        if spec.get("unpack", False):
            if not isinstance(sampled_value, dict):
                raise ValueError(
                    f"sampling_config[{var_name!r}] has unpack=true but sampled value is not a dict: "
                    f"{sampled_value}"
                )
            sampled.update(sampled_value)
        else:
            sampled[var_name] = sampled_value

    return sampled


def build_context(
    metadata_row: Dict[str, Any],
    sampled_config: Dict[str, Any],
    target_field: str,
) -> Dict[str, Any]:
    if target_field not in metadata_row:
        raise ValueError(
            f"Target field {target_field!r} is not present in metadata row. "
            f"Available keys: {sorted(metadata_row.keys())}"
        )

    target_value = metadata_row[target_field]

    ctx = dict(metadata_row)
    ctx.update(sampled_config)

    ctx["target_field"] = target_field
    ctx["value"] = target_value

    # Convenience aliases.
    ctx[f"{target_field}_rounded"] = round_half_up(target_value, 0)
    ctx[f"{target_field}_1dp"] = format_fixed(target_value, 1)
    ctx[f"{target_field}_2dp"] = format_fixed(target_value, 2)

    ctx["value_rounded"] = round_half_up(target_value, 0)
    ctx["value_1dp"] = format_fixed(target_value, 1)
    ctx["value_2dp"] = format_fixed(target_value, 2)

    return ctx


def render_template(template: str, context: Dict[str, Any]) -> str:
    protected = template.replace("{{", ESCAPED_LBRACE).replace("}}", ESCAPED_RBRACE)

    base_globals = {
        "__builtins__": {},
        "math": math,
        "abs": abs,
        "min": min,
        "max": max,
        "round": round,
        "int": int,
        "float": float,
        "str": str,
        "len": len,
        "range": range,
        "all": all,
        "any": any,
        "Decimal": Decimal,
        "round_half_up": round_half_up,
        "format_fixed": format_fixed,
        "num2words": num2words,
        "num2words_value": num2words_value,
        "digitwise_num2words": digitwise_num2words,
    }

    def replacer(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        if expr == "...":
            return "{...}"

        # Important: merge context into globals so generator expressions and
        # comprehensions can see variables like word_count.
        eval_globals = dict(base_globals)
        eval_globals.update(context)

        try:
            value = eval(expr, eval_globals, {})
        except Exception as exc:
            raise ValueError(
                f"Failed to evaluate template expression {{{expr}}}. "
                f"Context keys: {sorted(context.keys())}"
            ) from exc
        return str(value)

    rendered = EXPR_RE.sub(replacer, protected)
    rendered = rendered.replace(ESCAPED_LBRACE, "{").replace(ESCAPED_RBRACE, "}")
    return rendered


def weighted_sample_without_replacement(
    weights: List[float],
    k: int,
    rng: random.Random,
) -> List[int]:
    """
    Efraimidis-Spirakis weighted sampling without replacement.
    Higher weights lead to higher inclusion probability.
    """
    if k <= 0:
        return []
    if k > len(weights):
        raise ValueError("k cannot be larger than the number of weights")

    keys = []
    for i, w in enumerate(weights):
        u = rng.random()
        while u == 0.0:
            u = rng.random()
        key = math.log(u) / w
        keys.append((key, i))

    keys.sort(reverse=True)
    return [i for _, i in keys[:k]]


def choose_template_indices(
    templates: List[Dict[str, Any]],
    samples_per_entry: int,
    rng: random.Random,
) -> List[int]:
    num_templates = len(templates)
    weights = [get_template_weight(tpl, i) for i, tpl in enumerate(templates)]

    if samples_per_entry <= num_templates:
        return weighted_sample_without_replacement(weights, samples_per_entry, rng)

    indices = weighted_sample_without_replacement(weights, num_templates, rng)
    extra = rng.choices(
        population=list(range(num_templates)),
        weights=weights,
        k=samples_per_entry - num_templates,
    )
    return indices + extra


def generate(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    target_field: str,
    keep_metadata: bool = True,
) -> None:
    if samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be a positive integer")

    rng = random.Random(seed)

    templates = list(iter_jsonl(template_jsonl))
    metadata_rows = list(iter_jsonl(metadata_path))

    if not templates:
        raise ValueError("No templates found in --template-jsonl")
    if not metadata_rows:
        raise ValueError("No metadata entries found in --metadata")

    required_keys = {"question_template", "answer_template", "weight"}
    for i, tpl in enumerate(templates):
        missing = required_keys - set(tpl.keys())
        if missing:
            raise ValueError(f"Template row {i} is missing required keys: {missing}")
        _ = get_template_weight(tpl, i)

    output_rows: List[Dict[str, Any]] = []

    for metadata_row in metadata_rows:
        chosen_indices = choose_template_indices(
            templates=templates,
            samples_per_entry=samples_per_entry,
            rng=rng,
        )

        for template_index in chosen_indices:
            template_obj = templates[template_index]
            sampled_config = sample_template_config(template_obj, rng)
            context = build_context(
                metadata_row=metadata_row,
                sampled_config=sampled_config,
                target_field=target_field,
            )

            question = render_template(template_obj["question_template"], context)
            answer = render_template(template_obj["answer_template"], context)

            row = {
                "question": question,
                "answer": answer,
            }
            if keep_metadata:
                row["metadata"] = metadata_row

            output_rows.append(row)

    write_jsonl(output_path, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Instantiate weighted Stage-2 QA templates against metadata and write "
            "JSONL or JSONL.GZ rows with keys: question, answer, metadata."
        )
    )
    parser.add_argument("--template-jsonl", required=True, type=str)
    parser.add_argument("--metadata", required=True, type=str)
    parser.add_argument("--output", required=True, type=str)
    parser.add_argument("--samples-per-entry", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument(
        "--target-field",
        default="word_count",
        type=str,
        help="Target field to use from metadata. Defaults to 'word_count'.",
    )
    parser.add_argument(
        "--no-keep-metadata",
        action="store_true",
        help="Do not include the original metadata dict in the output rows.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        target_field=args.target_field,
        keep_metadata=not args.no_keep_metadata,
    )


if __name__ == "__main__":
    main()