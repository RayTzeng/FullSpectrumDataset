# VocalSound

## Overview
**VocalSound** is a free dataset consisting of 21,024 crowdsourced recordings of laughter, sighs, coughs, throat clearing, sneezes, and sniffs from 3,365 unique subjects. The dataset captures non-speech vocal sounds produced by humans and is designed for vocal sound classification research.

## Supported Tasks
1. **Vocal Sound Classification**

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 15,570 |
| dev | 1,860 |
| test | 3,594 |

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `vocal_sound` | Vocal sound label |

## Example Entries

```json
{"id": "f1423_0_sniff", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSounds/audio_16k/f1423_0_sniff.wav", "duration": "3.328", "sampling_rate": 16000, "dataset": "VocalSound", "vocal_sound": "sniff"}

{"id": "m0609_0_cough", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSounds/audio_16k/m0609_0_cough.wav", "duration": "3.669", "sampling_rate": 16000, "dataset": "VocalSound", "vocal_sound": "cough"}

{"id": "m0573_1_sigh", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSounds/audio_16k/m0573_1_sigh.wav", "duration": "3.243", "sampling_rate": 16000, "dataset": "VocalSound", "vocal_sound": "sigh"}
```

## Task Usage

### 1. Vocal Sound Classification
- **Target field:** `vocal_sound`

## Label Space

### Vocal Sound Types
<details>
<summary>Show 6 available labels:</summary>

`cough`, `laughter`, `sigh`, `sneeze`, `sniff`, `throat clearing`

</details>

## Notes
- All audio files are sampled at **16 kHz**.
- The dataset contains recordings from **3,365 unique subjects**.
- This is a **single-label** classification task with 6 classes.
- All samples are **crowdsourced recordings** of non-speech vocal sounds.
- Audio clips have **variable duration** (approximately 3-4 seconds based on examples).
