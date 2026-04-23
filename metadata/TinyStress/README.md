# TinyStress

## Overview
**TinyStress** (released as **TinyStress-15K**) is a synthetic speech dataset for **sentence-stress detection**, created to support models that identify which words in an utterance are prosodically emphasized and how that emphasis shifts meaning. The dataset contains approximately **16 hours** of synthesized English speech with corresponding sentence-level transcriptions and emphasis annotations. Each sample is a short utterance rendered from a simple narrative sentence, with one or more words marked as stressed. TinyStress was introduced alongside the **WhiStress** work as a scalable benchmark for prosody-aware speech understanding. Audio is synthesized at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Sentence Stress Detection**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 15,000 |
| test | 1,000 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`TinyStress`) |
| `text` | Transcription with stressed words wrapped in `**double asterisks**` |

---

## Example Entries

```json
{"id": "tinystress_train_00000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/TinyStress/train/00000.wav", "sampling_rate": 16000, "duration": "4.474", "dataset": "TinyStress", "text": "One **day,** a little girl named Lily found a needle in her room."}

{"id": "tinystress_train_00001", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/TinyStress/train/00001.wav", "sampling_rate": 16000, "duration": "4.163", "dataset": "TinyStress", "text": "One day, a **little** **girl** named Lily found a needle in her room."}

{"id": "tinystress_train_00003", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/TinyStress/train/00003.wav", "sampling_rate": 16000, "duration": "3.622", "dataset": "TinyStress", "text": "She knew it was **difficult** to play with it because it was sharp."}

{"id": "tinystress_test_00000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/TinyStress/test/00000.wav", "sampling_rate": 16000, "duration": "6.537", "dataset": "TinyStress", "text": "Spot **saw** the shiny car and said, \"Wow, Kitty, your **car** is so bright and clean!\""}
```

---

## Task Usage

### 1. Sentence Stress Detection
- **Target field:** `text` (transcription with `**word**` markers indicating stressed words)

---

## Label Space

### Stress Annotation Format
Stressed words are indicated inline within the `text` field using Markdown-style bold markers:
- `**word**` — the word (including any attached punctuation) is prosodically stressed
- Unmarked words — not stressed

Multiple words in a single utterance may be stressed simultaneously.

### Stressed Words per Utterance (Training Set)
| # Stressed Words | # Samples |
|-----------------|----------:|
| 1 | 11,325 |
| 2 | 2,248 |
| 3 | 949 |
| 4 | 300 |
| 5+ | 178 |

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, ranging from ~0.9 to ~11.3 seconds, with an average of ~3.6 seconds.
- Total dataset duration: **~16 hours** across all splits.
- All speech is **synthesized** (text-to-speech), not recorded from human speakers. Prosodic emphasis is rendered acoustically by the TTS system.
- The `text` field encodes emphasis annotations **inline**: stressed words are wrapped in `**...**` (double asterisks), including any trailing punctuation attached to the word (e.g., `**day,**`, `**replied,**`).
- Emphasis indices in the original dataset are **1-indexed** word positions; the manifest converts them to inline `**...**` markers by splitting on whitespace.
- The dataset is built from simple narrative sentences (short children's-story style prose), so vocabulary and sentence structure are straightforward.
- This dataset was introduced alongside **WhiStress** and is intended as a scalable, automatically annotatable benchmark for prosody-aware speech understanding.
- Audio was extracted from the **slprl/TinyStress-15K** HuggingFace dataset and resampled to 16 kHz.
