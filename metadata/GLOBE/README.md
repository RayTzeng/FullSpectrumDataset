# GLOBE

## Overview
**GLOBE** is a high-quality English speech corpus with worldwide accents. Each utterance includes a transcription together with speaker metadata such as **accent**, **age**, and **gender**, making it suitable for multiple speech and paralinguistic tasks.

## Supported Tasks
1. **Accent-Robust ASR**
2. **English Accent Classification**
3. **Speaker Age Estimation**
4. **Speaker Gender Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 704,750 |
| dev | 4,750 |
| test | 9,179 |

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
| `text` | Ground-truth transcription |
| `gender` | Speaker gender label |
| `age` | Speaker age label |
| `accent` | Speaker accent label |

---

## Example Entries

```json
{"id": "common_voice_en_20794008", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_20794008.wav", "sampling_rate": 16000, "duration": "4.920", "dataset": "GLOBE", "text": "The latter was completed after his return to Italy.", "gender": "female_feminine", "age": "sixties", "accent": "united states english"}

{"id": "common_voice_en_24328949", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_24328949.wav", "sampling_rate": 16000, "duration": "6.620", "dataset": "GLOBE", "text": "The association also organizes special trains and coaches for fans for away matches.", "gender": "male_masculine", "age": "teens", "accent": "united states english"}

{"id": "common_voice_en_26761293", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_26761293.wav", "sampling_rate": 16000, "duration": "3.780", "dataset": "GLOBE", "text": "He lives in Melbourne with wife Catherine Arena and their four children.", "gender": "male_masculine", "age": "thirties", "accent": "united states english"}
```

---

## Task Usage

### 1. Accent-Robust ASR
- **Input:** speech audio
- **Output:** transcript
- **Target field:** `text`

### 2. English Accent Classification
- **Input:** speech audio
- **Output:** accent label
- **Target field:** `accent`

### 3. Speaker Age Estimation
- **Input:** speech audio
- **Output:** age label
- **Target field:** `age`

### 4. Speaker Gender Classification
- **Input:** speech audio
- **Output:** gender label
- **Target field:** `gender`

---

## Notes
- All audio files are sampled at **16 kHz**.
- The dataset is English-only, with diversity in **accent**, **age**, and **gender**.
- Because the same corpus supports multiple tasks, the task definition depends on the selected target field.