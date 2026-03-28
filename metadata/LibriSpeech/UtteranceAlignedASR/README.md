# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. This task extends the standard ASR dataset with **utterance-level (sentence-level) timestamps** obtained from Montreal Forced Alignment (MFA). Each sentence in the transcription is paired with its temporal boundaries, enabling research on sentence segmentation, discourse analysis, and coarse-grained temporal modeling of spoken language. Utterances are defined as sentences separated by punctuation marks (periods, question marks, exclamation marks, or semicolons).

## Supported Tasks
1. **Timestamped ASR (Utterance-Level)**

## Dataset Statistics

| Split | # Samples |
|------|-----------|
| train | 81,031 |
| dev | 2,400 |
| test | 2,272 |

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
| `text` | Ground-truth transcription with punctuation |
| `aligned_text` | Utterance-level timestamps in `[start-end] utterance` format |

---

## Example Entries

```json
{"id": "1272-128104-0000", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0000.flac", "sampling_rate": 16000, "duration": "5.855", "dataset": "LibriSpeech", "text": "mister Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.", "aligned_text": "[0.50-5.51] mister Quilter is the apostle of the middle classes, and we are glad to welcome his gospel."}

{"id": "1272-135031-0002", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/135031/1272-135031-0002.flac", "sampling_rate": 16000, "duration": "11.950", "dataset": "LibriSpeech", "text": "Many of his theories have been accepted. He is found, when they are interrogated, to be at the bottom.", "aligned_text": "[0.50-3.78] Many of his theories have been accepted.\n[4.04-11.60] He is found, when they are interrogated, to be at the bottom."}

{"id": "100-121669-0005", "path": "/saltpool0/data/tseng/LibriSpeech/train-clean-360/100/121669/100-121669-0005.flac", "sampling_rate": 16000, "duration": "14.655", "dataset": "LibriSpeech", "text": "under his father's guidance, he fell into bad ways. One morning Tom, Tom, the piper's son, stole a pig and away he run.", "aligned_text": "[0.18-3.71] under his father's guidance, he fell into bad ways.\n[4.69-14.14] One morning Tom, Tom, the piper's son, stole a pig and away he run."}
```

---

## Task Usage

### 1. Timestamped ASR (Utterance-Level)
- **Target field:** `aligned_text` (utterance-level timestamps)

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions with utterance-level temporal alignments.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Utterance-level timestamps are computed from word-level alignments using **Montreal Forced Alignment (MFA)** TextGrid files.
- The `aligned_text` field contains each utterance (sentence) with its temporal boundaries in the format:
  ```
  [start-end] utterance
  ```
  where `start` is the beginning of the first word and `end` is the end of the last word in the utterance.
- Multiple utterances within a single audio file are separated by newline characters (`\n`).
- Utterances are defined by sentence-ending punctuation marks:
  - Period (`.`)
  - Question mark (`?`)
  - Exclamation mark (`!`)
  - Semicolon (`;`)
- Transcriptions include **proper punctuation** and **mixed case** formatting (derived from LibriSpeech-PC).
- Timestamps use 2 decimal precision (e.g., `0.50`, `5.51`).
- Only samples containing sentence-ending punctuation are included (samples without punctuation are filtered out).
- The dataset is derived from LibriSpeech's **clean subsets** with punctuation restored:
  - **train** (`train-clean-360`)
  - **dev** (`dev-clean`)
  - **test** (`test-clean`)