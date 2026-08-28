#!/usr/bin/env python3
"""
Instantiate Stage-1 / Stage-2 regression QA templates against a metadata manifest.

Copy this file to the task's QA directory as generate_stage1_qa.py and
generate_stage2_qa.py. The only thing that normally needs editing is
DEFAULT_TARGET_FIELD_PRIORITY (and TASK_HELPERS, if the task needs a
task-specific deterministic transform such as note_to_hz).

Template schema (one JSON object per line):

    {
      "template_id": "stage2_spl_threshold_003",
      "question_template": "Is the sound pressure level at least {threshold} dB?",
      "answer_template": "{'yes' if sound_pressure_level >= threshold else 'no'}",
      "sampling_config": {"threshold": {"type": "choice", "values": [75, 80, 85]}},
      "weight": 0.86
    }

Both question_template and answer_template are rendered the same way: every
{...} span is evaluated as a Python expression against the metadata row plus
the sampled config values. Literal braces are written {{ and }}.

Design notes (why this is fast):
  * metadata is streamed in and QA rows are streamed out; nothing accumulates
  * each template is parsed once into literal/code segments, and every distinct
    expression is compile()d once and reused for every row
  * per-row template choice is O(k log T) via cumulative weights, not O(T log T)
  * all templates are render-tested against the first metadata row before the
    full pass starts, so a bad expression fails in a second, not after an hour
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
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Task configuration -- edit these two for a new task
# ---------------------------------------------------------------------------

# Checked in order when --target-field is not passed. Put the task's declared
# regression target first. Never list an auxiliary categorical label here.
DEFAULT_TARGET_FIELD_PRIORITY: List[str] = [
    "tempo",
    "bpm",
]

# Extra deterministic helpers made available inside {...} expressions, e.g.
# {"note_to_hz": librosa.note_to_hz}. Keep every helper pure and deterministic.
TASK_HELPERS: Dict[str, Callable[..., Any]] = {}


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def open_text(path: str | Path, mode: str = "rt"):
    path = str(path)
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")


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


# ---------------------------------------------------------------------------
# Number formatting helpers (available inside {...})
# ---------------------------------------------------------------------------

def round_half_up(value: float | int | str, ndigits: int = 0) -> int | float:
    """Round half away from zero, unlike Python's banker's rounding."""
    q = Decimal("1") if ndigits == 0 else Decimal("1." + ("0" * ndigits))
    out = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    return int(out) if ndigits == 0 else float(out)


def format_fixed(value: float | int | str, ndigits: int) -> str:
    """Fixed-width decimal string, half-up: format_fixed(2.645, 1) -> '2.6'."""
    q = Decimal("1") if ndigits == 0 else Decimal("1." + ("0" * ndigits))
    out = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    return f"{out:.{ndigits}f}"


def pretty_number(value: Any) -> str:
    """Render a computed number without float noise: 0.30000000000000004 -> 0.3."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return str(value)
        return f"{value:.12g}"
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


_ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
_TENS = [
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
    "eighty", "ninety",
]


