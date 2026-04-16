# CoVoST 2 (de → en)

## Overview
**CoVoST 2** is a large-scale multilingual speech-to-text translation corpus built on top of **Mozilla Common Voice**, designed to support research in end-to-end spoken language translation. This manifest covers the **German-to-English (de → en)** translation direction. Audio consists of crowd-sourced German speech recordings paired with both German source transcriptions and English target translations, spanning a broad range of speakers and accents. Audio is recorded at **48 kHz** and stored in **MP3 format**.

## Supported Tasks
1. **Speech Translation (ST): German → English**
2. **Automatic Speech Recognition (ASR): German**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 71,841 |
| dev | 13,511 |
| test | 13,511 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`CoVoST2_de_en`) |
| `source_text` | German source transcription |
| `target_text` | English target translation |
| `split` | Dataset split (`train`, `dev`, or `test`) |

---

## Example Entries

```json
{"id": "covost2_de_en_common_voice_de_17516930", "path": "/saltpool0/data/rogertseng/CoVoST2/de/clips/common_voice_de_17516930.mp3", "duration": "2.136", "sampling_rate": 48000, "dataset": "CoVoST2_de_en", "source_text": "Morgenstund' hat Gold im Mund.", "target_text": "The early bird gets the worm.", "split": "train"}

{"id": "covost2_de_en_common_voice_de_17516931", "path": "/saltpool0/data/rogertseng/CoVoST2/de/clips/common_voice_de_17516931.mp3", "duration": "3.120", "sampling_rate": 48000, "dataset": "CoVoST2_de_en", "source_text": "Das nenne ich Ironie des Schicksals.", "target_text": "That's what I call the irony of fate.", "split": "train"}

{"id": "covost2_de_en_common_voice_de_17516932", "path": "/saltpool0/data/rogertseng/CoVoST2/de/clips/common_voice_de_17516932.mp3", "duration": "1.824", "sampling_rate": 48000, "dataset": "CoVoST2_de_en", "source_text": "Was heißt das auf Schwäbisch?", "target_text": "What does that mean in Swabian?", "split": "train"}
```

---

## Task Usage

### 1. Speech Translation (ST): German → English
- **Input:** Audio (German speech)
- **Target field:** `target_text` (English translation)

### 2. Automatic Speech Recognition (ASR): German
- **Input:** Audio (German speech)
- **Target field:** `source_text` (German transcription)

---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **48 kHz** and stored in **MP3 format**.
- Audio clips have **variable duration**, typically ranging from under 1 second to ~25 seconds, with an average of ~5.9 seconds.
- Total dataset duration: **~161 hours** across all splits.
- The `source_text` field contains the original German transcription as validated in Mozilla Common Voice.
- The `target_text` field contains the English translation provided by CoVoST 2 annotators.
- The `split` field in each record reflects the official CoVoST 2 train/dev/test partition.
- German is one of the highest-resource languages in CoVoST 2, offering a large and diverse training set.
- Audio comes from **crowd-sourced Mozilla Common Voice** recordings and therefore spans a wide variety of speakers, accents, recording environments, and microphone conditions.
