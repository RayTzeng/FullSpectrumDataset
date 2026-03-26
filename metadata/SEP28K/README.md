# SEP-28k

## Overview
**SEP-28k** is a speech dataset for stuttering event detection, built from public podcasts featuring people who stutter and organized into roughly **28,000 three-second clips**. It provides labels for five dysfluency types—**blocks**, **prolongations**, **sound repetitions**, **word repetitions**, and **interjections**—and is widely used for research on automatic stuttering analysis and assistive technologies for people with speech disorders.

## Supported Tasks
1. **Utterance-Level Stuttering Detection**
2. **Stuttering Type Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 23,460 |
| dev | 1,872 |
| test | 944 |

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
| `stuttering` | Ground-truth stuttering detection label |
| `stuttering_type` | Type(s) of stuttering event(s) present |

---

## Example Entries

```json
{"id": "WomenWhoStutter_51_26", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/WomenWhoStutter_51_26.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "SEP28K", "stuttering": "yes", "stuttering_type": "Sound_Repetition"}

{"id": "MyStutteringLife_35_10", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/MyStutteringLife_35_10.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "SEP28K", "stuttering": "no", "stuttering_type": "none"}

{"id": "HVSA_1_132", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/HVSA_1_132.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "SEP28K", "stuttering": "yes", "stuttering_type": "Block; Interjection"}
```

---

## Task Usage

### 1. Utterance-Level Stuttering Detection
- **Target field:** `stuttering` (binary stuttering detection label)

### 2. Stuttering Type Classification
- **Target field:** `stuttering_type` (stuttering type label)

---

## Label Space

### Stuttering Detection Labels
<details>
<summary>Show 2 available labels:</summary>

`yes`, `no`

</details>

### Label Definitions
<details>
<summary>Show detailed descriptions for each label:</summary>

- **yes**: The utterance contains one or more stuttering events (dysfluencies)
- **no**: The utterance does not contain any stuttering events

</details>

### Stuttering Type Labels
<details>
<summary>Show 5 available labels:</summary>

`Prolongation`, `Block`, `Sound_Repetition`, `Word_Repetition`, `Interjection`

</details>

### Stuttering Type Definitions
<details>
<summary>Show detailed descriptions for each stuttering type:</summary>

- **Prolongation**: Abnormal lengthening or extension of a sound (e.g., "ssssssun" for "sun")
- **Block**: Complete stoppage or blockage of airflow during speech, causing a silent pause
- **Sound_Repetition**: Repetition of individual sounds or syllables (e.g., "b-b-b-ball" for "ball")
- **Word_Repetition**: Repetition of entire words (e.g., "I I I want" for "I want")
- **Interjection**: Insertion of filler words or sounds to delay or avoid difficult words (e.g., "um", "uh", "like")

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- Each clip is exactly **3 seconds** long.
- This is a **multi-label** classification task for stuttering types: utterances may contain multiple types of stuttering events simultaneously, indicated by semicolon-separated labels (e.g., "Block; Interjection").
- For the **Stuttering Detection** task, it is a **binary classification** task.
- When `stuttering` is "no", the `stuttering_type` field is set to "none".
- The dataset is built from **real-world podcasts** featuring people who stutter, providing naturalistic speech data.
- SEP-28k is particularly valuable for:
  - Developing assistive technologies for people who stutter
  - Automatic stuttering detection and analysis systems
  - Speech therapy applications and progress monitoring
  - Understanding the acoustic characteristics of different dysfluency types
- The dataset captures authentic stuttering patterns from spontaneous conversational speech rather than scripted or laboratory settings.