def _int_to_words(n: int) -> str:
    if n < 0:
        return "minus " + _int_to_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TENS[tens] + (f"-{_ONES[ones]}" if ones else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        out = f"{_ONES[hundreds]} hundred"
        return out + (f" and {_int_to_words(rest)}" if rest else "")
    for unit, name in ((1_000_000_000, "billion"), (1_000_000, "million"), (1000, "thousand")):
        if n >= unit:
            head, rest = divmod(n, unit)
            out = f"{_int_to_words(head)} {name}"
            return out + (f" {_int_to_words(rest)}" if rest else "")
    raise ValueError(f"Cannot spell out {n}")


def num2words_value(value: float | int | str) -> str:
    """Spell a number in English: 86.4 -> 'eighty-six point four'.

    Pure Python, no dependency. Fractional digits are read out one by one,
    which is how people say measurements aloud.
    """
    s = pretty_number(value) if isinstance(value, float) else str(value)
    if "." not in s:
        return _int_to_words(int(s))
    left, right = s.split(".", 1)
    right = right.rstrip("0")
    if not right:
        return _int_to_words(int(left))
    digits = " ".join(_ONES[int(ch)] for ch in right)
    return f"{_int_to_words(int(left))} point {digits}"


# Back-compat alias so templates written as {num2words(x)} keep working.
num2words = num2words_value


def digitwise_num2words(value: float | int | str) -> str:
    """Read every character out: 86.4 -> 'eight six point four'."""
    mapping = {str(i): _ONES[i] for i in range(10)}
    mapping["."] = "point"
    mapping["-"] = "minus"
    return " ".join(mapping[ch] for ch in str(value))


# --- note-name targets (NSynth pitch, and any note-valued task) ---------------
# Pure Python so no librosa dependency is needed; same convention as
# librosa.note_to_midi / note_to_hz, with A4 = MIDI 69 = 440 Hz.

_PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_NOTE_RE = re.compile(r"^([A-Ga-g])([#b♯♭]*)(-?\d+)$")
_MIDI_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(note: str | int | float) -> int:
    """'A4' -> 69, 'Bb3' -> 58. Accepts a MIDI number unchanged."""
    if isinstance(note, (int, float)) and not isinstance(note, bool):
        return int(note)
    match = _NOTE_RE.match(str(note).strip())
    if not match:
        raise ValueError(f"Cannot parse note name {note!r}")
    letter, accidentals, octave = match.groups()
    value = _PITCH_CLASS[letter.upper()]
    for ch in accidentals:
        value += 1 if ch in "#♯" else -1
    return value + 12 * (int(octave) + 1)


def midi_to_note(midi: int | float) -> str:
    """69 -> 'A4'."""
    midi = int(round(float(midi)))
    return f"{_MIDI_NAMES[midi % 12]}{midi // 12 - 1}"


def note_to_hz(note: str | int | float) -> float:
    """'A4' -> 440.0, rounded to 3 dp so answers stay clean."""
    return round(440.0 * (2.0 ** ((note_to_midi(note) - 69) / 12.0)), 3)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

SAFE_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    "math": math,
    "abs": abs, "min": min, "max": max, "round": round, "sum": sum,
    "int": int, "float": float, "str": str, "bool": bool, "len": len,
    "all": all, "any": any, "range": range, "divmod": divmod, "pow": pow,
    "sorted": sorted, "list": list, "tuple": tuple, "set": set, "enumerate": enumerate,
    "Decimal": Decimal,
    "round_half_up": round_half_up,
    "format_fixed": format_fixed,
    "pretty_number": pretty_number,
    "num2words": num2words,
    "num2words_value": num2words_value,
    "digitwise_num2words": digitwise_num2words,
    "note_to_midi": note_to_midi,
    "midi_to_note": midi_to_note,
    "note_to_hz": note_to_hz,
}
SAFE_GLOBALS.update(TASK_HELPERS)

# expression source -> compiled code object, shared by every template and row
_CODE_CACHE: Dict[str, Any] = {}

# A parsed template is a list of segments: str = literal, code object = expression.
Segment = Any


def parse_template(template: str) -> List[Segment]:
    """Split a template into literal and compiled-expression segments (once).

    Single left-to-right scan so that `{{` / `}}` escapes and `{expr}` spans
    cannot interfere. This matters for JSON-shaped answers such as
    '{{"F0_Hz": {F0}}}', which a naive pre-replace mangles into `{F0}}`.
    """
    segments: List[Segment] = []
    literal: List[str] = []
    i, n = 0, len(template)

    def flush() -> None:
        if literal:
            segments.append("".join(literal))
            literal.clear()

    while i < n:
        ch = template[i]
        if ch == "{":
            if i + 1 < n and template[i + 1] == "{":
                literal.append("{")
                i += 2
                continue
            end = template.find("}", i + 1)
            expr = template[i + 1:end].strip() if end != -1 else ""
            code = _try_compile(expr) if expr else None
            if code is None:
                # Not a usable expression: this brace is literal text. Covers the
                # common unescaped JSON answer '{"spl_db": {sound_pressure_level}}'.
                _warn_literal_brace(template)
                literal.append("{")
                i += 1
                continue
            flush()
            segments.append((expr, code))
            i = end + 1
            continue
        if ch == "}" and i + 1 < n and template[i + 1] == "}":
            literal.append("}")
            i += 2
            continue
        literal.append(ch)
        i += 1

    flush()
    return segments


