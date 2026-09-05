#!/usr/bin/env python3
"""Split a canonicalised GLOBE manifest into disjoint Stage-1 and Stage-2 parts.

Three quarters of the clips are routed to Stage-1 and the remaining quarter to
Stage-2, so no clip carries both a Stage-1 and a Stage-2 question. The routing
is a deterministic md5 of the clip id, so the same clip always lands in the
same part regardless of split, machine, or run order.

    python3 partition_manifest.py --metadata train.jsonl.gz --outdir parts/
"""
import argparse, collections, gzip, hashlib, json, os


def route(clip_id: str) -> int:
    """0 -> stage 1, 1 -> stage 2. Three quarters of ids map to 0."""
    digest = hashlib.md5(clip_id.encode("utf-8")).hexdigest()
    return 0 if int(digest, 16) % 4 < 3 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--id-field", default="id")
    ap.add_argument("--target-field", default="accent")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    split = os.path.basename(args.metadata).split(".")[0]
    paths = [os.path.join(args.outdir, f"{split}_stage{n}.jsonl.gz") for n in (1, 2)]
    counts = [0, 0]
    by_label = [collections.Counter(), collections.Counter()]

    with gzip.open(paths[0], "wt") as f1, gzip.open(paths[1], "wt") as f2:
        handles = (f1, f2)
        with gzip.open(args.metadata, "rt") as src:
            for line in src:
                if not line.strip():
                    continue
                row = json.loads(line)
                part = route(str(row[args.id_field]))
                handles[part].write(line if line.endswith("\n") else line + "\n")
                counts[part] += 1
                by_label[part][row.get(args.target_field)] += 1

    total = sum(counts) or 1
    print(f"{split}: {total:,} clips -> stage1 {counts[0]:,} ({100*counts[0]/total:.1f}%), "
          f"stage2 {counts[1]:,} ({100*counts[1]/total:.1f}%)")
    # An id scheme that encodes the label can correlate a weak hash with the
    # class, so check the label distribution actually survives the routing.
    print(f"  {'label':62s} {'stage1 %':>9s} {'stage2 %':>9s}")
    worst = 0.0
    for lab in sorted(set(by_label[0]) | set(by_label[1])):
        p1 = 100 * by_label[0][lab] / max(counts[0], 1)
        p2 = 100 * by_label[1][lab] / max(counts[1], 1)
        worst = max(worst, abs(p1 - p2))
        print(f"  {lab:62s} {p1:8.2f}% {p2:8.2f}%")
    print(f"  largest share drift between parts: {worst:.2f} pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
