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
            "This template requested num2words, but the package is not installed. Install it with: pip install num2words"
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




def pretty_number(value: float | int | str) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.12g}"
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


def infer_target_field(metadata_row: Dict[str, Any]) -> str:
    preferred = ["sound_pressure_level", "target_value", "value"]
    for key in preferred:
        if key in metadata_row:
            return key

    numeric_keys = [k for k, v in metadata_row.items() if isinstance(v, (int, float))]
    if len(numeric_keys) == 1:
        return numeric_keys[0]

    raise ValueError(
        "Could not infer target field automatically from metadata. "
        "Please ensure the metadata contains 'sound_pressure_level' or a unique numeric target field."
    )


def sample_from_spec(spec: Dict[str, Any], rng: random.Random) -> Any:
    """
    Supported formats:
      {"type": "choice", "values": [...]}
      {"type": "randint", "min": 1, "max": 5}
      {"type": "uniform", "min": 0.0, "max": 1.0, "round": 3}
    """
    if "type" not in spec:
        raise ValueError(f"Sampling spec is missing 'type': {spec}")

    typ = spec["type"]

    if typ == "choice":
        values = spec.get("values", [])
        if not values:
            raise ValueError(f"Choice spec has empty values: {spec}")
        return rng.choice(values)

    if typ == "randint":
        return rng.randint(int(spec["min"]), int(spec["max"]))

    if typ == "uniform":
        value = rng.uniform(float(spec["min"]), float(spec["max"]))
        if "round" in spec:
            value = round_half_up(value, int(spec["round"]))
        return value

    raise ValueError(f"Unsupported sampling type: {typ}")


def sample_template_config(template_obj: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """
    Optional schema:

    {
      "question_template": "Is the sound pressure level at least {threshold} dB?",
      "answer_template": "{'yes' if sound_pressure_level >= threshold else 'no'}",
      "sampling_config": {
        "threshold": {"type": "choice", "values": [75, 80, 85, 90]}
      }
    }

    For coupled interval sampling, use unpack=true:

    {
      "sampling_config": {
        "interval": {
          "type": "choice",
          "values": [
            {"lower": 70, "upper": 80},
            {"lower": 80, "upper": 90}
          ],
          "unpack": true
        }
      }
    }

    If unpack=true, the sampled dict is merged into the render context, so
    {lower} and {upper} become available to both question_template and
    answer_template.
    """
    cfg = template_obj.get("sampling_config", {})
    if not cfg:
        return {}

    sampled: Dict[str, Any] = {}
    for var_name, spec in cfg.items():
        sampled_value = sample_from_spec(spec, rng)

        if spec.get("unpack", False):
            if not isinstance(sampled_value, dict):
                raise ValueError(
                    f"sampling_config[{var_name!r}] has unpack=true but sampled value is not a dict: {sampled_value}"
                )
            sampled.update(sampled_value)
        else:
            sampled[var_name] = sampled_value

    return sampled


def build_context(metadata_row: Dict[str, Any], sampled_config: Dict[str, Any]) -> Dict[str, Any]:
    target_field = infer_target_field(metadata_row)
    target_value = metadata_row[target_field]

    ctx = dict(metadata_row)
    ctx.update(sampled_config)

    ctx["target_field"] = target_field
    ctx["value"] = target_value

    ctx[f"{target_field}_rounded"] = round_half_up(target_value, 0)
    ctx[f"{target_field}_1dp"] = format_fixed(target_value, 1)
    ctx[f"{target_field}_2dp"] = format_fixed(target_value, 2)

    ctx["value_rounded"] = round_half_up(target_value, 0)
    ctx["value_1dp"] = format_fixed(target_value, 1)
    ctx["value_2dp"] = format_fixed(target_value, 2)

    return ctx


def render_template(template: str, context: Dict[str, Any]) -> str:
    protected = template.replace("{{", ESCAPED_LBRACE).replace("}}", ESCAPED_RBRACE)

    safe_globals = {
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
        "Decimal": Decimal,
        "num2words": num2words,
        "num2words_value": num2words_value,
        "digitwise_num2words": digitwise_num2words,
        "round_half_up": round_half_up,
        "format_fixed": format_fixed,
    }

    def replacer(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        try:
            value = eval(expr, safe_globals, context)
        except Exception as exc:
            raise ValueError(
                f"Failed to evaluate template expression {{{expr}}}. "
                f"Context keys: {sorted(context.keys())}"
            ) from exc
        return pretty_number(value)

    rendered = EXPR_RE.sub(replacer, protected)
    rendered = rendered.replace(ESCAPED_LBRACE, "{").replace(ESCAPED_RBRACE, "}")
    return rendered


def choose_template_indices(
    num_templates: int,
    samples_per_entry: int,
    rng: random.Random,
) -> List[int]:
    if samples_per_entry <= num_templates:
        return rng.sample(range(num_templates), k=samples_per_entry)

    indices = list(range(num_templates))
    rng.shuffle(indices)
    extra = [rng.randrange(num_templates) for _ in range(samples_per_entry - num_templates)]
    return indices + extra


def generate(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    keep_metadata: bool,
) -> None:
    rng = random.Random(seed)

    templates = list(iter_jsonl(template_jsonl))
    metadata_rows = list(iter_jsonl(metadata_path))

    if not templates:
        raise ValueError("No templates found in --template-jsonl")
    if not metadata_rows:
        raise ValueError("No metadata entries found in --metadata")

    required_keys = {"question_template", "answer_template"}
    for i, tpl in enumerate(templates):
        missing = required_keys - set(tpl.keys())
        if missing:
            raise ValueError(f"Template row {i} is missing required keys: {missing}")

    output_rows: List[Dict[str, Any]] = []

    for metadata_row in metadata_rows:
        chosen_indices = choose_template_indices(
            num_templates=len(templates),
            samples_per_entry=samples_per_entry,
            rng=rng,
        )

        for template_index in chosen_indices:
            template_obj = templates[template_index]
            sampled_config = sample_template_config(template_obj, rng)
            context = build_context(metadata_row, sampled_config)

            question = render_template(template_obj["question_template"], context)
            answer = render_template(template_obj["answer_template"], context)

            out = {
                "question": question,
                "answer": answer,
                "template_index": template_index,
            }

            if "template_id" in template_obj:
                out["template_id"] = template_obj["template_id"]

            if sampled_config:
                out["sampled_config"] = sampled_config

            if keep_metadata:
                out["metadata"] = metadata_row
            elif "id" in metadata_row:
                out["metadata_id"] = metadata_row["id"]

            output_rows.append(out)

    write_jsonl(output_path, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sample and instantiate Stage-2 templates conditioned on metadata entries."
    )
    parser.add_argument("--template-jsonl", required=True, type=str)
    parser.add_argument("--metadata", required=True, type=str)
    parser.add_argument("--output", required=True, type=str)
    parser.add_argument("--samples-per-entry", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--keep-metadata", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        keep_metadata=args.keep_metadata,
    )


if __name__ == "__main__":
    main()
