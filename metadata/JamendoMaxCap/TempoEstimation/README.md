# JamendoMaxCap - Tempo Estimation

## Overview
**JamendoMaxCap** is a large-scale music dataset built from Jamendo tracks paired with rich text captions generated from automated music analysis. This task provides a tempo estimation benchmark, where models predict the continuous tempo of a music clip. Audio clips are 30 seconds long and sampled at **16 kHz**.

Tempo labels are produced by **DeepRhythm**, a CNN tempo estimator run directly on the audio (see `extract_tempo.py` and `deeprhythm/`). Each estimate carries a `confidence` score, and the released splits keep only clips the estimator was confident about.

## Supported Tasks
1. **Tempo Estimation**

---

## Dataset Statistics

| Split | # Clips | # Source tracks |
|-------|--------:|----------------:|
| train | 83,166 | 66,705 |
| test | 1,000 | 789 |

Both splits are drawn from `train_0.jsonl.gz` + `train_1.jsonl.gz` (170,452 rows, 170,436 distinct clip ids) after filtering to `confidence >= 0.7`, which retains 84,166 clips (49.4%).

The split is **track-disjoint**. Clip ids have the form `<track>_<offset>`, and 31.2% of source tracks contribute more than one 30-second excerpt (up to 5). Whole tracks are assigned to one side, so no song appears in both splits.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|-------|-------------|
| `id` | Unique clip ID, formatted `<track>_<offset>` |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`JamendoMaxCaps`) |
| `tempo` | Tempo in beats per minute (DeepRhythm estimate, integer-valued) |
| `confidence` | DeepRhythm confidence for that estimate, 0-1 |

---

## Example Entries

```json
{"id": "1038270_opening_30s", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/1038270.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "tempo": 107.0, "confidence": 0.8608205318450928}

{"id": "1720726_30", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_2/wavs/1720726_30.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "tempo": 120.0, "confidence": 0.9906381964683533}

{"id": "1097054_opening_30s", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/1097054.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "tempo": 129.0, "confidence": 0.9880560636520386}
```

---

## Task Usage

### 1. Tempo Estimation
- **Target field:** `tempo` (tempo in beats per minute)

---

## Label Space

### Tempo (BPM)

| | train | test |
|---|---:|---:|
| Range | 60 - 245 | 78 - 153 |
| Mean | 113.4 | 114.0 |
| Median | 120 | 120 |
| Std. dev. | 19.3 | 19.0 |
| IQR | 97 - 128 | 95 - 128 |
| Mean confidence | 0.901 | 0.905 |

- **Type**: Continuous regression task; stored values are whole numbers of BPM
- **Interpretation** (bands used by the QA templates):

| Band | Rule | train | test |
|---|---|---:|---:|
| Slow | < 80 BPM | 0.74% | 1.00% |
| Medium | 80-120 BPM | 63.30% | 62.70% |
| Fast | > 120 BPM | 35.96% | 36.30% |

The distribution is strongly modal: 120 BPM alone accounts for ~21% of clips, and the top 20 values cover 82.8%. Support is dense over the integers 78-150.

---

## Files

| File | Contents |
|---|---|
| `train.jsonl.gz` | 83,166 clips, `tempo` + `confidence`, confidence >= 0.7 |
| `test.jsonl.gz` | 1,000 clips, track-disjoint from train |
| `train_0.jsonl.gz`, `train_1.jsonl.gz` | Raw DeepRhythm shards, unfiltered (85,226 rows each) |
| `build_splits.py` | Merges the shards, dedups, filters by confidence, writes the splits |
| `extract_tempo.py`, `deeprhythm/` | DeepRhythm inference used to produce the shards |
| `generate_manifest.py` | Legacy: builds caption-derived BPM manifests |
| `train_caption_bpm.jsonl.gz`, `test_caption_bpm.jsonl.gz` | Legacy caption-derived labels, superseded (see Notes) |
| `test_out.jsonl.gz` | DeepRhythm rerun of the 21-clip legacy test set |

Reproduce the splits with:

```bash
python3 build_splits.py --min-confidence 0.7 --test-size 1000 --seed 0
```

---

## Notes
- All audio files are sampled at **16 kHz** in WAV format.
- Audio clips are typically **30 seconds** in duration.
- Tempo is estimated by DeepRhythm from the audio signal. Clips with `confidence < 0.7` are excluded from the released splits; the unfiltered shards remain available in `train_{0,1}.jsonl.gz`.
- The dataset has a strong bias toward medium tempo music (~63% of clips fall in 80-120 BPM), and fewer than 1% fall below 80 BPM.
- **Superseded labels.** An earlier version of this task stored a `bpm` field extracted from JamendoMaxCap caption text by regex (e.g. "tempo of around 125 BPM"). Those manifests are kept as `train_caption_bpm.jsonl.gz` (568,115 rows) and `test_caption_bpm.jsonl.gz` (21 rows). On the 135,906 clips covered by both sources the two labels agree within 4% only 37.6% of the time (51.4% among DeepRhythm estimates at confidence >= 0.7), so they are not interchangeable. The caption labels are not used by the current splits.
