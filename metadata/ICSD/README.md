# ICSD

## Overview
**ICSD** (Infant Cry and Snoring Detection) is an open benchmark dataset for detecting infant crying and snoring events, designed to support sound event detection research in realistic caregiving scenarios. The dataset includes **real strongly labeled data**, **weakly labeled clips**, and **synthetic strongly labeled data**, providing over **40 hours** of annotated audio for robust model training and evaluation.

## Supported Tasks
1. **Infant Cry and Snoring Detection**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 12,284 |
| dev | 1,082 |
| test | 1,082 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `infant_sound` | Ground-truth infant sound label |

---

## Example Entries

```json
{"id": "synth_trainval_Infantcry_860", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/ICSD/audio/train/synth_strong_train/synth_trainval_Infantcry_860.wav", "sampling_rate": 16000, "duration": 10.0, "dataset": "ICSD", infant_sound: "crying"}

{"id": "weak_Snoring_641", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/ICSD/audio/train/weak/weak_Snoring_641.wav", "sampling_rate": 16000, "duration": 10.0, "dataset": "ICSD", infant_sound: "snoring"}

{"id": "synth_trainval_Infantcry_2494", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/ICSD/audio/train/synth_strong_train/synth_trainval_Infantcry_2494.wav", "sampling_rate": 16000, "duration": 10.0, "dataset": "ICSD", infant_sound: "crying"}
```

---

## Task Usage

### 1. Infant Cry and Snoring Detection
- **Target field:** `infant_sound` (infant sound label)

---

## Label Space

### Infant Sound Labels
<details>
<summary>Show 2 available labels:</summary>

`crying`, `snoring`

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Each clip is approximately **10 seconds** long.
- The training set includes three types of data:
  - **Real strongly labeled data** (643 files): Real recordings with temporal annotations
  - **Synthetic strongly labeled data** (8,000 files): Synthesized audio with temporal annotations
  - **Weakly labeled clips** (3,641 files): Real recordings with clip-level labels only
- The development set contains **1,082 real strongly labeled files**.
- The test set contains **82 real** and **1,000 synthetic** strongly labeled files.
- This is a **single-label** classification task focused on detecting infant crying and snoring events.
- The dataset is designed for **realistic caregiving scenarios**, making it suitable for applications in baby monitoring and health monitoring systems.
- For files with temporal annotations (strong labels), the most frequent event in each clip is used as the file-level label.
