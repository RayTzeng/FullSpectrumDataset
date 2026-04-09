#!/usr/bin/env python3
"""
Generate manifest files for MusicEval dataset.

MusicEval is a generative music evaluation dataset with MOS scores for:
1. Overall musical impression (quality)
2. Alignment with text prompts

Two types of manifests are generated:
1. Quality manifest: {"id", "path", "sampling_rate", "duration", "dataset", "quality_MOS"}
2. Alignment manifest: {"id", "path", "sampling_rate", "duration", "dataset", "prompt", "alignment_MOS"}
"""

import json
import gzip
import os
from pathlib import Path
import subprocess
from tqdm import tqdm


def get_audio_info(audio_path):
    """Get audio sampling rate and duration using soxi."""
    try:
        # Get duration
        duration_result = subprocess.run(
            ['soxi', '-D', audio_path],
            capture_output=True,
            text=True,
            check=True
        )
        duration = float(duration_result.stdout.strip())

        # Get sampling rate
        rate_result = subprocess.run(
            ['soxi', '-r', audio_path],
            capture_output=True,
            text=True,
            check=True
        )
        sampling_rate = int(rate_result.stdout.strip())

        return sampling_rate, duration
    except Exception as e:
        print(f"Warning: Could not get audio info for {audio_path}: {e}")
        return None, None


def load_prompts(prompt_file):
    """Load prompt information from prompt_info.txt."""
    prompts = {}
    with open(prompt_file, 'r', encoding='utf-8') as f:
        # Skip header
        next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                prompt_id, text = parts
                prompts[prompt_id] = text
    return prompts


def process_musiceval_split(mos_file, audio_dir, prompts, output_quality_path, output_alignment_path, split_name):
    """
    Process MusicEval MOS file and generate two types of manifests.

    Args:
        mos_file: Path to train/dev/test_mos_list.txt
        audio_dir: Path to wav directory
        prompts: Dictionary of prompt_id -> prompt_text
        output_quality_path: Output path for quality manifest
        output_alignment_path: Output path for alignment manifest
        split_name: 'train', 'dev', or 'test'
    """
    print(f"Processing {split_name} split...")
    print(f"  MOS file: {mos_file}")
    print(f"  Audio dir: {audio_dir}")

    quality_entries = []
    alignment_entries = []
    missing_audio = 0
    missing_prompt = 0

    # Read MOS file
    with open(mos_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"  Total entries in MOS file: {len(lines)}")

    for line in tqdm(lines, desc=f"  Processing {split_name}"):
        parts = line.split(',')
        if len(parts) != 3:
            continue

        filename, quality_mos, alignment_mos = parts
        quality_mos = float(quality_mos)
        alignment_mos = float(alignment_mos)

        # Extract system ID and prompt ID from filename
        # Format: audiomos2025-track1-S001_P001.wav
        audio_id = filename.replace('.wav', '')
        base_name = audio_id.replace('audiomos2025-track1-', '')

        # Extract system and prompt IDs
        system_id, prompt_id = base_name.split('_')

        # Get audio path
        audio_path = audio_dir / filename

        if not audio_path.exists():
            missing_audio += 1
            continue

        # Get audio info
        sampling_rate, duration = get_audio_info(str(audio_path))
        if sampling_rate is None or duration is None:
            missing_audio += 1
            continue

        # Get prompt text
        prompt_text = prompts.get(prompt_id, "")
        if not prompt_text:
            missing_prompt += 1

        # Create quality manifest entry
        quality_entry = {
            "id": audio_id,
            "path": str(audio_path.absolute()),
            "sampling_rate": sampling_rate,
            "duration": duration,
            "dataset": "MusicEval",
            "quality_MOS": quality_mos
        }
        quality_entries.append(quality_entry)

        # Create alignment manifest entry
        alignment_entry = {
            "id": audio_id,
            "path": str(audio_path.absolute()),
            "sampling_rate": sampling_rate,
            "duration": duration,
            "dataset": "MusicEval",
            "prompt": prompt_text,
            "alignment_MOS": alignment_mos
        }
        alignment_entries.append(alignment_entry)

    if missing_audio > 0:
        print(f"  Warning: {missing_audio} audio files not found or inaccessible")
    if missing_prompt > 0:
        print(f"  Warning: {missing_prompt} prompts not found")

    # Sort by ID for consistency
    quality_entries.sort(key=lambda x: x['id'])
    alignment_entries.sort(key=lambda x: x['id'])

    # Write quality manifest
    print(f"Writing {len(quality_entries)} entries to {output_quality_path}")
    with gzip.open(output_quality_path, 'wt', encoding='utf-8') as f:
        for entry in quality_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # Write alignment manifest
    print(f"Writing {len(alignment_entries)} entries to {output_alignment_path}")
    with gzip.open(output_alignment_path, 'wt', encoding='utf-8') as f:
        for entry in alignment_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"✓ {split_name} manifests created successfully!\n")


def main():
    # Paths
    base_dir = Path('/saltpool0/data/tseng/FullSpectrumDataset')
    corpus_dir = base_dir / 'corpus' / 'MusicEval' / 'MusicEval-full'
    audio_dir = corpus_dir / 'wav'
    sets_dir = corpus_dir / 'sets'
    metadata_dir = base_dir / 'metadata' / 'MusicEval'

    # Create metadata directory if it doesn't exist
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # Load prompts
    print("Loading prompts...")
    prompts = load_prompts(corpus_dir / 'prompt_info.txt')
    print(f"  Loaded {len(prompts)} prompts\n")

    # Process train set
    process_musiceval_split(
        mos_file=sets_dir / 'train_mos_list.txt',
        audio_dir=audio_dir,
        prompts=prompts,
        output_quality_path=metadata_dir / 'train_quality.jsonl.gz',
        output_alignment_path=metadata_dir / 'train_alignment.jsonl.gz',
        split_name='train'
    )

    # Process dev set
    process_musiceval_split(
        mos_file=sets_dir / 'dev_mos_list.txt',
        audio_dir=audio_dir,
        prompts=prompts,
        output_quality_path=metadata_dir / 'dev_quality.jsonl.gz',
        output_alignment_path=metadata_dir / 'dev_alignment.jsonl.gz',
        split_name='dev'
    )

    # Process test set
    process_musiceval_split(
        mos_file=sets_dir / 'test_mos_list.txt',
        audio_dir=audio_dir,
        prompts=prompts,
        output_quality_path=metadata_dir / 'test_quality.jsonl.gz',
        output_alignment_path=metadata_dir / 'test_alignment.jsonl.gz',
        split_name='test'
    )

    print("All manifests generated successfully!")
    print("\nGenerated files:")
    print("  Quality manifests: train_quality.jsonl.gz, dev_quality.jsonl.gz, test_quality.jsonl.gz")
    print("  Alignment manifests: train_alignment.jsonl.gz, dev_alignment.jsonl.gz, test_alignment.jsonl.gz")


if __name__ == '__main__':
    main()
