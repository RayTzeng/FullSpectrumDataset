#!/usr/bin/env python3
"""Split an NSynth manifest into disjoint Stage-1 and Stage-2 parts.

Two thirds of the clips are routed to Stage-1 and the remaining third to
Stage-2, so no clip carries both a Stage-1 and a Stage-2 question. The routing
is a deterministic md5 of the clip id, so the same clip always lands in the
same part regardless of split, machine, or run order.

    python3 partition_manifest.py --metadata train.jsonl.gz --outdir parts/
"""
import argparse, gzip, hashlib, json, os


def route(clip_id: str) -> int:
    """0 -> stage 1, 1 -> stage 2. Two thirds of ids map to 0."""
    digest = hashlib.md5(clip_id.encode("utf-8")).hexdigest()
    return 0 if int(digest, 16) % 3 < 2 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--id-field", default="id")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    split = os.path.basename(args.metadata).split(".")[0]
    paths = [os.path.join(args.outdir, f"{split}_stage{n}.jsonl.gz") for n in (1, 2)]
    counts = [0, 0]

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

    total = sum(counts) or 1
    print(f"{split}: {total} clips -> stage1 {counts[0]} ({100*counts[0]/total:.1f}%), "
          f"stage2 {counts[1]} ({100*counts[1]/total:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
