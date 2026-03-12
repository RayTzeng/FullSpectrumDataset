# Google Speech Commands

## Overview
**Google Speech Commands** is a large-scale dataset of one-second audio clips containing isolated spoken English words and background noise, recorded by a diverse set of speakers. It is widely used for keyword spotting research, enabling models to learn how to recognize short command words such as “left,” “right,” “up,” and “down” from speech audio.

## Supported Tasks
1. **Keyword Spotting**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 84,848 |
| dev | 9,982 |
| test | 4,890 |

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
| `label` | Ground-truth keyword label |

---

## Example Entries

```json
{"id": "7d6b4b10_nohash_1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/SpeechCommands/train/left/7d6b4b10_nohash_1.wav", "duration": 1.0, "dataset": "SpeechCommands", "label": "left", "sampling_rate": 16000}

{"id": "c0e8f5a1_nohash_1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/SpeechCommands/train/down/c0e8f5a1_nohash_1.wav", "duration": 1.0, "dataset": "SpeechCommands", "label": "down", "sampling_rate": 16000}

{"id": "f8ba7c0e_nohash_3", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/SpeechCommands/train/seven/f8ba7c0e_nohash_3.wav", "duration": 1.0, "dataset": "SpeechCommands", "label": "seven", "sampling_rate": 16000}
```

---

## Task Usage

### 1. Keyword Spotting
- **Target field:** `label` (keyword label)

---

## Label Space

### Keywords
<details>
<summary>Show keyword labels:</summary>

`_silence_`, `backward`, `bed`, `bird`, `cat`, `dog`, `down`, `eight`, `five`, `follow`, `forward`, `four`, `go`, `happy`, `house`, `learn`, `left`, `marvin`, `nine`, `no`, `off`, `on`, `one`, `right`, `seven`, `sheila`, `six`, `stop`, `three`, `tree`, `two`, `up`, `visual`, `wow`, `yes`, `zero`

</details>

---

## Notes
- All audio files are **1 second** long.
- All audio files are sampled at **16 kHz**.
- Each clip contains either a single spoken keyword or a background/noise example.