# REVERB

## Overview
**REVERB** (Room Acoustic Speech) is a large-scale dataset for acoustic parameter estimation from reverberant speech recordings. The dataset contains **82,000 speech samples** synthesized by convolving room impulse responses (RIRs) from the **SLR28 dataset** with clean speech segments from **LibriSpeech**. Each sample is annotated with ground-truth room acoustic measurements including reverberation time (RT60), direct-to-reverberant ratio (DRR), and clarity indices (C50/C80). These measurements characterize the acoustic properties of the recording environment, making the dataset valuable for research on blind room acoustic parameter estimation, speech dereverberation, and acoustic scene analysis.

## Supported Tasks
1. **Reverberation Time (RT60) Estimation**
2. **Direct-to-Reverberant Ratio Estimation**
3. **Clarity Index (C50/C80) Estimation**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 80,000 |
| dev | 1,000 |
| test | 1,000 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `RT60` | Reverberation time (seconds) - time for sound to decay by 60 dB |
| `DRR_2.5ms` | Direct-to-reverberant ratio using 2.5ms threshold (dB) |
| `DRR_50ms` | Direct-to-reverberant ratio using 50ms threshold (dB) |
| `C50` | Clarity index at 50ms (dB) - speech intelligibility metric |
| `C80` | Clarity index at 80ms (dB) - music clarity metric |

---

## Example Entries

```json
{"id": "train_000000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train/train_000000.wav", "sampling_rate": 16000, "duration": 5.38, "dataset": "REVERB", "RT60": 2.890423083462326, "DRR_2.5ms": -1.6737910541989967, "DRR_50ms": 8.074783777383228, "C50": 8.074783777383228, "C80": 10.73154816345406}

{"id": "train_000001", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train/train_000001.wav", "sampling_rate": 16000, "duration": 5.13, "dataset": "REVERB", "RT60": 0.15807440708920953, "DRR_2.5ms": -0.11654763494673329, "DRR_50ms": 28.494004333832137, "C50": 28.494004333832137, "C80": 35.34426922307283}

{"id": "train_000002", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train/train_000002.wav", "sampling_rate": 16000, "duration": 8.3, "dataset": "REVERB", "RT60": 2.8426038511398786, "DRR_2.5ms": 0.4277139909763624, "DRR_50ms": 8.418370278782458, "C50": 8.418370278782458, "C80": 11.339656602175108}
```

---

## Task Usage

### 1. Reverberation Time (RT60) Estimation
- **Target field:** `RT60` (reverberation time in seconds)

### 2. Direct-to-Reverberant Ratio Estimation
- **Target field:** `DRR_50ms` (DRR at 50ms threshold in dB)

### 3. Clarity Index (C50/C80) Estimation
- **Target field:** `C50` (clarity at 50ms in dB) or `C80` (clarity at 80ms in dB)

---

## Label Space

### RT60 (Reverberation Time)
- **Range**: 0.053 to 8.808 seconds
- **Type**: Continuous regression task
- **Average**: ~1.65 seconds (in training set)
- **Interpretation**:
  - **< 0.3s**: Anechoic or very dry room (recording booth, outdoor)
  - **0.3-0.6s**: Typical living room or small office
  - **0.6-1.2s**: Larger room or medium-sized hall
  - **1.2-2.5s**: Large hall or auditorium
  - **> 2.5s**: Cathedral, large concert hall, or highly reverberant space

### DRR (Direct-to-Reverberant Ratio)
- **Range**: -35.735 to 49.145 dB
- **Type**: Continuous regression task
- **Average**: ~14.44 dB (in training set)
- **Interpretation**:
  - **> 20 dB**: Very close to source, minimal reverberation
  - **10-20 dB**: Moderate distance, balanced direct/reverberant sound
  - **0-10 dB**: Far from source, significant reverberation
  - **< 0 dB**: Reverberant energy dominates direct sound

### C50 (Clarity Index at 50ms)
- **Range**: -35.735 to 49.145 dB
- **Type**: Continuous regression task
- **Average**: ~14.44 dB (in training set)
- **Interpretation**:
  - **> 5 dB**: Excellent speech intelligibility
  - **0-5 dB**: Good speech intelligibility
  - **-5 to 0 dB**: Fair speech intelligibility
  - **< -5 dB**: Poor speech intelligibility

### C80 (Clarity Index at 80ms)
- **Range**: -34.395 to 69.922 dB
- **Type**: Continuous regression task
- **Average**: ~18.49 dB (in training set)
- **Interpretation**:
  - **> 5 dB**: Excellent music clarity
  - **0-5 dB**: Good music clarity
  - **-5 to 0 dB**: Fair music clarity
  - **< -5 dB**: Poor music clarity, excessive reverberation

---

## Acoustic Parameters

### RT60 (Reverberation Time)
The time required for sound pressure level to decrease by 60 dB after the sound source stops. Longer RT60 indicates more reverberant environments.

### DRR (Direct-to-Reverberant Ratio)
The ratio between direct sound energy and reverberant sound energy, measured in dB. Two variants are provided:
- **DRR_2.5ms**: Uses 2.5ms threshold to separate direct from reverberant sound
- **DRR_50ms**: Uses 50ms threshold (more commonly used)

### C50 (Clarity Index at 50ms)
The logarithmic ratio of early sound energy (0-50ms) to late sound energy (after 50ms). Primarily used for speech intelligibility assessment.

### C80 (Clarity Index at 80ms)
The logarithmic ratio of early sound energy (0-80ms) to late sound energy (after 80ms). Primarily used for music clarity assessment.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from 3 to 10 seconds.
- All acoustic parameters are **continuous regression targets**.
- The dataset covers a wide range of acoustic environments from anechoic to highly reverberant spaces.
- **RT60 values** span from nearly anechoic (0.05s) to cathedral-like (8.8s) conditions.
- **DRR values** indicate source-to-listener distance and room characteristics.
- **C50 and C80** are related but target different applications (speech vs. music).
- Note that **C50 = DRR_50ms** by definition, as both measure the same energy ratio at 50ms threshold.
- These parameters are fundamental for:
  - **Speech enhancement**: Dereverberation and intelligibility improvement
  - **Audio forensics**: Room identification and recording environment analysis
  - **Virtual acoustics**: Realistic room simulation and auralization
  - **Hearing aid design**: Environment-adaptive processing
