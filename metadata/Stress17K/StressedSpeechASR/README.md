# Stress-17K (Stressed Speech ASR)

## Overview
**Stress-17K** (released as **Stress-17K-raw**) is a synthetic speech dataset designed for research on **sentence stress understanding**, specifically how prosodic emphasis shifts the meaning of an utterance. This manifest (`raw`) contains the base audio-with-annotation entries used for **Stressed Speech ASR**: given an audio clip, predict the transcription with stressed words marked inline using `**word**` notation, along with the pragmatic interpretation of that stress pattern. The dataset was introduced alongside the **StressTest: Can YOUR Speech LM Handle the Stress?** work as a training resource for stress detection and stress reasoning. Audio is synthesized at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Stressed Speech ASR** — Transcribe speech with inline stress markers (`**word**`) indicating prosodically emphasized words

---

## Dataset Statistics

| Split | # Samples | # Unique Base Sentences | # Unique Stressed Variants |
|-------|----------:|------------------------:|---------------------------:|
| train | 4,000 | 1,003 | 2,000 |
| test | 400 | 100 | 200 |

Each base sentence is rendered with **multiple stress placements** (each targeting a different word or phrase), and each stressed variant may appear multiple times as separate audio recordings.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`Stress17K`) |
| `text` | Transcription with stressed word(s) wrapped in `**double asterisks**` |
| `description` | Free-text explanation of the pragmatic meaning conveyed by the stress pattern |
| `possible_answers` | List of 2 candidate pragmatic interpretations for the utterance |
| `label` | Index (0-based) into `possible_answers` identifying the correct interpretation |

---

## Example Entries

```json
{"id": "stress17k_train_00000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00000.wav", "sampling_rate": 16000, "duration": "2.513", "dataset": "Stress17K", "text": "**leonardo** painted a remarkable fresco.", "description": "Highlighting that it was Leonardo, as opposed to other artists, who painted the fresco.", "possible_answers": ["Highlighting that it was Leonardo, not other artists, who painted it.", "Emphasizing that the fresco was remarkable, not ordinary."], "label": 0}

{"id": "stress17k_train_00002", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00002.wav", "sampling_rate": 16000, "duration": "2.513", "dataset": "Stress17K", "text": "leonardo painted a **remarkable** fresco.", "description": "Emphasizing that the fresco, in particular, was remarkable as opposed to being ordinary or average.", "possible_answers": ["Highlighting that it was Leonardo, not other artists, who painted it.", "Emphasizing that the fresco was remarkable, not ordinary."], "label": 1}

{"id": "stress17k_train_04000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/04000.wav", "sampling_rate": 16000, "duration": "2.600", "dataset": "Stress17K", "text": "**the play** inspired the audience to act.", "description": "Highlighting that it was specifically 'the play', not some other medium or event, that inspired the audience.", "possible_answers": ["Highlighting it was 'the play', not something else, that inspired them.", "Emphasizing the audience was moved to take action, not just think or feel."], "label": 0}
```

---

## Task Usage

### 1. Stressed Speech ASR
- **Target field:** `text` (transcription with `**word**` markers indicating prosodically stressed words)
- **Additional fields:** `description` (ground-truth pragmatic explanation), `possible_answers` + `label` (multiple-choice stress meaning)

---

## Label Space

### Stress Annotation Format
Stressed words or phrases are indicated inline within the `text` field using Markdown-style bold markers:
- `**word**` — the word or phrase is prosodically stressed
- Unmarked words — not stressed

### Pragmatic Interpretation (`label`)
Each sample is paired with exactly **2 candidate interpretations** (`possible_answers`), and `label` is the 0-based index of the correct one:

| Label | Meaning |
|-------|---------|
| `0` | First candidate interpretation is correct |
| `1` | Second candidate interpretation is correct |

### Label Distribution (Training Set)
| Label | # Samples |
|-------|----------:|
| 0 | 1,946 |
| 1 | 2,054 |

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, ranging from ~1.1 to ~6.5 seconds, with an average of ~2.97 seconds.
- Total dataset duration: **~3.65 hours** across all splits (train ~3.30h + test ~0.35h).
- All speech is **synthesized** (text-to-speech), not recorded from human speakers. Prosodic emphasis is rendered acoustically by the TTS system.
- The dataset is structured around **contrastive stress pairs**: each base sentence appears in multiple versions, each emphasizing a different word or phrase to convey a different pragmatic meaning.
- The `text` field is derived from the `intonation` field in the original HuggingFace dataset (`slprl/Stress-17K-raw`), which already contains `**...**` markers.
- The `possible_answers` list always contains exactly **2 options** per sample.
- The `label` field enables binary multiple-choice evaluation without free-form generation.
- Audio was extracted from the **slprl/Stress-17K-raw** HuggingFace dataset (`train_full` split) and resampled to 16 kHz.
- The companion manifest at `../understanding/` provides the same audio reformatted as open-ended QA prompts suitable for instruction-tuned speech language models.
