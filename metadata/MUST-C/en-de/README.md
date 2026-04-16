# MuST-C (en → de)

## Overview
**MuST-C** (Multilingual Speech Translation Corpus) is a large-scale multilingual speech-to-text translation dataset derived from English **TED Talks**, designed to support research in end-to-end spoken language translation. This manifest covers the **English-to-German (en → de)** translation direction. Audio consists of segmented English speech clips from TED Talk recordings paired with English source transcriptions and German target translations. Audio is segmented from long-form talk recordings at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Speech Translation (ST): English → German**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 250,942 |
| dev | 1,415 |
| test | 3,180 |

The test split combines two official MuST-C test sets:
- **tst-COMMON** (2,580 samples): Shared test set across all MuST-C language pairs
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
| `dataset` | Source dataset (`MuST-C_en_de`) |
| `source_text` | English source transcription |
| `target_text` | German target translation |

---

## Example Entries

```json
{"id": "en-de_train_591545ec8855", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-de/train/train_ted_1_591545ec8855.wav", "duration": "37.200", "sampling_rate": 16000, "dataset": "MuST-C_en_de", "source_text": "And it's truly a great honor to have the opportunity to come to this stage twice; I'm extremely grateful. I have been blown away by this conference, and I want to thank all of you for the many nice comments about what I had to say the other night.", "target_text": "Vielen Dank, Chris. Es ist mir wirklich eine Ehre, zweimal auf dieser Bühne stehen zu dürfen. Tausend Dank dafür. Ich bin wirklich begeistert von dieser Konferenz, und ich danke Ihnen allen für die vielen netten Kommentare zu meiner Rede vorgestern Abend."}

{"id": "en-de_dev_8a486218cd74", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-de/dev/dev_ted_767_8a486218cd74.wav", "duration": "3.500", "sampling_rate": 16000, "dataset": "MuST-C_en_de", "source_text": "I'm going to talk today about energy and climate.", "target_text": "Heute spreche ich zu Ihnen über Energie und Klima."}

{"id": "en-de_tst-COMMON_6d62c6369acc", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-de/tst-COMMON/tst-COMMON_ted_1096_6d62c6369acc.wav", "duration": "4.130", "sampling_rate": 16000, "dataset": "MuST-C_en_de", "source_text": "Back in New York, I am the head of development for a non-profit called Robin Hood.", "target_text": "Zu Hause in New York, bin ich Chef der Entwicklungsabteilung einer gemeinnützigen Organisation namens Robin Hood."}
```

---

## Task Usage

### 1. Speech Translation (ST): English → German
- **Input:** Audio (English speech)
- **Target field:** `target_text` (German translation)

---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from under 1 second to ~38 seconds, with an average of ~6.4 seconds.
- Total dataset duration: **~915 hours** across all splits.
- Audio segments are extracted from long-form TED Talk recordings using timestamps from the MuST-C YAML metadata, via ffmpeg.
- The `source_text` field contains the English transcription of the spoken segment.
- The `target_text` field contains the German translation provided by MuST-C annotators.
- Transcriptions may include **spoken annotations** such as `(Laughter)`, `(Applause)`, and `(Mock sob)` reflecting the original TED Talk annotation style.
- The dataset originates from TED Talks and therefore reflects **prepared public-speaking style** English: clear articulation, varied vocabulary, and a wide range of topics.
- The `train` split is sharded across three files (`en-de_train_00000`, `_00001`, `_00002`) due to its size; `train.jsonl.gz` is the merged manifest.
- The `test` split merges the two official evaluation sets, `tst-COMMON` and `tst-HE`, which are also available as separate files.
