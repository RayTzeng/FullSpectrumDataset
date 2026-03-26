# FluencyBank

## Overview
**FluencyBank** is a shared multimodal corpus within **TalkBank** created to support research on fluency development and fluency disorders, including speech from children and adults who stutter as well as other speaker groups. The dataset provides labels for five dysfluency types—**blocks**, **prolongations**, **sound repetitions**, **word repetitions**, and **interjections**—and is organized into three-second clips for research on automatic stuttering analysis and speech fluency assessment.

## Supported Tasks
1. **Utterance-Level Stuttering Detection**
2. **Stuttering Type Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 3,864 |

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
{"id": "FluencyBank_87_10", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/FluencyBank_087_10.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "FluencyBank", "stuttering": "yes", "stuttering_type": "Word_Repetition; Interjection"}

{"id": "FluencyBank_98_56", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/FluencyBank_098_56.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "FluencyBank", "stuttering": "no", "stuttering_type": "none"}

{"id": "FluencyBank_219_106", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SEP28K/archive/clips/stuttering-clips/clips/FluencyBank_219_106.wav", "sampling_rate": 16000, "duration": "3.000", "dataset": "FluencyBank", "stuttering": "yes", "stuttering_type": "Prolongation; Interjection"}
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
- This is a **multi-label** classification task for stuttering types: utterances may contain multiple types of stuttering events simultaneously, indicated by semicolon-separated labels (e.g., "Prolongation; Interjection").
- For the **Stuttering Detection** task, it is a **binary classification** task.
- When `stuttering` is "no", the `stuttering_type` field is set to "none".
- There is no `dev` or `test` split in the provided manifest.
- The dataset is part of **TalkBank**, a multilingual corpus hosting system for transcribed and annotated conversational interactions.
- FluencyBank includes speech from both **children and adults** who stutter, as well as other speaker groups, providing diverse age ranges and fluency profiles.
- The dataset is particularly valuable for:
  - Developing assistive technologies for people who stutter
  - Automatic stuttering detection and analysis systems
  - Speech therapy applications and progress monitoring
  - Understanding the acoustic characteristics of different dysfluency types
  - Studying fluency development across different age groups and populations
- FluencyBank provides a controlled, well-documented resource for research on speech fluency and fluency disorders.
