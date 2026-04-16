# CoVoST 2 (es → en)

## Overview
**CoVoST 2** is a large-scale multilingual speech-to-text translation corpus built on top of **Mozilla Common Voice**, designed to support research in end-to-end spoken language translation. This manifest covers the **Spanish-to-English (es → en)** translation direction. Audio consists of crowd-sourced Spanish speech recordings paired with both Spanish source transcriptions and English target translations, spanning a broad range of speakers and accents from diverse Spanish-speaking regions. Audio is recorded at **48 kHz** and stored in **MP3 format**.

## Supported Tasks
1. **Speech Translation (ST): Spanish → English**
2. **Automatic Speech Recognition (ASR): Spanish**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 64,353 |
| dev | 13,221 |
| test | 13,221 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`CoVoST2_es_en`) |
| `source_text` | Spanish source transcription |
| `target_text` | English target translation |
| `split` | Dataset split (`train`, `dev`, or `test`) |

---

## Example Entries

```json
{"id": "covost2_es_en_common_voice_es_19742144", "path": "/saltpool0/data/rogertseng/CoVoST2/es/clips/common_voice_es_19742144.mp3", "duration": "5.616", "sampling_rate": 48000, "dataset": "CoVoST2_es_en", "source_text": "Tras su lanzamiento ha recibido positivas reseñas por parte de la crítica especializada.", "target_text": "After its release, it has received positive feedback from expert critics.", "split": "train"}

{"id": "covost2_es_en_common_voice_es_19742146", "path": "/saltpool0/data/rogertseng/CoVoST2/es/clips/common_voice_es_19742146.mp3", "duration": "4.536", "sampling_rate": 48000, "dataset": "CoVoST2_es_en", "source_text": "Las hojas se secan a la sombra, en un lugar aireado.", "target_text": "Leaves are dried in the shade, in a ventilated place.", "split": "train"}

{"id": "covost2_es_en_common_voice_es_19742323", "path": "/saltpool0/data/rogertseng/CoVoST2/es/clips/common_voice_es_19742323.mp3", "duration": "5.016", "sampling_rate": 48000, "dataset": "CoVoST2_es_en", "source_text": "Por este motivo no pudo integrar la selección de su país.", "target_text": "For this reason, he could not be part of his country's national team.", "split": "train"}
```

---

## Task Usage

### 1. Speech Translation (ST): Spanish → English
- **Input:** Audio (Spanish speech)
- **Target field:** `target_text` (English translation)

### 2. Automatic Speech Recognition (ASR): Spanish
- **Input:** Audio (Spanish speech)
- **Target field:** `source_text` (Spanish transcription)

---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **48 kHz** and stored in **MP3 format**.
- Audio clips have **variable duration**, typically ranging from under 1 second to ~16 seconds, with an average of ~5.6 seconds.
- Total dataset duration: **~141 hours** across all splits.
- The `source_text` field contains the original Spanish transcription as validated in Mozilla Common Voice.
- The `target_text` field contains the English translation provided by CoVoST 2 annotators.
- The `split` field in each record reflects the official CoVoST 2 train/dev/test partition.
- Spanish is one of the highest-resource languages in CoVoST 2, offering a large and diverse training set.
- Audio comes from **crowd-sourced Mozilla Common Voice** recordings and therefore spans a wide variety of speakers, accents (including Latin American and Iberian Spanish), recording environments, and microphone conditions.
