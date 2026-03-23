# AVID

## Overview
**AVID** (Aalto Vocal Intensity Database) is an open, calibrated speech and electroglottography (EGG) corpus designed for machine-learning studies of vocal intensity. The dataset contains recordings from **50 speakers** producing speech in four intensity categories—**soft**, **normal**, **loud**, and **very loud**—with sentence-level labels that support both vocal-intensity classification and sound-pressure-level prediction tasks.

## Supported Tasks
1. **Vocal Intensity Classification**
2. **Sound Pressure Level Prediction**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 10,000 |
| test | 800 |

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
| `vocal_intensity` | Ground-truth vocal intensity category |
| `sound_pressure_level` | Calibrated sound pressure level in dB |

---

## Example Entries

```json
{"id": "sp44_s2_sen19_soft", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp44_s2_sen19_soft.wav", "sampling_rate": 44100, "duration": 1.3141496598639455, "dataset": "AVID", "vocal_intensity": "soft", "sound_pressure_level": 75.8}

{"id": "sp35_s2_para1_normal", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/PARA/sp35_s2_para1_normal.wav", "sampling_rate": 44100, "duration": 27.572471655328798, "dataset": "AVID", "vocal_intensity": "normal", "sound_pressure_level": 86.1}

{"id": "sp12_s1_sen9_normal", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp12_s1_sen9_normal.wav", "sampling_rate": 44100, "duration": 1.5659183673469388, "dataset": "AVID", "vocal_intensity": "normal", "sound_pressure_level": 86.4}
```

---

## Task Usage

### 1. Vocal Intensity Classification
- **Target field:** `vocal_intensity` (intensity category label)

### 2. Sound Pressure Level Prediction
- **Target field:** `sound_pressure_level` (continuous SPL value in dB)

---

## Label Space

### Vocal Intensity Categories
<details>
<summary>Show 4 available labels:</summary>

`soft`, `normal`, `loud`, `veryloud`

</details>

### Intensity Definitions and Recording Instructions
<details>
<summary>Show detailed descriptions for each intensity level:</summary>

- **soft**: Speak softly but do not whisper; speak as you would talk to your peer in a lecture
  - Statistical range: SPL < 79 dB
- **normal**: Speak as you would talk to your friend during a lecture break and intervals
  - Statistical range: 79 dB ≤ SPL < 86 dB
- **loud**: Speak as a lecturer
  - Statistical range: 86 dB ≤ SPL < 93 dB
- **veryloud**: Speak as you would talk to someone in a noisy room but do not shout
  - Statistical range: SPL ≥ 93 dB

</details>

### Sound Pressure Level (SPL)
<details>
<summary>Show SPL characteristics:</summary>

- **Type**: Continuous regression target
- **Range**: Approximately 70 dB to 110 dB
- **Unit**: Decibels (dB)
- **Calibration**: Values are calibrated measurements, not relative estimates

</details>

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Audio files are stored in **WAV format**.
- The dataset includes both sentence-level (SENT) and paragraph-level (PARA) recordings, as indicated by the file paths.
- Duration varies significantly across samples, from around 1 second for sentences to over 25 seconds for paragraphs.
- The four intensity categories were elicited using specific speaking scenarios designed to produce naturalistic variations in vocal effort.
- While intensity categories are defined by statistical SPL ranges, there may be some overlap between adjacent categories due to individual speaker differences.
- The dataset provides both **categorical labels** (vocal_intensity) and **continuous measurements** (sound_pressure_level), enabling both classification and regression tasks.
- The corpus includes electroglottography (EGG) recordings alongside audio, though the manifests focus on the audio modality.
- This is a calibrated dataset, meaning the SPL values represent actual acoustic measurements rather than relative intensities.
