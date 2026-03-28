# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. This task extends the standard ASR dataset by adding **time interval constraints** that require models to transcribe only specific temporal segments of the audio. The dataset combines word-level timestamps from Montreal Forced Alignment (MFA) with instruction-following capabilities, enabling research on temporally-aware speech recognition, selective transcription. Models must understand temporal instructions (e.g., "transcribe after 2.5 seconds") and produce accurate transcriptions for the specified intervals.

## Supported Tasks
1. **Instruction-Following ASR (Time-Interval)**

## Dataset Statistics

| Split | # Samples |
|------|-----------|
| train | 25,440 |
| dev | 1,938 |
| test | 1,870 |

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
| `time_interval` | Time constraint as `[start, end]` (in seconds) |
| `text` | Ground-truth transcription for the specified interval |

---

## Example Entries

```json
{"id": "1272-128104-0000", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0000.flac", "sampling_rate": 16000, "duration": "5.855", "dataset": "LibriSpeech", "time_interval": [1.2, -1], "text": "is the apostle of the middle classes, and we are glad to welcome his gospel."}

{"id": "1272-128104-0003", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0003.flac", "sampling_rate": 16000, "duration": "9.900", "dataset": "LibriSpeech", "time_interval": [1.5, 7.2], "text": "whether Sir Frederick Leighton's work is really 'Greek, after all, and can discover in"}

{"id": "1272-128104-0005", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0005.flac", "sampling_rate": 16000, "duration": "9.010", "dataset": "LibriSpeech", "time_interval": [-1, 7.5], "text": "It is obviously unnecessary for us to point out how luminous these criticisms are, how delicate"}
```

---

## Task Usage

### 1. Instruction-Following ASR (Time-Interval)
- **Input fields:** Audio + `time_interval` (temporal constraint)
- **Target field:** `text` (transcription for the specified interval)

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions based on temporal instructions.*

---

## Time Interval Format

The `time_interval` field is a two-element list `[start, end]` specifying the temporal boundaries:

### Three Task Types:

1. **Transcribe After** (50% of samples): `[start_time, -1]`
   - Transcribe all speech starting from `start_time` until the end of audio
   - Example: `[1.2, -1]` means transcribe from 1.2 seconds onward

2. **Transcribe Between** (25% of samples): `[start_time, end_time]`
   - Transcribe speech within the specified interval
   - Example: `[1.5, 7.2]` means transcribe only speech between 1.5 and 7.2 seconds

3. **Transcribe Before** (25% of samples): `[-1, end_time]`
   - Transcribe all speech from the beginning until `end_time`
   - Example: `[-1, 7.5]` means transcribe from start to 7.5 seconds

### Interval Semantics:
- `-1` indicates an unbounded endpoint (beginning or end of audio)
- Times are in seconds with 0.1 second granularity
- Word inclusion is based on word-level timestamps from MFA:
  - For `[start, -1]`: Include words where `word_start >= start`
  - For `[-1, end]`: Include words where `word_end <= end`
  - For `[start, end]`: Include words where `word_start >= start` AND `word_end <= end`

---

## Notes
- All audio files are sampled at **16 kHz**.
- Transcriptions include **proper punctuation** and **mixed case** formatting (preserved from original text).
- Word-level timestamps are obtained from **Montreal Forced Alignment (MFA)** TextGrid files.
- Time intervals use **0.1 second granularity** (rounded to nearest tenth of a second).
- All transcribed segments are **at least 5 seconds long** to ensure meaningful content.
- Task type distribution is deterministic based on sample ID for reproducibility:
  - 50% "transcribe after" tasks
  - 25% "transcribe between" tasks
  - 25% "transcribe before" tasks
- The dataset is derived from LibriSpeech's **clean subsets** only:
  - **train** (`train-clean-100`)
  - **dev** (`dev-clean`)
  - **test** (`test-clean`)
- Silence markers from TextGrid files are filtered out during processing.
- Only samples with valid word-level alignments and sufficient duration are included.
