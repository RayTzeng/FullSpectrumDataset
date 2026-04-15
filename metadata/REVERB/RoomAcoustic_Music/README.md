# REVERB

## Overview
**REVERB** (Room Acoustic Music) is a large-scale dataset for acoustic parameter estimation from reverberant music recordings. The dataset contains **82,000 music samples** synthesized by convolving room impulse responses (RIRs) from the **SLR28 dataset** with single instrument stems from **Slakh2100**. Each sample is annotated with ground-truth room acoustic measurements including reverberation time (RT60), direct-to-reverberant ratio (DRR), and clarity indices (C50/C80). These measurements characterize the acoustic properties of the recording environment, making the dataset valuable for research on blind room acoustic parameter estimation, music dereverberation, and acoustic scene analysis from musical content.

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
{"id": "train_music_000001", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train_music/train_music_000001.wav", "sampling_rate": 16000, "duration": 7.08, "dataset": "REVERB-Music", "RT60": 2.5387642820031573, "DRR_2.5ms": 0.6654611065274946, "DRR_50ms": 13.199380061183831, "C50": 13.199380061183831, "C80": 13.856507955047094}

{"id": "train_music_000008", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train_music/train_music_000008.wav", "sampling_rate": 16000, "duration": 4.14, "dataset": "REVERB-Music", "RT60": 0.3104858464391653, "DRR_2.5ms": -3.863066797513755, "DRR_50ms": 23.210388135772853, "C50": 23.210388135772853, "C80": 31.05584689686973}

{"id": "train_music_000000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/REVERB/audio/train_music/train_music_000000.wav", "sampling_rate": 16000, "duration": 9.36, "dataset": "REVERB-Music", "RT60": 1.9720982334527821, "DRR_2.5ms": 0.7596954363301545, "DRR_50ms": 12.71859771010162, "C50": 12.71859771010162, "C80": 13.103131225263748}
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
  - **< 0.3s**: Anechoic or very dry room (recording studio, isolation booth)
  - **0.3-0.6s**: Typical home listening room or small studio
  - **0.6-1.2s**: Medium-sized concert hall or recording studio
  - **1.2-2.5s**: Large concert hall or theater
  - **> 2.5s**: Cathedral, opera house, or highly reverberant venue

### DRR (Direct-to-Reverberant Ratio)
- **Range**: -35.735 to 49.145 dB
- **Type**: Continuous regression task
- **Average**: ~14.45 dB (in training set)
- **Interpretation**:
  - **> 20 dB**: Close-miked recording, minimal room effect
  - **10-20 dB**: Moderate distance, natural room ambience
  - **0-10 dB**: Distant recording, prominent room character
  - **< 0 dB**: Very distant recording, reverberant field dominates

### C50 (Clarity Index at 50ms)
- **Range**: -35.735 to 49.145 dB
- **Type**: Continuous regression task
- **Average**: ~14.45 dB (in training set)
- **Interpretation**:
  - **> 5 dB**: Excellent clarity for articulation and lyrics
  - **0-5 dB**: Good clarity with noticeable ambience
  - **-5 to 0 dB**: Fair clarity, significant reverberation
  - **< -5 dB**: Poor clarity, excessive reverberation

### C80 (Clarity Index at 80ms)
- **Range**: -34.395 to 69.261 dB
- **Type**: Continuous regression task
- **Average**: ~18.50 dB (in training set)
- **Interpretation**:
  - **> 5 dB**: Excellent music clarity and definition
  - **0-5 dB**: Good music clarity with pleasant ambience
  - **-5 to 0 dB**: Fair clarity, warm reverberant character
  - **< -5 dB**: Poor clarity, muddy or washed-out sound

---

## Acoustic Parameters

### RT60 (Reverberation Time)
The time required for sound pressure level to decrease by 60 dB after the sound source stops. In music contexts, RT60 significantly affects perceived warmth, spaciousness, and blend. Different musical genres have optimal RT60 ranges (e.g., classical music benefits from longer RT60, while pop/rock prefer shorter RT60).

### DRR (Direct-to-Reverberant Ratio)
The ratio between direct sound energy and reverberant sound energy, measured in dB. Two variants are provided:
- **DRR_2.5ms**: Uses 2.5ms threshold to separate direct from reverberant sound
- **DRR_50ms**: Uses 50ms threshold (more commonly used in music applications)

### C50 (Clarity Index at 50ms)
The logarithmic ratio of early sound energy (0-50ms) to late sound energy (after 50ms). While traditionally used for speech, C50 is also relevant for music where articulation and rhythmic clarity are important (e.g., fast passages, vocal intelligibility).

### C80 (Clarity Index at 80ms)
The logarithmic ratio of early sound energy (0-80ms) to late sound energy (after 80ms). This is the **primary clarity metric for music**, as the 80ms threshold better captures the perceptual boundary between enhancing warmth and causing muddiness in musical performance.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from 3 to 10 seconds.
- All acoustic parameters are **continuous regression targets**.
- The dataset covers a wide range of acoustic environments suitable for music recording and performance.
- **RT60 values** span from studio-dry (0.05s) to cathedral-like (8.8s) conditions.
- **DRR values** reflect microphone placement and venue size.
- **C80 is the preferred metric for music clarity**, as the 80ms threshold aligns better with musical perception than C50.
- Note that **C50 = DRR_50ms** by definition, as both measure the same energy ratio at 50ms threshold.
- Musical content presents unique challenges for acoustic parameter estimation:
  - **Spectral complexity**: Rich harmonic content and wide frequency range
  - **Temporal structure**: Note onsets, sustained tones, and varying dynamics
  - **Masking effects**: Complex interactions between direct and reverberant sound
- These parameters are fundamental for:
  - **Music production**: Artificial reverberation and spatial effects design
  - **Concert hall acoustics**: Venue characterization and optimization
  - **Audio restoration**: Historical recording enhancement and remastering
  - **Music information retrieval**: Acoustic scene understanding and recording metadata extraction
  - **Immersive audio**: Spatial audio rendering and room simulation for music
