# AudioSet - Vocal Sound Classification

## Overview
**AudioSet** consists of a collection of over **2 million** human-labeled 10-second sound clips drawn from YouTube videos. This subset focuses on **human non-verbal vocal sounds**, filtering the full AudioSet ontology to include only vocal sound events such as laughter, crying, breathing, coughing, and other non-speech vocalizations.

## Supported Tasks
1. **Vocal Sound Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 26,607 |
| test | 1,463 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source subset |
| `vocal_sound` | Ground-truth vocal sound labels |

---

## Example Entries

```json
{"id": "L-SKBowUGv0_20_30", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/L-SKBowUGv0.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "unbalanced", "vocal_sounds": "Screaming"}

{"id": "Jxhsq-9YSA0_90_100", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/Jxhsq-9YSA0.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "unbalanced", "vocal_sounds": "Laughter; Baby laughter"}

{"id": "rPu7ppZVTuU_200_210", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/rPu7ppZVTuU.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "unbalanced", "vocal_sounds": "Baby laughter"}
```

---

## Task Usage

### 1. Vocal Sound Classification
- **Target field:** `vocal_sounds` (semicolon-separated vocal sound labels)

---

## Label Space

### Vocal Sound Labels
<details>
<summary>Show 35 available labels:</summary>

`Shout`, `Bellow`, `Whoop`, `Yell`, `Battle cry`, `Children shouting`, `Screaming`, `Laughter`, `Baby laughter`, `Giggle`, `Snicker`, `Belly laugh`, `Chuckle, chortle`, `Crying, sobbing`, `Baby cry, infant cry`, `Whimper`, `Wail, moan`, `Sigh`, `Humming`, `Groan`, `Grunt`, `Whistling`, `Breathing`, `Wheeze`, `Snoring`, `Gasp`, `Pant`, `Snort`, `Cough`, `Throat clearing`, `Sneeze`, `Sniff`, `Gargling`, `Beatboxing`

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Each clip is approximately **10 seconds** long.
- This is a **multi-label** classification task: each clip may contain one or multiple vocal sound event labels.
- Labels are stored in the `vocal_sounds` field as a **semicolon-separated string**.
- This subset excludes speech content and focuses exclusively on **non-verbal vocal sounds**.
- There is no `dev` split in the provided manifest.
