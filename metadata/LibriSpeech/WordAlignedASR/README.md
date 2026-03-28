# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. This task extends the standard ASR dataset with **word-level timestamps** obtained from Montreal Forced Alignment (MFA). Each word in the transcription is paired with precise start and end times, enabling research on word-level speech segmentation, alignment quality assessment, and fine-grained temporal analysis of spoken language.

## Supported Tasks
1. **Timestamped ASR (Word-Level)**
2. **Force Alignment**

## Dataset Statistics

| Split | # Samples |
|------|-----------|
| train | 87,290 |
| dev | 2,364 |
| test | 2,201 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `text` | Ground-truth transcription |
| `aligned_text` | Word-level timestamps in `[start-end] word` format |

---

## Example Entries

```json
{"id": "1272-128104-0000", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0000.flac", "duration": "5.855", "dataset": "LibriSpeech", "text": "mister Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.", "sampling_rate": 16000, "aligned_text": "[0.50-0.80] mister\n[0.80-1.27] quilter\n[1.27-1.40] is\n[1.40-1.52] the\n[1.52-2.15] apostle\n[2.15-2.27] of\n[2.27-2.35] the\n[2.35-2.62] middle\n[2.62-3.27] classes\n[3.30-3.45] and\n[3.45-3.60] we\n[3.60-3.67] are\n[3.67-4.07] glad\n[4.07-4.20] to\n[4.20-4.60] welcome\n[4.60-4.84] his\n[4.84-5.51] gospel"}

{"id": "1272-128104-0001", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0001.flac", "duration": "4.815", "dataset": "LibriSpeech", "text": "Nor is mister Quilter's manner less interesting than his matter.", "sampling_rate": 16000, "aligned_text": "[0.50-0.88] nor\n[0.88-1.08] is\n[1.08-1.36] mister\n[1.36-1.71] quilter\n[1.71-1.82] s\n[1.82-2.28] manner\n[2.28-2.61] less\n[2.61-3.28] interesting\n[3.28-3.51] than\n[3.51-3.85] his\n[3.85-4.39] matter"}
```

---

## Task Usage

### 1. Timestamped ASR (Word-Level)
- **Target field:** `aligned_text` (word-level timestamps)
### 2. Force Alignment
- **Target field:** `aligned_text` (word-level timestamps), while providing the `text` field as reference transcription for alignment evaluation.
---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions with word-level temporal alignments.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Word-level timestamps are obtained using **Montreal Forced Alignment (MFA)** from TextGrid files.
- The `aligned_text` field contains each word with its temporal boundaries in the format:
  ```
  [start-end] word
  ```
  where `start` and `end` are timestamps in seconds with 2 decimal precision.
- Words are separated by newline characters (`\n`) in the `aligned_text` field.
- Transcriptions are in **lowercase** (as processed by MFA).
- Contractions and possessives are split (e.g., "Quilter's" becomes "quilter" + "s").
- Silence markers from TextGrid files are filtered out.
- The dataset is derived from LibriSpeech's **clean subsets** only:
  - **train** (`train-clean-360`)
  - **dev** (`dev-clean`)
  - **test** (`test-clean`)