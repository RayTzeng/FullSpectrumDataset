#!/usr/bin/env python3
"""
Instantiate Stage-1 / Stage-2 classification QA templates against a metadata manifest.

Copy this file to the task's QA directory as generate_stage1_qa.py and
generate_stage2_qa.py. The only things that normally need editing are
DEFAULT_TARGET_FIELD_PRIORITY and, rarely, TASK_HELPERS.

Template schema (one JSON object per line):

    {
      "template_id": "stage1_event_label_mcq_003",
      "question_template": "Which of these matches the clip? {options_block(options)}",
      "answer_template": "({letter_of(options, gold_option)})",
      "sampling_config": {"opts": {"type": "mcq_options", "n_options": 4,
                                   "distractors": "same:category", "unpack": true}},
      "weight": 0.78
    }

Both question_template and answer_template are rendered the same way: every
{...} span is evaluated as a Python expression against the metadata row plus
the sampled config values. Literal braces are written {{ and }}.

What this adds over the regression generator:

  * a label space, either passed in or derived from the manifest in one pass,
    with per-label counts kept for frequency-weighted distractor sampling
  * row-dependent sampling: `label_probe`, `positive_label`, `negative_label`
    and `mcq_options` all need to know the row's gold label(s), so the sampler
    receives the row rather than only the rng
  * a `label_semantics.json` side-car exposed as sem(label, slot), which is
    where every Stage-2 reasoning answer comes from
  * multi-label plumbing: as_labels / has_label / n_labels / join_labels over
    both list-valued fields and separator-joined strings

Design notes (why this is fast):
  * metadata is streamed in and QA rows are streamed out; nothing accumulates
  * each template is parsed once into literal/code segments, and every distinct
    expression is compile()d once and reused for every row
  * per-row template choice is O(k log T) via cumulative weights, not O(T log T)
  * all templates are render-tested against the first usable row before the full
    pass starts, so a bad expression fails in a second, not after an hour
"""

from __future__ import annotations

import argparse
import bisect
import collections
import csv
import gzip
import json
import math
import random
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Task configuration -- edit these for a new task
# ---------------------------------------------------------------------------

# Checked in order when --target-field is not passed. Put the task's declared
# classification target first. Never list an auxiliary label from the same
# manifest (SEP28K keeps both `stuttering` and `stuttering_type`).
DEFAULT_TARGET_FIELD_PRIORITY: List[str] = [
    "label",
]

# Separator for multi-label targets stored as one string. AudioSet writes
# "Speech; Gush". NEVER guess this: VggSound labels contain commas of their own
# ("bird chirping, tweeting"), so a comma-splitting default would shred them.
DEFAULT_LABEL_SEPARATOR = ";"

# Values that mean "no label applies" rather than naming a class. SEP28K stores
# stuttering_type="none" on every non-stuttered clip. as_labels() maps these to
# the empty list so n_labels() and has_label() stay honest.
DEFAULT_NONE_LABELS = ("none", "None", "", "N/A", "n/a", "unknown", "Unknown")

# Extra deterministic helpers made available inside {...}. Keep every helper pure.
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
# Number formatting helpers (available inside {...}; multi-label counts use them)
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
    for unit, name in ((1_000_000, "million"), (1000, "thousand")):
        if n >= unit:
            head, rest = divmod(n, unit)
            return f"{_int_to_words(head)} {name}" + (f" {_int_to_words(rest)}" if rest else "")
    raise ValueError(f"Cannot spell out {n}")


def num2words_value(value: float | int | str) -> str:
    """Spell a number in English: 3 -> 'three'. Counts only; no fractions needed."""
    s = str(value)
    if "." not in s:
        return _int_to_words(int(s))
    left, right = s.split(".", 1)
    right = right.rstrip("0")
    if not right:
        return _int_to_words(int(left))
    digits = " ".join(_ONES[int(ch)] for ch in right)
    return f"{_int_to_words(int(left))} point {digits}"


num2words = num2words_value


# ---------------------------------------------------------------------------
# Label plumbing
# ---------------------------------------------------------------------------

