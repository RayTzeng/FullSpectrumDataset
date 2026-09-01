#!/usr/bin/env python3
"""Generate CS-FLEURS manifests and recopy selected audio files.

This script:
1. Loads the Hugging Face dataset `byan/cs-fleurs`
2. Keeps only:
   - `xtts/train` samples for the `train` manifest
   - `xtts/test1` samples for the `test` manifest
3. Copies audio into:
   - `/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/train`
   - `/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/test`
4. Writes compressed JSONL manifests with fields:
   `id`, `path`, `sampling_rate`, `duration`, `dataset`, `language`, `text`

Example:
    python3 generate_manifest.py --splits train --max-samples 100
"""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from datasets import Audio, load_dataset
from tqdm import tqdm


BASE_DIR = Path("/saltpool0/data/tseng/FullSpectrumDataset")
METADATA_DIR = BASE_DIR / "metadata" / "CS-FLEURS"
CORPUS_DIR = BASE_DIR / "corpus" / "CS-FLEURS"
DATASET_NAME = "byan/cs-fleurs"
MANIFEST_FIELDS = ("id", "path", "sampling_rate", "duration", "dataset", "language", "text")
SPLIT_PATH_FILTERS = {
    "train": "xtts/train",
    "test": "xtts/test1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CS-FLEURS manifests and copy selected audio files."
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=sorted(SPLIT_PATH_FILTERS),
        default=["train", "test"],
        help="Dataset splits to process.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Process at most this many matched samples per split after filtering.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start from this raw Hugging Face split index. Useful for spot checks.",
    )
    parser.add_argument(
        "--overwrite-audio",
        action="store_true",
        help="Overwrite copied audio files if they already exist.",
    )
    parser.add_argument(
        "--overwrite-manifest",
        action="store_true",
        help="Overwrite manifest files if they already exist.",
    )
    parser.add_argument(
        "--skip-copy",
        action="store_true",
        help="Do not copy audio files. Useful for faster dry-run testing.",
    )
    parser.add_argument(
        "--dataset-name",
        default=DATASET_NAME,
        help="Hugging Face dataset name to load.",
    )
    return parser.parse_args()


def get_audio_info(audio_path: Path) -> Tuple[Optional[int], Optional[float]]:
    """Return (sampling_rate, duration) from ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=sample_rate",
                "-of",
                "json",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("ffprobe is required but was not found in PATH.") from exc
    except subprocess.CalledProcessError:
        return None, None

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, None

    duration = None
    if "format" in payload and "duration" in payload["format"]:
        try:
            duration = float(payload["format"]["duration"])
        except (TypeError, ValueError):
            duration = None

    sampling_rate = None
    for stream in payload.get("streams", []):
        sample_rate = stream.get("sample_rate")
        if sample_rate is None:
            continue
        try:
            sampling_rate = int(sample_rate)
            break
        except (TypeError, ValueError):
            continue

    return sampling_rate, duration


def make_destination_path(split: str, sample_id: str, source_path: Path) -> Path:
    suffix = "".join(source_path.suffixes) or ".wav"
    safe_id = sample_id.replace("/", "_")
    return CORPUS_DIR / "audio" / split / f"{safe_id}{suffix}"


def copy_audio(source_path: Path, destination_path: Path, overwrite: bool) -> str:
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    if destination_path.exists() and not overwrite:
        return "reused"

    shutil.copy2(source_path, destination_path)
    return "copied"


def build_record(sample: dict, audio_path: Path) -> dict:
    sampling_rate, probed_duration = get_audio_info(audio_path)
    fallback_duration = float(sample.get("duration", 0.0))

    if sampling_rate is None:
        raise RuntimeError(f"Could not determine sampling rate for {audio_path}")

    record = {
        "id": str(sample["id"]),
        "path": str(audio_path),
        "sampling_rate": sampling_rate,
        "duration": probed_duration if probed_duration is not None else fallback_duration,
        "dataset": "CS-FLEURS",
        "language": str(sample["language"]),
        "text": str(sample["text"]),
    }

    return record


def process_split(
    hf_dataset,
    split: str,
    max_samples: Optional[int],
    start_index: int,
    overwrite_audio: bool,
    overwrite_manifest: bool,
    skip_copy: bool,
) -> None:
    if split not in hf_dataset:
        raise KeyError(f"Hugging Face dataset does not contain split '{split}'")

    raw_split = hf_dataset[split]
    path_filter = SPLIT_PATH_FILTERS[split]
    output_manifest = METADATA_DIR / f"{split}.jsonl.gz"
    output_manifest.parent.mkdir(parents=True, exist_ok=True)

    if output_manifest.exists() and not overwrite_manifest:
        raise FileExistsError(
            f"{output_manifest} already exists. Use --overwrite-manifest to replace it."
        )

    processed = 0
    skipped_path = 0
    missing_audio = 0
    copied = 0
    reused = 0

    total = max(len(raw_split) - start_index, 0)
    progress = tqdm(
        range(start_index, len(raw_split)),
        total=total,
        desc=f"Processing {split}",
    )

    with gzip.open(output_manifest, "wt", encoding="utf-8") as fout:
        for index in progress:
            sample = raw_split[index]
            audio_info = sample.get("audio") or {}
            source_path_str = audio_info.get("path")

            if not source_path_str or path_filter not in source_path_str:
                skipped_path += 1
                continue

            source_path = Path(source_path_str)
            if not source_path.is_file():
                missing_audio += 1
                continue

            destination_path = make_destination_path(split, str(sample["id"]), source_path)
            if not skip_copy:
                copy_status = copy_audio(source_path, destination_path, overwrite_audio)
                if copy_status == "copied":
                    copied += 1
                else:
                    reused += 1

            manifest_audio_path = source_path if skip_copy else destination_path
            record = build_record(sample, manifest_audio_path)
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            processed += 1

            progress.set_postfix(
                kept=processed,
                skipped=skipped_path,
                missing=missing_audio,
            )

            if max_samples is not None and processed >= max_samples:
                break

    print(
        json.dumps(
            {
                "split": split,
                "manifest": str(output_manifest),
                "processed": processed,
                "skipped_path_filter": skipped_path,
                "missing_audio": missing_audio,
                "copied_audio": copied,
                "reused_audio": reused,
                "path_filter": path_filter,
                "fields": list(MANIFEST_FIELDS),
            },
            ensure_ascii=False,
        )
    )


def main() -> None:
    args = parse_args()

    dataset = load_dataset(args.dataset_name)
    dataset = dataset.cast_column("audio", Audio(decode=False))

    for split in args.splits:
        process_split(
            hf_dataset=dataset,
            split=split,
            max_samples=args.max_samples,
            start_index=args.start_index,
            overwrite_audio=args.overwrite_audio,
            overwrite_manifest=args.overwrite_manifest,
            skip_copy=args.skip_copy,
        )


if __name__ == "__main__":
    main()
