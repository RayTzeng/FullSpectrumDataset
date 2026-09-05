#!/usr/bin/env python3
"""Canonicalise GLOBE's free-text `accent` field into a closed 17-label space.

GLOBE copies Mozilla Common Voice's self-reported accent field verbatim. That
field is a comma-joined mix of the 16 checkbox varieties the Common Voice
profile form offers for English and arbitrary free text the contributor typed,
so a single row can read

    "united states english,midwestern,low,demure"

The comma is not a clean separator: it also appears *inside* two of the
checkbox labels ("india and south asia (india, pakistan, sri lanka)"), so the
split here is parenthesis-aware and never splits inside brackets.

Each row is reduced to the set of canonical labels among its tags. A row is
kept only when exactly one canonical label survives; rows resolving to none
(pure free text) or to two or more (contributors who ticked several boxes) are
dropped, because neither yields a defensible single-label target. Free-text
tags that sit alongside a canonical label are annotator commentary about a
sub-variety, not a competing class, and are discarded.

`accent` is overwritten with the canonical label so the shipped generator can
read it directly; the untouched original is preserved as `accent_raw`.

    python3 prepare_manifest.py --metadata .../train.jsonl.gz \
        --output train.jsonl.gz --per-class-cap 45000
"""
import argparse, collections, gzip, hashlib, json, sys

# The 16 accent options Common Voice's English profile form offers, spelled
# exactly as GLOBE stores them. Do not normalise the spelling: the README is
# explicit that manifest strings are the label names.
CV_CHECKBOX = [
    "united states english",
    "england english",
    "india and south asia (india, pakistan, sri lanka)",
    "canadian english",
    "australian english",
    "southern african (south africa, zimbabwe, namibia)",
    "northern irish",
    "irish english",
    "new zealand english",
    "scottish english",
    "filipino",
    "hong kong english",
    "singaporean english",
    "malaysian english",
    "welsh english",
    "west indies and bermuda (bahamas, bermuda, jamaica, trinidad)",
]

# A 17th class, promoted from free text: German-accented English is the only
# non-checkbox variety with enough rows in every split to be learnable and
# evaluable. Merged from the spelling variants contributors actually typed.
# Biographical free text ("born in west germany in 1966", "speak some german")
# is deliberately excluded -- it is not a claim about the speaker's accent.
GERMAN_ENGLISH = "german english"
GERMAN_VARIANTS = {
    "german english", "german", "german accent", "germany english",
    "german native speaker", "german native", "austrian",
    "south german accent", "south-west german", "alemannic german accent",
    "south german / swiss accent", "english with swiss german accent",
}

CANON = {t: t for t in CV_CHECKBOX}
CANON.update({v: GERMAN_ENGLISH for v in GERMAN_VARIANTS})
LABELS = CV_CHECKBOX + [GERMAN_ENGLISH]


def split_tags(value: str):
    """Comma-split that never splits inside parentheses.

    "india and south asia (india, pakistan, sri lanka)" is one tag, while
    "non native speaker,german english" is two.
    """
    out, depth, cur = [], 0, ""
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return [t for t in out if t]


def canonical(value: str):
    """The row's single canonical label, or None if it has zero or several."""
    hits = {CANON[t] for t in split_tags(value.lower()) if t in CANON}
    return hits.pop() if len(hits) == 1 else None


def rank(clip_id: str) -> str:
    """Deterministic per-clip ordering key, so a cap keeps the same rows."""
    return hashlib.md5(clip_id.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--target-field", default="accent")
    ap.add_argument("--id-field", default="id")
    ap.add_argument("--per-class-cap", type=int, default=0,
                    help="keep at most N rows per label (0 = keep all); the kept "
                         "rows are the N with the lowest md5(id), so the choice is "
                         "reproducible and independent of file order")
    args = ap.parse_args()

    field = args.target_field
    kept_ids, dropped = None, collections.Counter()
    per_class = collections.Counter()

    if args.per_class_cap:
        by_label = collections.defaultdict(list)
        with gzip.open(args.metadata, "rt") as src:
            for line in src:
                if not line.strip():
                    continue
                row = json.loads(line)
                lab = canonical(row.get(field, ""))
                if lab is not None:
                    by_label[lab].append(str(row[args.id_field]))
        kept_ids = set()
        for lab, ids in by_label.items():
            ids.sort(key=rank)
            kept_ids.update(ids[: args.per_class_cap])

    written = 0
    with gzip.open(args.output, "wt") as out, gzip.open(args.metadata, "rt") as src:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            raw = row.get(field, "")
            lab = canonical(raw)
            if lab is None:
                n = len({CANON[t] for t in split_tags(raw.lower()) if t in CANON})
                dropped["no canonical label" if n == 0 else "several canonical labels"] += 1
                continue
            if kept_ids is not None and str(row[args.id_field]) not in kept_ids:
                dropped["over per-class cap"] += 1
                continue
            row["accent_raw"] = raw
            row[field] = lab
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            per_class[lab] += 1
            written += 1

    print(f"wrote {written:,} rows -> {args.output}")
    for reason, n in dropped.most_common():
        print(f"  dropped {n:,}: {reason}")
    print(f"  {len(per_class)} labels present")
    for lab in LABELS:
        n = per_class[lab]
        flag = "  <-- ABSENT" if n == 0 else ""
        print(f"    {n:8,}  {100*n/max(written,1):5.2f}%  {lab}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
