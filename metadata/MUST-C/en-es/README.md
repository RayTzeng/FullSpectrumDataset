# MuST-C (en → es)

## Overview
**MuST-C** (Multilingual Speech Translation Corpus) is a large-scale multilingual speech-to-text translation dataset derived from English **TED Talks**, designed to support research in end-to-end spoken language translation. This manifest covers the **English-to-Spanish (en → es)** translation direction. Audio consists of segmented English speech clips from TED Talk recordings paired with English source transcriptions and Spanish target translations. Audio is segmented from long-form talk recordings at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Speech Translation (ST): English → Spanish**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 265,625 |
| dev | 1,316 |
| test | 3,102 |

The test split combines two official MuST-C test sets:
- **tst-COMMON** (2,502 samples): Shared test set across all MuST-C language pairs
- **tst-HE** (600 samples): Human evaluation subset

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`MuST-C_en_es`) |
| `source_text` | English source transcription |
| `target_text` | Spanish target translation |

---

## Example Entries

```json
{"id": "en-es_train_8f8bfe1b8a9e", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-es/train/train_ted_1_8f8bfe1b8a9e.wav", "duration": "28.800", "sampling_rate": 16000, "dataset": "MuST-C_en_es", "source_text": "And it's truly a great honor to have the opportunity to come to this stage twice; I'm extremely grateful. I have been blown away by this conference, and I want to thank all of you for the many nice comments about what I had to say the other night.", "target_text": "Muchas gracias Chris. Y es en verdad un gran honor tener la oportunidad de venir a este escenario por segunda vez. Estoy extremadamente agradecido. He quedado conmovido por esta conferencia, y deseo agradecer a todos ustedes sus amables comentarios acerca de lo que tenía que decir la otra noche."}

{"id": "en-es_train_78faa5fc6fd7", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-es/train/train_ted_1_78faa5fc6fd7.wav", "duration": "22.350", "sampling_rate": 16000, "dataset": "MuST-C_en_es", "source_text": "And I say that sincerely, partly because (Mock sob) I need that. (Laughter)", "target_text": "Y digo eso sinceramente, en parte porque — (Sollozos fingidos) — ¡lo necesito! (Risas) ¡Pónganse en mi posición!"}

{"id": "en-es_train_d9f7267962ca", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-es/train/train_ted_1_d9f7267962ca.wav", "duration": "14.120", "sampling_rate": 16000, "dataset": "MuST-C_en_es", "source_text": "(Laughter) Now I have to take off my shoes or boots to get on an airplane! (Laughter) (Applause)", "target_text": "Volé en el avión vicepresidencial por ocho años. ¡Ahora tengo que quitarme mis zapatos o botas para subirme a un avión! (Risas) (Aplausos)"}
```

---

## Task Usage

### 1. Speech Translation (ST): English → Spanish
- **Input:** Audio (English speech)
- **Target field:** `target_text` (Spanish translation)


---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from under 1 second to ~30 seconds, with an average of ~6.7 seconds.
- Total dataset duration: **~1,009 hours** across all splits, making en-es the largest of the three MuST-C language pairs in this collection.
- Audio segments are extracted from long-form TED Talk recordings using timestamps from the MuST-C YAML metadata, via ffmpeg.
- The `source_text` field contains the English transcription of the spoken segment.
- The `target_text` field contains the Spanish translation provided by MuST-C annotators.
- Transcriptions may include **spoken annotations** such as `(Laughter)`, `(Applause)`, and `(Risas)` (in the Spanish target) reflecting the original TED Talk annotation style.
- The dataset originates from TED Talks and therefore reflects **prepared public-speaking style** English: clear articulation, varied vocabulary, and a wide range of topics.
- The `train` split is sharded across three files (`en-es_train_00000`, `_00001`, `_00002`) due to its size; `train.jsonl.gz` is the merged manifest.
- The `test` split merges the two official evaluation sets, `tst-COMMON` and `tst-HE`, which are also available as separate files.