# Module-level so templates can call as_labels()/has_label() with one argument;
# set once by configure_labels() before any rendering happens.
_LABEL_SEPARATOR = DEFAULT_LABEL_SEPARATOR
_NONE_LABELS = set(DEFAULT_NONE_LABELS)


def as_labels(value: Any) -> List[str]:
    """Normalise a target field to a list of label strings.

    Handles the three shapes the manifests actually use:
      ["rock", "pop"]      -> ["rock", "pop"]        (MTG-Jamendo, ParaSpeechCaps)
      "Speech; Gush"       -> ["Speech", "Gush"]     (AudioSet, SEP28K, FSD50k)
      "playing timbales"   -> ["playing timbales"]   (VggSound and every single-label task)

    A none-sentinel collapses to the empty list, so a clip with
    stuttering_type="none" honestly has zero labels.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = [str(v).strip() for v in value]
    else:
        text = str(value).strip()
        items = [p.strip() for p in text.split(_LABEL_SEPARATOR)] if _LABEL_SEPARATOR else [text]
    return [x for x in items if x and x not in _NONE_LABELS]


def join_labels(labels: Iterable[str], sep: str = "; ") -> str:
    """Serialise a label list. The default matches the manifests' own '; ' style."""
    return sep.join(labels)


def has_label(value: Any, label: str) -> bool:
    """Membership test that works for single-label and multi-label fields alike.

    Case-insensitive, because a probe label sampled from the inventory should
    still match when a template lowercases it for a natural-sounding question.
    """
    target = str(label).strip().casefold()
    return any(x.casefold() == target for x in as_labels(value))


def n_labels(value: Any) -> int:
    """How many labels apply. Zero for a none-sentinel."""
    return len(as_labels(value))


def sort_labels(value: Any) -> List[str]:
    """Alphabetical order, for templates that ask for a sorted list explicitly."""
    return sorted(as_labels(value), key=str.casefold)


def a_or_an(word: str) -> str:
    """Indefinite article for a label, so composed sentences read naturally."""
    return "an" if str(word)[:1].lower() in "aeiou" else "a"


def and_list(items: Sequence[str]) -> str:
    """'a', 'b', 'c' -> 'a, b, and c'. For prose answers over multi-label fields."""
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


class LabelSpace:
    """The task's label inventory plus per-label counts.

    Counts drive frequency-weighted distractor sampling, which keeps MCQ options
    looking like labels a real system would confuse rather than a uniform draw
    from a 5,000-name species list.
    """

    __slots__ = ("labels", "counts", "_index", "_cum", "_total")

    def __init__(self, counts: Dict[str, int]) -> None:
        self.labels: List[str] = sorted(counts, key=str.casefold)
        self.counts = counts
        self._index = {lab: i for i, lab in enumerate(self.labels)}
        total = 0.0
        cum: List[float] = []
        for lab in self.labels:
            total += max(float(counts.get(lab, 0)), 1.0)
            cum.append(total)
        self._cum = cum
        self._total = total

    def __len__(self) -> int:
        return len(self.labels)

    def sample(self, rng: random.Random, exclude: Sequence[str], weighting: str) -> str | None:
        """One label not in `exclude`. Rejection sampling: the excluded set is tiny."""
        blocked = {x.casefold() for x in exclude}
        if len(blocked) >= len(self.labels):
            return None
        for _ in range(64):
            lab = self._draw(rng, weighting)
            if lab.casefold() not in blocked:
                return lab
        pool = [x for x in self.labels if x.casefold() not in blocked]
        return rng.choice(pool) if pool else None

    def _draw(self, rng: random.Random, weighting: str) -> str:
        if weighting == "uniform":
            return rng.choice(self.labels)
        i = bisect.bisect(self._cum, rng.random() * self._total)
        return self.labels[min(i, len(self.labels) - 1)]

    def sample_many(
        self,
        rng: random.Random,
        k: int,
        exclude: Sequence[str],
        weighting: str,
        pool: Sequence[str] | None = None,
    ) -> List[str]:
        """k distinct labels, drawn from `pool` if given, else the whole space."""
        blocked = {x.casefold() for x in exclude}
        out: List[str] = []
        if pool is not None:
            candidates = [x for x in pool if x.casefold() not in blocked]
            rng.shuffle(candidates)
            out = candidates[:k]
            if len(out) == k:
                return out
            blocked |= {x.casefold() for x in out}
        while len(out) < k:
            lab = self.sample(rng, sorted(blocked), weighting)
            if lab is None:
                break
            out.append(lab)
            blocked.add(lab.casefold())
        return out


