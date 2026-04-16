# CoVoST 2 (zh-CN → en)

## Overview
**CoVoST 2** is a large-scale multilingual speech-to-text translation corpus built on top of **Mozilla Common Voice**, designed to support research in end-to-end spoken language translation. This manifest covers the **Mandarin Chinese-to-English (zh-CN → en)** translation direction. Audio consists of crowd-sourced Mandarin Chinese speech recordings paired with both Chinese source transcriptions and English target translations, spanning a range of speakers and accents. Audio is recorded at **48 kHz** and stored in **MP3 format**.

## Supported Tasks
1. **Speech Translation (ST): Mandarin Chinese → English**
2. **Automatic Speech Recognition (ASR): Mandarin Chinese**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 7,079 |
| dev | 4,843 |
| test | 4,898 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`CoVoST2_zh-CN_en`) |
| `source_text` | Mandarin Chinese source transcription |
| `target_text` | English target translation |
| `split` | Dataset split (`train`, `dev`, or `test`) |

---

## Example Entries

```json
{"id": "covost2_zh-CN_en_common_voice_zh-CN_18536372", "path": "/saltpool0/data/rogertseng/CoVoST2/zh-CN/clips/common_voice_zh-CN_18536372.mp3", "duration": "5.568", "sampling_rate": 48000, "dataset": "CoVoST2_zh-CN_en", "source_text": "对于更高阶的导数，我们可以继续同样的过程。", "target_text": "For derivatives of higher order, we can use the same process.", "split": "train"}

{"id": "covost2_zh-CN_en_common_voice_zh-CN_18536373", "path": "/saltpool0/data/rogertseng/CoVoST2/zh-CN/clips/common_voice_zh-CN_18536373.mp3", "duration": "7.824", "sampling_rate": 48000, "dataset": "CoVoST2_zh-CN_en", "source_text": "乳头凹陷也称为乳头内陷，是指乳头凹陷，未突出乳房的情形。", "target_text": "An inverted nipple is a condition where the nipple, instead of pointing outward, is retracted into the breast.", "split": "train"}

{"id": "covost2_zh-CN_en_common_voice_zh-CN_18536375", "path": "/saltpool0/data/rogertseng/CoVoST2/zh-CN/clips/common_voice_zh-CN_18536375.mp3", "duration": "8.544", "sampling_rate": 48000, "dataset": "CoVoST2_zh-CN_en", "source_text": "在很多情况下借词中的被读作而非，甚至在源语言中读作时也如此。", "target_text": "It is often that the loan words are read as exceptions, including time in source language.", "split": "train"}
```

---

## Task Usage

### 1. Speech Translation (ST): Mandarin Chinese → English
- **Input:** Audio (Mandarin Chinese speech)
- **Target field:** `target_text` (English translation)

### 2. Automatic Speech Recognition (ASR): Mandarin Chinese
- **Input:** Audio (Mandarin Chinese speech)
- **Target field:** `source_text` (Mandarin Chinese transcription)

---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **48 kHz** and stored in **MP3 format**.
- Audio clips have **variable duration**, ranging from ~1.5 seconds to ~20 seconds, with an average of ~5.7 seconds.
- Total dataset duration: **~27 hours** across all splits.
- The `source_text` field contains the original Mandarin Chinese transcription (simplified characters) as validated in Mozilla Common Voice.
- The `target_text` field contains the English translation provided by CoVoST 2 annotators.
- The `split` field in each record reflects the official CoVoST 2 train/dev/test partition.
- Compared to the German and Spanish subsets, the zh-CN split is smaller in training data but has proportionally larger dev and test sets, reflecting the original CoVoST 2 design.
- Audio comes from **crowd-sourced Mozilla Common Voice** recordings and therefore spans a variety of speakers, Mandarin accents, recording environments, and microphone conditions.
- The Chinese-to-English translation direction presents unique challenges including:
  - **Morphological divergence**: Chinese is an isolating language with no inflection, while English uses morphological markers
  - **Word order differences**: Chinese is SVO but with different relative clause and modifier ordering conventions
  - **Script mismatch**: Source text uses logographic simplified Chinese characters; target text uses the Latin alphabet