def _try_compile(expr: str):
    """Compile an expression, or return None if it is not valid Python."""
    if expr in _CODE_CACHE:
        return _CODE_CACHE[expr]
    try:
        code = compile(expr, "<template>", "eval")
    except SyntaxError:
        return None
    _CODE_CACHE[expr] = code
    return code


_WARNED_LITERAL_BRACE: set = set()


def _warn_literal_brace(template: str) -> None:
    if template in _WARNED_LITERAL_BRACE:
        return
    _WARNED_LITERAL_BRACE.add(template)
    print(
        f"NOTE: treating a '{{' as literal text in template {template!r}. "
        "Write literal braces as {{ and }} to make this explicit.",
        file=sys.stderr,
    )


def render(segments: Sequence[Segment], env: Dict[str, Any]) -> str:
    """Render parsed segments against `env`.

    `env` is passed as eval's *globals*, not its locals. A comprehension or
    generator expression opens a new scope that resolves free names against
    globals only, so an expression like
    `all(word_count % d for d in range(...))` raises NameError when the
    metadata lives in a separate locals mapping.
    """
    parts: List[str] = []
    for seg in segments:
        if isinstance(seg, str):
            parts.append(seg)
            continue
        expr, code = seg
        try:
            value = eval(code, env)  # noqa: S307 - sandboxed globals, no builtins
        except Exception as exc:
            names = sorted(k for k in env if not k.startswith("__"))
            raise ValueError(
                f"Failed to evaluate template expression {{{expr}}} ({type(exc).__name__}: {exc}). "
                f"Available names: {names}"
            ) from exc
        parts.append(pretty_number(value))
    return "".join(parts)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class Template:
    __slots__ = ("index", "template_id", "question", "answer", "sampling_config", "weight")

    def __init__(self, index: int, obj: Dict[str, Any]) -> None:
        missing = {"question_template", "answer_template"} - set(obj)
        if missing:
            raise ValueError(f"Template row {index} is missing required keys: {sorted(missing)}")
        self.index = index
        self.template_id = obj.get("template_id", f"template_{index:04d}")
        self.question = parse_template(obj["question_template"])
        self.answer = parse_template(obj["answer_template"])
        self.sampling_config: Dict[str, Any] = obj.get("sampling_config") or {}
        if "weight" not in obj:
            raise ValueError(
                f"Template row {index} ({self.template_id}) is missing 'weight'. "
                "Every template must carry a naturalness weight in (0, 1]."
            )
        self.weight = float(obj["weight"])
        if not 0.0 < self.weight <= 1.0:
            raise ValueError(
                f"Template row {index} ({self.template_id}) has weight {self.weight}; expected (0, 1]."
            )


def sample_from_spec(spec: Dict[str, Any], rng: random.Random) -> Any:
    typ = spec.get("type")
    if typ == "choice":
        values = spec.get("values") or []
        if not values:
            raise ValueError(f"Choice spec has empty values: {spec}")
        return rng.choice(values)
    if typ == "randint":
        return rng.randint(int(spec["min"]), int(spec["max"]))
    if typ == "uniform":
        value = rng.uniform(float(spec["min"]), float(spec["max"]))
        return round_half_up(value, int(spec["round"])) if "round" in spec else value
    raise ValueError(f"Unsupported sampling type {typ!r} in spec: {spec}")


def sample_config(template: Template, rng: random.Random) -> Dict[str, Any]:
    """Draw this template's parameters. unpack=true merges a dict of coupled values."""
    if not template.sampling_config:
        return {}
    sampled: Dict[str, Any] = {}
    for name, spec in template.sampling_config.items():
        value = sample_from_spec(spec, rng)
        if spec.get("unpack", False):
            if not isinstance(value, dict):
                raise ValueError(
                    f"sampling_config[{name!r}] has unpack=true but sampled a non-dict: {value!r}"
                )
            sampled.update(value)
        else:
            sampled[name] = value
    return sampled


# ---------------------------------------------------------------------------
# Weighted choice of k distinct templates per metadata entry
# ---------------------------------------------------------------------------

