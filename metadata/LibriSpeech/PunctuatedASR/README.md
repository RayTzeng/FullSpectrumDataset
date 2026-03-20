# LibriSpeech-PC

## Overview
**LibriSpeech-PC** is a punctuated version of LibriSpeech where punctuation is restored in the transcripts. This dataset is used for training and evaluating models on punctuated automatic speech recognition, requiring models to transcribe speech while restoring proper punctuation marks such as commas and periods.

## Supported Tasks
1. **Punctuated Automatic Speech Recognition**

## Dataset Statistics

| Split | # Samples |
|------|-----------|
| train | 250,590 |
| dev | 5,152 |
| test | 5,152 |

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

---

## Example Entries

```json
{"id": "8590-258292-0039", "path": "/saltpool0/data/tseng/LibriSpeech/train-other-500/8590/258292/8590-258292-0039.flac", "duration": "15.105", "dataset": "LibriSpeech", "text": "They replied, O King of the Age, there remain nor ships nor boats nor those who were therein for they are all drowned and become food for fishes. Now when he heard this, he cried aloud", "sampling_rate": 16000}

{"id": "7552-87290-0057", "path": "/saltpool0/data/tseng/LibriSpeech/train-other-500/7552/87290/7552-87290-0057.flac", "duration": "13.080", "dataset": "LibriSpeech", "text": "At this the men all laughed, and were very impertinent in the free and easy manner of such gentry, most of whom were professional adventurers, with every finer sense dulled and debased by years of vice.", "sampling_rate": 16000}

{"id": "2514-149482-0106", "path": "/saltpool0/data/tseng/LibriSpeech/train-clean-100/2514/149482/2514-149482-0106.flac", "duration": "15.435", "dataset": "LibriSpeech", "text": "yet Densher might even then have felt them in the air. They were practically in it already when Kate, waiving the question of her friend's chemical change, wound up with the comparatively unobjectionable proposition that he must now, having missed so much,", "sampling_rate": 16000}
```

---

## Task Usage

### 1. Punctuated Automatic Speech Recognition
- **Target field:** `text`

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions with punctuation.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Transcriptions include **proper punctuation** (commas, periods, etc.) and **mixed case** formatting.
- Models must predict both word sequences and punctuation marks.
- The dataset is derived from LibriSpeech with restored punctuation.