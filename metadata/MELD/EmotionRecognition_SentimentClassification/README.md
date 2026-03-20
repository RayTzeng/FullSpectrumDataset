# MELD

## Overview
**MELD** (Multimodal EmotionLines Dataset) is a multimodal conversational emotion recognition dataset built from the TV series **Friends**, containing dialogue utterances annotated with **emotion** and **sentiment** labels.

## Supported Tasks
1. **Speech Emotion Recognition**
2. **Speech Sentiment Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 9,988 |
| dev | 1,108 |
| test | 2,610 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `emotion` | Emotion label |
| `sentiment` | Sentiment label |

---

## Example Entries

```json
{"id": "dia549_utt0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD.Raw/train/dia549_utt0.wav", "sampling_rate": 16000, "duration": 5.44, "dataset": "MELD", "emotion": "joy", "sentiment": "positive"}

{"id": "dia872_utt8", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD.Raw/train/dia872_utt8.wav", "sampling_rate": 16000, "duration": 5.504, "dataset": "MELD", "emotion": "neutral", "sentiment": "neutral"}

{"id": "dia759_utt8", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD.Raw/train/dia759_utt8.wav", "sampling_rate": 16000, "duration": 1.429312, "dataset": "MELD", "emotion": "anger", "sentiment": "negative"}
```

---

## Task Usage

### 1. Speech Emotion Recognition
- **Target field:** `emotion` (emotion label)

### 2. Speech Sentiment Classification
- **Target field:** `sentiment` (sentiment label)

---

## Label Space

### Emotion
<details>
<summary>Show 7 available labels:</summary>

`neutral`, `joy`, `surprise`, `anger`, `sadness`, `disgust`, `fear`

</details>

### Sentiment
<details>
<summary>Show 3 available labels:</summary>

`neutral`, `negative`, `positive`

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- MELD is a **conversational** dataset built from dialogue utterances in the TV series **Friends**.
- Because the same corpus supports multiple tasks, the task definition depends on the selected target field.