def build_cum_weights(templates: Sequence[Template]) -> List[float]:
    total = 0.0
    cum: List[float] = []
    for t in templates:
        total += t.weight
        cum.append(total)
    return cum


def choose_indices(
    cum_weights: List[float],
    k: int,
    rng: random.Random,
) -> List[int]:
    """Pick k distinct template indices, favouring higher weights.

    Successive weighted draws with rejection of repeats. k is small (2-8) and
    T is large (80-400), so collisions are rare and this stays O(k log T) --
    the reason a full 400k-row run does not spend its time in the sampler.
    """
    n = len(cum_weights)
    if k >= n:
        return list(range(n))
    total = cum_weights[-1]
    chosen: List[int] = []
    seen = set()
    attempts = 0
    budget = 20 * k + 50
    while len(chosen) < k and attempts < budget:
        attempts += 1
        i = bisect.bisect(cum_weights, rng.random() * total)
        if i >= n:
            i = n - 1
        if i not in seen:
            seen.add(i)
            chosen.append(i)
    if len(chosen) < k:  # degenerate weights: fill deterministically
        for i in range(n):
            if len(chosen) == k:
                break
            if i not in seen:
                seen.add(i)
                chosen.append(i)
    return chosen


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

def resolve_target_field(row: Dict[str, Any], target_field: str | None) -> str:
    if target_field is not None:
        if target_field not in row:
            raise ValueError(
                f"--target-field {target_field!r} is not in the metadata row. "
                f"Available keys: {sorted(row)}"
            )
        return target_field
    for key in DEFAULT_TARGET_FIELD_PRIORITY:
        if key in row:
            return key
    numeric = [k for k, v in row.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if len(numeric) == 1:
        return numeric[0]
    raise ValueError(
        "Could not infer the target field. Pass --target-field explicitly. "
        f"Numeric keys present: {sorted(numeric)}"
    )


def new_env() -> Dict[str, Any]:
    """A reusable evaluation environment seeded with the safe helpers."""
    return dict(SAFE_GLOBALS)


def fill_env(
    env: Dict[str, Any],
    row: Dict[str, Any],
    sampled: Dict[str, Any],
    target_field: str,
) -> Dict[str, Any]:
    """Load one metadata row plus its sampled parameters into `env`, in place.

    Reusing one dict avoids allocating a fresh context per QA pair. Every row
    has the same schema, so nothing meaningful goes stale between rows.
    Metadata keys deliberately shadow helpers of the same name.
    """
    raw = row[target_field]
    if isinstance(raw, str):
        # Numeric strings are coerced; symbolic targets such as note names
        # ('F5') stay as-is and are converted inside the template expression
        # via note_to_midi / note_to_hz.
        try:
            value = float(raw)
        except ValueError:
            value = raw
    else:
        value = raw

    env.update(row)
    env[target_field] = value
    if sampled:
        env.update(sampled)

    env["target_field"] = target_field
    env["value"] = value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        rounded = round_half_up(value, 0)
        fixed1 = format_fixed(value, 1)
        fixed2 = format_fixed(value, 2)
        for prefix in (target_field, "value"):
            env[f"{prefix}_rounded"] = rounded
            env[f"{prefix}_1dp"] = fixed1
            env[f"{prefix}_2dp"] = fixed2
    return env


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def load_templates(path: str) -> List[Template]:
    templates = [Template(i, obj) for i, obj in enumerate(iter_jsonl(path))]
    if not templates:
        raise ValueError(f"No templates found in {path}")
    seen: Dict[str, int] = {}
    dupes: List[str] = []
    for t in templates:
        if t.template_id in seen:
            dupes.append(t.template_id)
        else:
            seen[t.template_id] = t.index
    if dupes:
        print(
            f"WARNING: {len(dupes)} duplicate template_id value(s) in {path}, "
            f"e.g. {sorted(set(dupes))[:3]}. Generation still works, but IDs should be "
            "unique so templates stay traceable. Run validate_templates.py to list them.",
            file=sys.stderr,
        )
    return templates


def smoke_test(templates: Sequence[Template], row: Dict[str, Any], target_field: str) -> None:
    """Render every template once before the real pass, so failures are instant."""
    rng = random.Random(0)
    env = new_env()
    for t in templates:
        fill_env(env, row, sample_config(t, rng), target_field)
        try:
            render(t.question, env)
            render(t.answer, env)
        except ValueError as exc:
            raise ValueError(f"Template {t.template_id} failed its render check: {exc}") from exc


def generate(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    target_field: str | None,
    keep_metadata: bool,
    limit: int | None,
    verbose: bool,
) -> Tuple[int, int]:
    """Stream metadata through the templates, writing one QA row per pair."""
    if samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be a positive integer")

    rng = random.Random(seed)
    templates = load_templates(template_jsonl)
    cum_weights = build_cum_weights(templates)

    rows = iter_jsonl(metadata_path)
    try:
        first_row = next(rows)
    except StopIteration:
        raise ValueError(f"No metadata entries found in {metadata_path}") from None

    resolved_field = resolve_target_field(first_row, target_field)

    # The smoke test needs a row with a usable target, which the first one may not be.
    buffered: List[Dict[str, Any]] = [first_row]
    probe = first_row
    while probe.get(resolved_field) is None:
        try:
            probe = next(rows)
        except StopIteration:
            raise ValueError(
                f"Every metadata entry has a null {resolved_field!r}; nothing to generate."
            ) from None
        buffered.append(probe)
    smoke_test(templates, probe, resolved_field)

    n_entries = 0
    n_pairs = 0
    n_skipped = 0
    dumps = json.dumps
    env = new_env()

    with open_text(output_path, "wt") as out:
        for row in _chain(buffered, rows):
            if limit is not None and n_entries >= limit:
                break
            # A null target would render as the literal string "None" in the answer,
            # which silently poisons the training set. Skip and report instead.
            if row.get(resolved_field) is None or row.get(resolved_field) == "":
                n_skipped += 1
                continue
            n_entries += 1
            for idx in choose_indices(cum_weights, samples_per_entry, rng):
                tpl = templates[idx]
                fill_env(env, row, sample_config(tpl, rng), resolved_field)
                record = {
                    "question": render(tpl.question, env),
                    "answer": render(tpl.answer, env),
                }
                if keep_metadata:
                    record["metadata"] = row
                elif "id" in row:
                    record["metadata_id"] = row["id"]
                out.write(dumps(record, ensure_ascii=False))
                out.write("\n")
                n_pairs += 1
            if verbose and n_entries % 50_000 == 0:
                print(f"  ... {n_entries:,} entries -> {n_pairs:,} pairs", file=sys.stderr)

    if n_skipped:
        print(
            f"WARNING: skipped {n_skipped:,} metadata entr(ies) with a null {resolved_field!r}.",
            file=sys.stderr,
        )
    return n_entries, n_pairs


def _chain(buffered: Sequence[Dict[str, Any]], rest: Iterable[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    yield from buffered
    yield from rest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Instantiate weighted regression QA templates against a metadata manifest. "
                    "Writes JSONL(.gz) rows of {question, answer, metadata}."
    )
    p.add_argument("--template-jsonl", required=True)
    p.add_argument("--metadata", required=True, help="metadata manifest, .jsonl or .jsonl.gz")
    p.add_argument("--output", required=True, help="output path; .gz enables compression")
    p.add_argument("--samples-per-entry", required=True, type=int,
                   help="distinct templates instantiated per metadata entry")
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--target-field", default=None,
                   help="the declared regression target; required when several numeric fields exist")
    p.add_argument("--no-keep-metadata", dest="keep_metadata", action="store_false",
                   help="store only metadata_id instead of the full metadata row")
    p.add_argument("--limit", type=int, default=None, help="stop after N metadata entries (smoke test)")
    p.add_argument("--quiet", dest="verbose", action="store_false")
    p.set_defaults(keep_metadata=True, verbose=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    n_entries, n_pairs = generate(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        target_field=args.target_field,
        keep_metadata=args.keep_metadata,
        limit=args.limit,
        verbose=args.verbose,
    )
    if args.verbose:
        print(f"{n_entries:,} metadata entries -> {n_pairs:,} QA pairs written to {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