def load_label_space(path: str | Path) -> Dict[str, int]:
    """Read a label inventory from .txt (one per line), .json, or a *_stats.csv.

    The stats.csv shape is the one the metadata folders already ship:
    `common_name,train_count,test_count,total_count`, with a `__samples__` row
    that is a grand total, not a label.
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): int(v) for k, v in data.items()}
        return {str(k): 1 for k in data}
    if suffix == ".csv":
        counts: Dict[str, int] = {}
        with p.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or not row[0].strip() or row[0].strip() == "__samples__":
                    continue
                label = row[0].strip()
                count = 1
                for cell in reversed(row[1:]):
                    try:
                        count = int(float(cell))
                        break
                    except (TypeError, ValueError):
                        continue
                counts[label] = count
        if not counts:
            raise ValueError(f"No labels parsed from {p} (header was {header!r})")
        return counts
    counts = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1
    return counts


def derive_label_space(metadata_path: str, target_field: str, max_rows: int | None = None) -> Dict[str, int]:
    """Count every label in the manifest. One streaming pass, no accumulation.

    This, not the README, is the source of truth for the inventory: GLOBE's
    README lists 10 accents by way of illustration where the manifest holds 254.
    """
    counts: collections.Counter = collections.Counter()
    for i, row in enumerate(iter_jsonl(metadata_path)):
        if max_rows is not None and i >= max_rows:
            break
        counts.update(as_labels(row.get(target_field)))
    if not counts:
        raise ValueError(
            f"No labels found under {target_field!r} in {metadata_path}. "
            "Check --target-field and --label-separator."
        )
    return dict(counts)


# ---------------------------------------------------------------------------
# label_semantics.json -- where every Stage-2 answer comes from
# ---------------------------------------------------------------------------

class Semantics:
    """Label -> attribute-slot lookup, loaded from label_semantics.json.

    Schema:
        {"_meta": {"target_field": "event_label",
                   "slots": {"category": {"kind": "closed",
                                          "values": ["human", "animal", ...],
                                          "certainty": "certain"},
                             "activity": {"kind": "prose",
                                          "certainty": "plausible"}}},
         "labels": {"dog barking": {"category": "animal", "activity": "..."}}}

    Lookups fail loudly. A silent fallback would emit a plausible-looking wrong
    answer for every clip carrying an unmapped label, which is the single most
    expensive mistake available here.
    """

    __slots__ = ("meta", "table", "_fold", "strict")

    def __init__(self, obj: Dict[str, Any], strict: bool = True) -> None:
        self.meta = obj.get("_meta", {}) or {}
        self.table = obj.get("labels", obj if "labels" not in obj else {}) or {}
        self._fold = {str(k).casefold(): k for k in self.table}
        self.strict = strict

    @classmethod
    def load(cls, path: str | Path, strict: bool = True) -> "Semantics":
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(obj, strict=strict)

    @classmethod
    def empty(cls) -> "Semantics":
        return cls({"_meta": {}, "labels": {}}, strict=True)

    def slots(self) -> Dict[str, Any]:
        return self.meta.get("slots", {}) or {}

    def get(self, label: str, slot: str, default: Any = None) -> Any:
        key = self._fold.get(str(label).strip().casefold())
        if key is None:
            if default is not None or not self.strict:
                return default
            raise KeyError(
                f"label_semantics.json has no entry for {label!r}. Every label in the "
                f"manifest needs one, or Stage-2 answers become guesses. Run "
                f"profile_labels.py --semantics <file> to list what is missing."
            )
        entry = self.table[key]
        if slot not in entry:
            if default is not None or not self.strict:
                return default
            raise KeyError(
                f"label_semantics.json entry for {label!r} has no slot {slot!r} "
                f"(has: {sorted(entry)})."
            )
        return entry[slot]

    def missing(self, labels: Iterable[str], slot: str | None = None) -> List[str]:
        out = []
        for lab in labels:
            key = self._fold.get(str(lab).strip().casefold())
            if key is None:
                out.append(lab)
            elif slot is not None and slot not in self.table[key]:
                out.append(lab)
        return out

    def labels_with(self, slot: str, value: Any) -> List[str]:
        """Every label whose `slot` equals `value` -- the confusable-distractor pool."""
        return [k for k, v in self.table.items() if v.get(slot) == value]

    def labels_without(self, slot: str, value: Any) -> List[str]:
        return [k for k, v in self.table.items() if slot in v and v.get(slot) != value]


_SEMANTICS = Semantics.empty()
_DISPLAY: Dict[str, str] = {}


def sem(label: Any, slot: str, default: Any = None) -> Any:
    """Attribute lookup for one label: sem(event_label, 'category') -> 'animal'."""
    if isinstance(label, (list, tuple, set)):
        labs = as_labels(label)
        label = labs[0] if labs else ""
    return _SEMANTICS.get(str(label), slot, default)


def sem_all(value: Any, slot: str) -> List[str]:
    """Slot values for every label on a multi-label row, de-duplicated, ordered."""
    seen: List[str] = []
    for lab in as_labels(value):
        got = _SEMANTICS.get(lab, slot, None)
        if got is not None and got not in seen:
            seen.append(got)
    return seen


def sem_any(value: Any, slot: str, wanted: Any) -> bool:
    """Does any label on this row carry `wanted` in `slot`?"""
    return wanted in sem_all(value, slot)


def because(label: Any, slot: str, connective: str = "is commonly associated with") -> str:
    """The because-clause of a justified Stage-2 answer.

    Returns the authored `<slot>_why` when the semantics file has one, else a
    generic clause built from the label name -- which is the shape the guide
    sheet's own examples use ("because bird chirping is commonly associated with
    outdoor environments"). The main slot is fetched first and strictly, so an
    unmapped label still raises rather than yielding a clause about nothing.
    """
    value = sem(label, slot)
    if isinstance(label, (list, tuple, set)):
        labs = as_labels(label)
        label = labs[0] if labs else ""
    authored = _SEMANTICS.get(str(label), f"{slot}_why", "")
    if authored:
        return authored
    # The generic clause names the label and points at the slot value, exactly as
    # the guide sheet does: "because bird chirping is commonly associated with
    # outdoor environments". That only reads as a reason when the value is a
    # short category. Composed against a descriptive prose value it degenerates
    # into restating the verdict -- "because cough is commonly associated with a
    # room where someone has a cold" -- so a prose slot has to author its own.
    if (_SEMANTICS.slots().get(slot, {}) or {}).get("kind") == "prose":
        raise KeyError(
            f"because({label!r}, {slot!r}): {slot!r} is a prose slot, so the generic "
            f"clause would just restate the answer. Author {slot}_why for this label, "
            f"or justify from a closed slot instead."
        )
    return f"{pretty_label(label)} {connective} {value}"


def caveat(label: Any, slot: str, fallback: str = "other contexts are possible") -> str:
    """The concession clause: authored `<slot>_caveat`, else a generic hedge."""
    sem(label, slot)                       # strict: unmapped labels must still raise
    if isinstance(label, (list, tuple, set)):
        labs = as_labels(label)
        label = labs[0] if labs else ""
    return _SEMANTICS.get(str(label), f"{slot}_caveat", "") or fallback


def pretty_label(label: Any) -> str:
    """Display form of a label: 'Sound_Repetition' -> 'sound repetition'.

    Overridable per label via a `_display` map in label_semantics.json, for the
    cases the generic rule gets wrong ('Aves(birds)' -> 'birds').
    """
    if isinstance(label, (list, tuple, set)):
        return and_list([pretty_label(x) for x in as_labels(label)])
    text = str(label)
    if text in _DISPLAY:
        return _DISPLAY[text]
    return text.replace("_", " ").strip()


# ---------------------------------------------------------------------------
# Multiple-choice rendering
# ---------------------------------------------------------------------------

_LETTERS = "ABCDEFGH"


def options_block(options: Sequence[str], style: str = "letter", sep: str = "   ") -> str:
    """Render an option list for the question text.

    style="letter"  -> "(A) dog barking   (B) cat meowing"
    style="number"  -> "1. dog barking   2. cat meowing"
    style="inline"  -> "dog barking, cat meowing, or bird chirping"
    style="lines"   -> one option per line, letter-marked

    Vary the style across templates: a set where every MCQ looks identical
    teaches the format, not the task.
    """
    opts = [pretty_label(o) for o in options]
    if style == "inline":
        if len(opts) == 1:
            return opts[0]
        return ", ".join(opts[:-1]) + f", or {opts[-1]}"
    if style == "number":
        return sep.join(f"{i + 1}. {o}" for i, o in enumerate(opts))
    if style == "lines":
        return "\n".join(f"({_LETTERS[i]}) {o}" for i, o in enumerate(opts))
    return sep.join(f"({_LETTERS[i]}) {o}" for i, o in enumerate(opts))


def letter_of(options: Sequence[str], value: str, style: str = "letter") -> str:
    """The marker of `value` within `options`: 'A', or '1' for style='number'."""
    target = str(value).strip().casefold()
    for i, opt in enumerate(options):
        if str(opt).strip().casefold() == target:
            return str(i + 1) if style == "number" else _LETTERS[i]
    raise ValueError(
        f"{value!r} is not among the options {list(options)!r}. An mcq_options draw "
        "always contains the gold label, so this means the answer template referenced "
        "the wrong variable."
    )


def option_of(options: Sequence[str], value: str, style: str = "letter") -> str:
    """'(B) cat meowing' -- the letter-plus-text answer form."""
    mark = letter_of(options, value, style)
    text = pretty_label(value)
    return f"{mark}. {text}" if style == "number" else f"({mark}) {text}"


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

SAFE_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    "math": math,
    "abs": abs, "min": min, "max": max, "round": round, "sum": sum,
    "int": int, "float": float, "str": str, "bool": bool, "len": len,
    "all": all, "any": any, "range": range, "divmod": divmod, "pow": pow,
    "sorted": sorted, "list": list, "tuple": tuple, "set": set, "dict": dict,
    "enumerate": enumerate, "zip": zip, "reversed": reversed, "Decimal": Decimal,
    # numbers
    "round_half_up": round_half_up,
    "format_fixed": format_fixed,
    "num2words": num2words,
    "num2words_value": num2words_value,
    # labels
    "as_labels": as_labels,
    "join_labels": join_labels,
    "has_label": has_label,
    "n_labels": n_labels,
    "sort_labels": sort_labels,
    "and_list": and_list,
    "a_or_an": a_or_an,
    "pretty_label": pretty_label,
    # semantics
    "sem": sem,
    "sem_all": sem_all,
    "sem_any": sem_any,
    "because": because,
    "caveat": caveat,
    # multiple choice
    "options_block": options_block,
    "letter_of": letter_of,
    "option_of": option_of,
}
SAFE_GLOBALS.update(TASK_HELPERS)

# expression source -> compiled code object, shared by every template and row
_CODE_CACHE: Dict[str, Any] = {}

# A parsed template is a list of segments: str = literal, (expr, code) = expression.
Segment = Any


def parse_template(template: str) -> List[Segment]:
    """Split a template into literal and compiled-expression segments (once).

    Single left-to-right scan so that `{{` / `}}` escapes and `{expr}` spans
    cannot interfere. This matters for JSON-shaped answers such as
    '{{"events": "{join_labels(as_labels(audio_events))}"}}'.
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
            end = _matching_brace(template, i)
            expr = template[i + 1:end].strip() if end != -1 else ""
            code = _try_compile(expr) if expr else None
            if code is None:
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


