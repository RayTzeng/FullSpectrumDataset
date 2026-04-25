# Spoken-DREAM (Reasoning QA)

## Overview
**Spoken-DREAM** is a spoken dialogue comprehension benchmark derived from **DREAM**, a dialogue-based multiple-choice reading comprehension dataset constructed from English-as-a-foreign-language (EFL) exam materials. DREAM is designed to evaluate reasoning over multi-turn conversations rather than simple answer matching, covering a wide range of everyday topics. In this work, the original text dialogues are converted into speech by synthesizing each dialogue with the **VibeVoice** TTS model, enabling spoken dialogue comprehension experiments on top of the original benchmark. Each audio file contains the full synthesized dialogue; the corresponding questions and answer choices are provided as text fields. Audio is synthesized at **24 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Spoken Dialogue Reasoning QA** — Given a synthesized multi-turn dialogue and a multiple-choice question about its content, select the correct answer (A, B, or C)

---

## Dataset Statistics

### Per-QA Manifests (`train.jsonl.gz`, `dev.jsonl.gz`, `test.jsonl.gz`)
Each entry is one question–answer pair linked to its dialogue audio file.

| Split | # QA Pairs | # Unique Dialogues |
|-------|----------:|-------------------:|
| train | 6,051 | 3,852 |
| dev | 2,017 | 1,281 |
| test | 2,024 | 1,278 |

Each dialogue has on average **~1.57 QA pairs** associated with it.

---

## Data Format

### Per-QA Format (`train.jsonl.gz`, `dev.jsonl.gz`, `test.jsonl.gz`)

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID (e.g., `1-101_dialogue_FM_Q1`) |
| `path` | Path to synthesized dialogue audio file |
| `sampling_rate` | Audio sampling rate (24000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source split (`train`, `dev`, or `test`) |
| `question` | Multiple-choice question with answer choices inline, e.g., `... (A) ... (B) ... (C) ...` |
| `answer` | Correct answer letter (`A`, `B`, or `C`) |

---

## Example Entries

### Per-QA Format
```json
{"id": "1-101_dialogue_FM_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Spoken-DREAM/wavs/train/1-101_dialogue_FM_generated.wav", "sampling_rate": 24000, "duration": 271.066667, "dataset": "train", "question": "The man (Andrew) and woman are _________. (A) siblings (B) husband and wife (C) close friends", "answer": "A"}

{"id": "1-0_dialogue_MM_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Spoken-DREAM/wavs/test/1-0_dialogue_MM_generated.wav", "sampling_rate": 24000, "duration": 72.666667, "dataset": "test", "question": "How does Joshua go to school in Japan? (A) He takes a school bus every morning (B) He rides the subway at 8:00 AM. (C) He walks with a group of students.", "answer": "C"}
```

---

## Task Usage

### 1. Spoken Dialogue Reasoning QA
- **Input:** Audio (synthesized dialogue) + `question` (text, with choices inline)
- **Target field:** `answer` (`A`, `B`, or `C`)

---

## Label Space

Each question has exactly **3 answer choices** labeled `(A)`, `(B)`, and `(C)` inline within the `question` field. The `answer` field contains the single correct letter.

### Answer Distribution (Training Set, non-empty QA pairs)
| Answer | # Samples |
|--------|----------:|
| A | 1,960 |
| B | 2,046 |
| C | 2,045 |

---

## Notes
- All audio files are sampled at **24 kHz** and stored in **WAV format**.
- Audio duration corresponds to the full synthesized dialogue, not an individual question. Dialogue durations range from ~2 to ~271 seconds, with an average of ~36.8 seconds per entry.
- Total unique dialogue audio: **~38.6 hours** across all splits (train ~23.4h, dev ~7.5h, test ~7.7h).
- All speech is **synthesized** using the **VibeVoice** TTS model. Speaker gender for each dialogue turn is encoded in the filename suffix (e.g., `_FM` = female–male, `_MF` = male–female, `_MM` = male–male).
- The original DREAM benchmark is sourced from EFL exam materials and covers a broad range of everyday conversational topics. Questions test general reasoning, inference, and comprehension rather than direct fact lookup.
- The per-QA manifests (`train.jsonl.gz`, etc.) expand each dialogue into one entry per question, making them convenient for training models that process one QA pair at a time.
- The merged manifests (`*_merged.jsonl.gz`) and `manifest_all.jsonl.gz` group all questions per dialogue into lists, which is useful for dialogue-level evaluation or batched inference.
- A small number of entries in the per-QA `train.jsonl.gz` (17 entries) have empty `question` and `answer` fields; these should be filtered out during training.
- The companion manifest at `../SpeechSummarization/` provides the same dialogue audio paired with abstractive summaries and topic labels.
