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
{"id": "common_voice_en_29718448", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_29718448.wav", "sampling_rate": 16000, "duration": "4.060", "dataset": "GLOBE", "text": "She has kept on drawing and painting and writing.", "gender": "male", "age": "twenties", "accent": "canadian english"}

{"id": "common_voice_en_34134180", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_34134180.wav", "sampling_rate": 16000, "duration": "7.120", "dataset": "GLOBE", "text": "He suffered from Persecution Complex and used to wander from one place to another.", "gender": "male", "age": "thirties", "accent": "new zealand english"}

{"id": "common_voice_en_20240255", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/GLOBE/train/common_voice_en_20240255.wav", "sampling_rate": 16000, "duration": "4.160", "dataset": "GLOBE", "text": "Thus epistemic considerations enter in addition to structural ones.", "gender": "male", "age": "teens", "accent": "australian english"}
```

---

## Task Usage

### 1. Accent-Robust ASR
- **Target field:** `text` (transcription)

### 2. English Accent Classification
- **Target field:** `accent` (accent label)

### 3. Speaker Age Estimation
- **Target field:** `age` (age label)

### 4. Speaker Gender Classification
- **Target field:** `gender` (gender label)

---

## Label Space

### Age
<details>
<summary>Show 9 available labels:</summary>

`teens`, `twenties`, `thirties`, `fourties`, `fifties`, `sixties`, `seventies`, `eighties`, `nineties`

</details>

### Accent
<details>
<summary>Show available accent labels:</summary>

English accent varieties include but are not limited to:

`united states english`, `england english`, `india/south asia`, `canadian english`, `german-accented english`, `australian english`, `southern african`, `northern irish`, `irish english`, `new zealand english`

</details>

### Gender
<details>
<summary>Show 4 available labels:</summary>

`male`, `female`, `non-binary`, `transgender`

Note: The majority of samples belong to the `male` and `female` categories.

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- The dataset is English-only, with diversity in **accent**, **age**, and **gender**.
- Because the same corpus supports multiple tasks, the task definition depends on the selected target field.
- If your manifest uses exact string labels, keep the README label names identical to the manifest values. For example, if the stored label is `fourties`, avoid silently normalizing it to `forties`.