def _matching_brace(template: str, start: int) -> int:
    """Index of the '}' closing the '{' at `start`, allowing nested dict/set literals.

    The regression generator took the first '}', which is enough for arithmetic
    but not for the comprehensions and dict literals classification templates
    need: {' '.join({'a': 1}[k] for k in x)}.
    """
    depth = 0
    in_str = ""
    i = start
    n = len(template)
    while i < n:
        ch = template[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = ""
        elif ch in "'\"":
            in_str = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


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


def render_value(value: Any) -> str:
    """Stringify one evaluated expression.

    A list renders as a joined label list, which is what a bare
    `{genre}` on MTG-Jamendo's list-valued field should produce.
    """
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return join_labels([str(v) for v in value])
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return str(value)
        return f"{value:.12g}"
    return str(value)


def render(segments: Sequence[Segment], env: Dict[str, Any]) -> str:
    """Render parsed segments against `env`.

    `env` is passed as eval's *globals*, not its locals. A comprehension opens a
    new scope that resolves free names against globals only, so an expression
    like `[x for x in as_labels(audio_events)]` would raise NameError if the
    metadata lived in a separate locals mapping.
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
        parts.append(render_value(value))
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


# ---------------------------------------------------------------------------
# Sampling
#
# Unlike the regression generator, four of these specs are row-dependent: a
# probe label, a guaranteed-wrong label and an MCQ option list all have to know
# what this clip's gold label is. So the sampler takes the gold set as well as
# the rng, and every draw happens per row rather than once per template.
# ---------------------------------------------------------------------------

def _pool_for(spec: Dict[str, Any], gold: Sequence[str], space: LabelSpace) -> Sequence[str] | None:
    """Resolve a `distractors` directive into a candidate pool, or None for 'any'.

      "random"          -> None (the whole label space)
      "same:<slot>"     -> labels sharing this row's slot value  (confusable)
      "diff:<slot>"     -> labels with a different slot value    (easy)
      {"values": [...]} -> an explicit pool
    """
    if spec.get("values"):
        return [str(v) for v in spec["values"]]
    directive = spec.get("distractors", "random")
    if not isinstance(directive, str) or ":" not in directive:
        return None
    mode, slot = directive.split(":", 1)
    anchor = gold[0] if gold else None
    if anchor is None:
        return None
    value = _SEMANTICS.get(anchor, slot, None)
    if value is None:
        return None
    pool = _SEMANTICS.labels_with(slot, value) if mode == "same" else _SEMANTICS.labels_without(slot, value)
    known = {lab.casefold() for lab in space.labels}
    pool = [lab for lab in pool if lab.casefold() in known]
    return pool or None


def sample_from_spec(
    spec: Dict[str, Any],
    rng: random.Random,
    gold: Sequence[str],
    space: LabelSpace,
) -> Any:
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

    weighting = spec.get("weighting", "frequency")

    if typ == "label_probe":
        # A candidate label for a yes/no question. p_positive of the time it is
        # one of this clip's own labels, so the yes/no answer stays balanced.
        # The answer template still recomputes the verdict with has_label();
        # it never trusts the sampler.
        p_pos = float(spec.get("p_positive", 0.5))
        if gold and rng.random() < p_pos:
            return rng.choice(list(gold))
        pool = _pool_for(spec, gold, space)
        drawn = space.sample_many(rng, 1, gold, weighting, pool)
        return drawn[0] if drawn else (gold[0] if gold else "")
    if typ == "positive_label":
        if not gold:
            raise ValueError(
                "positive_label was requested for a row with no labels. Guard the "
                "template, or filter none-valued rows out of the manifest."
            )
        return rng.choice(list(gold))
    if typ == "negative_label":
        pool = _pool_for(spec, gold, space)
        drawn = space.sample_many(rng, 1, gold, weighting, pool)
        if not drawn:
            raise ValueError("negative_label: the label space holds nothing outside the gold set.")
        return drawn[0]

    if typ == "mcq_options":
        n = int(spec.get("n_options", 4))
        if not gold:
            raise ValueError(
                "mcq_options was requested for a row with no labels; nothing can be the "
                "correct option. Guard the template or filter the manifest."
            )
        correct = rng.choice(list(gold))
        pool = _pool_for(spec, gold, space)
        # Every gold label is excluded, not just the drawn one: on a multi-label
        # row a second true label would make two options correct.
        distractors = space.sample_many(rng, n - 1, list(gold), weighting, pool)
        options = [correct] + distractors
        if spec.get("order") == "alpha":
            options = sorted(options, key=str.casefold)
        else:
            rng.shuffle(options)          # uniform gold position -> uniform letter
        return {"options": options, "gold_option": correct, "n_options": len(options)}

    raise ValueError(f"Unsupported sampling type {typ!r} in spec: {spec}")


def sample_config(
    template: Template,
    rng: random.Random,
    gold: Sequence[str],
    space: LabelSpace,
) -> Dict[str, Any]:
    """Draw this template's parameters. unpack=true merges a dict of coupled values."""
    if not template.sampling_config:
        return {}
    sampled: Dict[str, Any] = {}
    for name, spec in template.sampling_config.items():
        value = sample_from_spec(spec, rng, gold, space)
        # mcq_options always yields coupled values, so unpacking is implicit.
        if spec.get("unpack", False) or spec.get("type") == "mcq_options":
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


def choose_indices(cum_weights: List[float], k: int, rng: random.Random) -> List[int]:
    """Pick k distinct template indices, favouring higher weights.

    Successive weighted draws with rejection of repeats. k is small (1-8) and T
    is large (100-500), so collisions are rare and this stays O(k log T).
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

def configure_labels(separator: str | None, none_labels: Sequence[str] | None) -> None:
    """Set the module-level label conventions before anything is rendered."""
    global _LABEL_SEPARATOR, _NONE_LABELS
    if separator is not None:
        _LABEL_SEPARATOR = separator
    if none_labels is not None:
        _NONE_LABELS = set(none_labels)


def configure_semantics(path: str | None, strict: bool = True) -> Semantics:
    global _SEMANTICS, _DISPLAY
    _SEMANTICS = Semantics.load(path, strict=strict) if path else Semantics.empty()
    raw = json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    _DISPLAY = {str(k): str(v) for k, v in (raw.get("_display") or {}).items()}
    return _SEMANTICS


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
    raise ValueError(
        "Could not infer the target field. Pass --target-field explicitly. "
        f"Keys present: {sorted(row)}"
    )


def new_env() -> Dict[str, Any]:
    """A reusable evaluation environment seeded with the safe helpers."""
    return dict(SAFE_GLOBALS)


def fill_env(
    env: Dict[str, Any],
    row: Dict[str, Any],
    sampled: Dict[str, Any],
    target_field: str,
    space: LabelSpace | None = None,
) -> Dict[str, Any]:
    """Load one metadata row plus its sampled parameters into `env`, in place.

    Reusing one dict avoids allocating a fresh context per QA pair. Every row has
    the same schema, so nothing goes stale between rows. Label values are never
    coerced: '0' stays the string '0' so the answer matches the manifest exactly.
    """
    env.update(row)
    if sampled:
        env.update(sampled)

    labels = as_labels(row.get(target_field))
    env["target_field"] = target_field
    env["label"] = labels[0] if labels else ""
    env["labels"] = labels
    env["gold"] = labels
    env["n_gold"] = len(labels)
    env["label_space"] = space.labels if space is not None else []
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


def smoke_test(
    templates: Sequence[Template],
    rows: Sequence[Dict[str, Any]],
    target_field: str,
    space: LabelSpace,
) -> None:
    """Render every template against a few real rows before the full pass.

    Several rows, not one: an mcq_options template on a multi-label row exercises
    a different branch than on a single-label one, and a none-valued row is the
    case that actually breaks positive_label.
    """
    rng = random.Random(0)
    env = new_env()
    for t in templates:
        for row in rows:
            gold = as_labels(row.get(target_field))
            fill_env(env, row, sample_config(t, rng, gold, space), target_field, space)
            try:
                render(t.question, env)
                render(t.answer, env)
            except (ValueError, KeyError) as exc:
                raise ValueError(
                    f"Template {t.template_id} failed its render check on id="
                    f"{row.get('id')!r}: {exc}"
                ) from exc


def generate(
    template_jsonl: str,
    metadata_path: str,
    output_path: str,
    samples_per_entry: int,
    seed: int,
    target_field: str | None,
    label_space_path: str | None,
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

    first_row = next(iter_jsonl(metadata_path), None)
    if first_row is None:
        raise ValueError(f"No metadata entries found in {metadata_path}")
    resolved_field = resolve_target_field(first_row, target_field)

    if label_space_path:
        counts = load_label_space(label_space_path)
    else:
        if verbose:
            print(f"deriving label space from {metadata_path} ...", file=sys.stderr)
        counts = derive_label_space(metadata_path, resolved_field)
    space = LabelSpace(counts)
    if verbose:
        print(f"label space: {len(space):,} labels", file=sys.stderr)

    # Probe rows for the smoke test: the first few that carry a label, plus one
    # empty-labelled row if the manifest has any, so both branches are exercised.
    probes: List[Dict[str, Any]] = []
    empty_probe: Dict[str, Any] | None = None
    for i, row in enumerate(iter_jsonl(metadata_path)):
        if as_labels(row.get(resolved_field)):
            if len(probes) < 3:
                probes.append(row)
        elif empty_probe is None:
            empty_probe = row
        if len(probes) >= 3 and (empty_probe is not None or i > 5000):
            break
    if not probes:
        raise ValueError(f"Every metadata entry has an empty {resolved_field!r}; nothing to generate.")
    smoke_test(templates, probes, resolved_field, space)

    n_entries = n_pairs = n_skipped = 0
    dumps = json.dumps
    env = new_env()

    with open_text(output_path, "wt") as out:
        for row in iter_jsonl(metadata_path):
            if limit is not None and n_entries >= limit:
                break
            gold = as_labels(row.get(resolved_field))
            # An empty target would render as an empty answer, which silently
            # poisons the training set. Skip and report instead.
            if not gold:
                n_skipped += 1
                continue
            n_entries += 1
            for idx in choose_indices(cum_weights, samples_per_entry, rng):
                tpl = templates[idx]
                fill_env(env, row, sample_config(tpl, rng, gold, space), resolved_field, space)
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
            f"WARNING: skipped {n_skipped:,} metadata entr(ies) whose {resolved_field!r} was "
            f"empty or a none-sentinel. If 'none' is a real class for this task, pass "
            f"--none-labels '' so it is treated as a label.",
            file=sys.stderr,
        )
    return n_entries, n_pairs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Instantiate weighted classification QA templates against a metadata "
                    "manifest. Writes JSONL(.gz) rows of {question, answer, metadata}."
    )
    p.add_argument("--template-jsonl", required=True)
    p.add_argument("--metadata", required=True, help="metadata manifest, .jsonl or .jsonl.gz")
    p.add_argument("--output", required=True, help="output path; .gz enables compression")
    p.add_argument("--samples-per-entry", required=True, type=int,
                   help="distinct templates instantiated per metadata entry")
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--target-field", default=None,
                   help="the declared classification target; required when the manifest "
                        "holds more than one label field")
    p.add_argument("--label-space", default=None,
                   help=".txt / .json / *_stats.csv inventory; derived from the manifest "
                        "if omitted")
    p.add_argument("--label-semantics", default=None,
                   help="label_semantics.json; required for Stage 2")
    p.add_argument("--label-separator", default=DEFAULT_LABEL_SEPARATOR,
                   help="separator for multi-label string fields (default ';')")
    p.add_argument("--none-labels", default=",".join(DEFAULT_NONE_LABELS),
                   help="comma-separated values meaning 'no label applies'")
    p.add_argument("--lenient-semantics", action="store_true",
                   help="return None for unmapped labels instead of raising; for drafting only")
    p.add_argument("--no-keep-metadata", dest="keep_metadata", action="store_false",
                   help="store only metadata_id instead of the full metadata row")
    p.add_argument("--limit", type=int, default=None, help="stop after N metadata entries (smoke test)")
    p.add_argument("--quiet", dest="verbose", action="store_false")
    p.set_defaults(keep_metadata=True, verbose=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    configure_labels(
        args.label_separator,
        [x for x in args.none_labels.split(",")] if args.none_labels else [],
    )
    configure_semantics(args.label_semantics, strict=not args.lenient_semantics)
    n_entries, n_pairs = generate(
        template_jsonl=args.template_jsonl,
        metadata_path=args.metadata,
        output_path=args.output,
        samples_per_entry=args.samples_per_entry,
        seed=args.seed,
        target_field=args.target_field,
        label_space_path=args.label_space,
        keep_metadata=args.keep_metadata,
        limit=args.limit,
        verbose=args.verbose,
    )
    if args.verbose:
        print(f"{n_entries:,} metadata entries -> {n_pairs:,} QA pairs written to {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
