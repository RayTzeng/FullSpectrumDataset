# JamendoMaxCap - Tempo Estimation

## Overview
**JamendoMaxCap** is a large-scale music dataset built from Jamendo tracks paired with rich text captions generated from automated music analysis. This task extracts **BPM (beats per minute)** values from those captions to form a tempo estimation benchmark, where models predict the continuous tempo of a music clip. Audio clips are 30 seconds long and sampled at **16 kHz**.

## Supported Tasks
1. **Tempo Estimation**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 568,115 |
| test | 21 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|-------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`JamendoMaxCaps`) |
| `bpm` | Tempo in beats per minute (continuous float) |

---

## Example Entries

```json
{"id": "1748883_90", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_2/wavs/1748883_90.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "bpm": 80.0}

{"id": "695133_opening_30s", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/695133.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "bpm": 130.0}

{"id": "316929_360", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_3/wavs/316929_360.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "bpm": 89.0}
```

---

## Task Usage

### 1. Tempo Estimation
- **Target field:** `bpm` (continuous tempo value in beats per minute)

---

## Label Space

### BPM (Tempo)
- **Range**: 20.0 to 300.0 BPM (training set)
- **Type**: Continuous regression task
- **Mean**: ~104.4 BPM, **Median**: ~105.3 BPM
- **Interpretation**:
  - **Slow** (<90 BPM): 35.4% of training data
  - **Medium** (90–140 BPM): 60.9% of training data
  - **Fast** (>140 BPM): 3.6% of training data

---

## Notes
- All audio files are sampled at **16 kHz** in WAV format.
- Audio clips are typically **30 seconds** in duration.
- BPM values are extracted from JamendoMaxCap caption text via regex (e.g., "tempo of around 125 BPM"), not from signal processing.
- Only clips whose captions contained an extractable BPM value are included (79.5% coverage of source training data).
- The dataset has a strong bias toward medium tempo music (~61% of training samples fall in 90–140 BPM).
- The test set is small (21 samples) and covers only 60–139.5 BPM; do not draw conclusions about fast-tempo performance from it.
