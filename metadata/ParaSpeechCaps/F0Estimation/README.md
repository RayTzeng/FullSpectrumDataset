# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Fundamental Frequency (F0) Estimation**, providing mean pitch values for prosody modeling and voice analysis research.

## Supported Tasks
1. **F0 Estimation**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 116,516 |
| dev | 11,967 |
| test | 14,756 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio/speaker identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (44100 or 48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `F0` | Fundamental frequency in Hz (rounded to nearest 5) |

---

## Example Entries

```json
{"id": "voxceleb1_dev_wav_id10954_E9ze2O0JuUA_00006_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb1/dev/wav/id10954/E9ze2O0JuUA/00006_voicefixer.wav", "sampling_rate": 44100, "duration": 17.76, "dataset": "ParaSpeechCaps", "F0": 105}

{"id": "voxceleb2_dev_aac_id05010_AEm8ZsF5bCA_00154_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id05010/AEm8ZsF5bCA/00154_voicefixer.wav", "sampling_rate": 44100, "duration": 6.9, "dataset": "ParaSpeechCaps", "F0": 155}

{"id": "voxceleb1_dev_wav_id10945_wlkqb3-vdYw_00034_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb1/dev/wav/id10945/wlkqb3-vdYw/00034_voicefixer.wav", "sampling_rate": 44100, "duration": 4.8, "dataset": "ParaSpeechCaps", "F0": 145}
```

---

## Task Usage

### 1. F0 Estimation
- **Input field:** Audio
- **Target field:** `F0` (fundamental frequency in Hz)

---

## Label Space

### F0 Values (Rounded to Nearest 5 Hz)

<details>
<summary>Show F0 range and typical distributions:</summary>

**F0 Rounding**:
- Values are rounded to the nearest multiple of 5 Hz for discretization
- Example: 224.7 Hz → 225 Hz, 142.92 Hz → 145 Hz, 78.45 Hz → 80 Hz

**Typical F0 Ranges**:
- **Male voices**: 80-180 Hz (low-pitched to medium-pitched)
- **Female voices**: 160-300 Hz (medium-pitched to high-pitched)
- **Children**: 250-400 Hz (high-pitched)

**Example Distribution**:
- 60-80 Hz: Very low-pitched males
- 80-120 Hz: Low-pitched males
- 120-160 Hz: Medium-pitched males / Low-pitched females
- 160-220 Hz: High-pitched males / Medium-pitched females
- 220-300 Hz: High-pitched females
- 300+ Hz: Very high-pitched or children

**Task Type**: This can be treated as either:
- **Regression**: Predicting continuous F0 values
- **Classification**: Treating each 5 Hz bin as a discrete class

</details>

---

## F0 Rounding

F0 values are extracted from the `utterance_pitch_mean` field and **rounded to the nearest multiple of 5**:

| Original F0 | Rounded F0 |
|-------------|------------|
| 224.7 Hz    | 225 Hz     |
| 222.3 Hz    | 220 Hz     |
| 137.2 Hz    | 135 Hz     |
| 78.45 Hz    | 80 Hz      |
| 142.92 Hz   | 145 Hz     |

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled)
- **Dev**: From `dev` split
- **Test**: From `test` split

All splits contain mean F0 values extracted from the ParaSpeechCaps dataset.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
- **F0 source**: Mean fundamental frequency across the entire utterance from `utterance_pitch_mean` field.
- **Rounding**: To nearest 5 Hz creates bins (60, 65, 70, 75, 80, ..., 295, 300 Hz).
- **Filtering**: Entries with missing or non-positive F0 values are excluded.
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.
