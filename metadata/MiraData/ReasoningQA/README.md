# MiraData (Reasoning QA)

## Overview
**MiraData** is a large-scale collection of long-duration videos with structured captions, originally introduced for long-video generation and annotated with detailed descriptions from multiple perspectives to capture rich temporal and semantic content. In the **AudioFlamingo3** LongAudio-XL training pipeline, MiraData audio is paired with question–answer pairs for reasoning over extended audio clips, covering tasks such as open-ended content QA, audio scene description, temporal localization, and multiple-choice reasoning. Audio is stored as **WAV** at **16 kHz**.

## Supported Tasks
1. **Long-Audio Reasoning QA** — Given a long-form audio clip, answer open-ended or multiple-choice questions requiring comprehension of sounds, speech, and acoustic events over extended durations

---

## Dataset Statistics

| Split | # QA Pairs | # Unique Audio Files | Total Duration | Avg Duration |
|-------|----------:|---------------------:|---------------:|-------------:|
| train | 64,436 | 13,507 | ~1,339.1h | ~74.8s |

Audio duration ranges from ~0.01 to ~599.1 seconds (~10 minutes). Each audio file has 1–11 QA pairs, with an average of ~4.8 QA pairs per file.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID encoding audio file and question index (e.g., `000000010642.0_Q3`) |
| `path` | Path to audio file (WAV) |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`MiraData`) |
| `question` | Open-ended or multiple-choice question about the audio content |
| `answer` | Free-form text answer, or correct choice letter with label for MC questions |

The ID format is `{clip_id}_Q{index}`, where multiple QA pairs sharing the same `{clip_id}` prefix refer to the same audio file.

---

## Example Entries

### Open-Ended QA
```json
{"id": "000000010642.0_Q0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MiraData/wavs/000000010/000000010642.0.wav", "sampling_rate": 16000, "duration": 45.673, "dataset": "MiraData", "question": "What mood does the man convey while speaking to the dog?", "answer": "Happy"}

{"id": "000000010642.0_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MiraData/wavs/000000010/000000010642.0.wav", "sampling_rate": 16000, "duration": 45.673, "dataset": "MiraData", "question": "What is the nature of the conversation among the cowboys?", "answer": "The conversation is tense and confrontational, involving serious or possibly volatile interaction."}
```

### General Description
```json
{"id": "000000010642.0_Q2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MiraData/wavs/000000010/000000010642.0.wav", "sampling_rate": 16000, "duration": 45.673, "dataset": "MiraData", "question": "Give a general description of the audio content.", "answer": "Cowboys engaged in a tense conversation, with continuous background noise and occasional indistinct impact sounds."}
```

### Multiple-Choice QA (3 choices)
```json
{"id": "000000010642.0_Q3", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MiraData/wavs/000000010/000000010642.0.wav", "sampling_rate": 16000, "duration": 45.673, "dataset": "MiraData", "question": "Where in the audio do the generic impact sounds first appear? Choose the correct option among the options below:\n\n(A) the beginning\n(B) the middle\n(C) the end", "answer": "(A) the beginning"}
```

### Multiple-Choice QA (4 choices)
```json
{"id": "000000010642.0_Q4", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MiraData/wavs/000000010/000000010642.0.wav", "sampling_rate": 16000, "duration": 45.673, "dataset": "MiraData", "question": "What can be heard towards the end of the audio? Choose the correct option among the options below:\n\n(A) A male voice saying 'Kids are talking by the door'\n(B) A male voice with a happy mood\n(C) Animal noises\n(D) A male voice saying 'show me that shit'", "answer": "(C) Animal noises"}
```

---

## Task Usage

### 1. Long-Audio Reasoning QA
- **Input:** Audio (long-form clip) + `question` (text)
- **Target field:** `answer` (free-form text, or choice letter with label for MC questions)

---

## Label Space

### Open-Ended QA
*This task generates open-vocabulary text — there is no predefined label space.*

Answers range from single words (e.g., `Happy`) to multi-sentence descriptions depending on question complexity.

### Multiple-Choice QA
Questions have **3 or 4 answer choices** labeled `(A)`–`(C)` or `(A)`–`(D)` inline within the `question` field. The `answer` field contains the correct choice letter followed by the label text (e.g., `(A) the beginning`).

Question types include:
- **Open-ended content QA** — Questions about sounds, speakers, mood, or events heard in the audio
- **General description** — "Give a general description of the audio content."
- **Temporal localization** — "Where in the audio does X first appear?" (beginning / middle / end)
- **Multiple-choice reasoning** — Questions about specific sonic events, speaker characteristics, or acoustic scene properties

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio duration ranges widely, from near 0 to ~29 minutes, with an average of ~79 seconds. The dataset is designed for **long-form audio reasoning**.
- Each audio file is sourced from MiraData video clips covering a wide range of real-world scenes, including speech, ambient sounds, music, and mixed acoustic environments.
- The QA pairs were generated as part of the **AudioFlamingo3** LongAudio-XL training pipeline for long-form sound-and-music understanding. See the AudioFlamingo3 paper for details on the QA generation process.
- The original MiraData dataset is described in: Wang et al., "MiraData: A Large-Scale Video Dataset with Long Durations and Structured Captions" (2024).
