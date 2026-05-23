# Harmonicity

## Overview
**Harmonicity** is a binary classification dataset designed to evaluate audio models' ability to distinguish between harmonic and non-harmonic sounds. The dataset contains **100,000 training samples** and **1,000 test samples**, with approximately balanced classes. Samples are drawn from diverse acoustic sources including speech, vocal sounds, music, environmental audio, and synthetic noise, with durations ranging from **1.5 to 15 seconds**.

Harmonic sources include speech (LibriSpeech, VocalSet), harmonic vocal sounds (laughter, sigh), music (NSynth), and harmonic environmental sounds. Non-harmonic sources include synthetic noise (white, pink, brown), percussive music (LoFiDrums), non-harmonic vocal sounds (cough, sneeze, sniff, throat clearing), and non-harmonic environmental sounds.

All audio is sampled at **16 kHz** in mono. This benchmark evaluates models' understanding of fundamental acoustic properties related to periodicity, pitch perception, and spectral structure.

## Supported Tasks
1. **Harmonicity Classification**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 100,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **1.5s to 15.0s**
- Average duration: **~4.7s**
- Sampling rate: **16 kHz** for all audio files

### Harmonicity Distribution (Training Set)

| Label | # Samples |
|-------|----------:|
| no (non-harmonic) | 50,269 |
| yes (harmonic) | 49,731 |

### Source Dataset Distribution (Training Set)

| Dataset | # Samples | Type |
|---------|----------:|------|
| ESC-50 | 18,559 | Environmental sounds (mixed) |
| FSD50K | 18,482 | Environmental sounds (mixed) |
| VocalSound | 18,245 | Vocal sounds (mixed) |
| LoFiDrums | 10,063 | Drums (non-harmonic) |
| NSynth | 8,387 | Music (harmonic) |
| VocalSet | 8,222 | Singing (harmonic) |
| LibriSpeech | 8,149 | Speech (harmonic) |
| Noise-pink | 3,330 | Synthetic (non-harmonic) |
| Noise-brown | 3,292 | Synthetic (non-harmonic) |
| Noise-white | 3,271 | Synthetic (non-harmonic) |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (e.g., `train_000000`, `test_000000`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset name |
| `harmonicity` | Binary label: `yes` (harmonic) or `no` (non-harmonic) |

---

## Example Entries

```json
{"id": "train_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/FSD50k/train/135594.wav", "sampling_rate": 16000, "duration": 6.175, "dataset": "FSD50K", "harmonicity": "no"}

{"id": "train_000001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Harmonicity/wavs/train_000001.wav", "sampling_rate": 16000, "duration": 10.635, "dataset": "LoFiDrums", "harmonicity": "no"}

{"id": "train_000002", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/male9/scales/straight/m9_scales_straight_o.wav", "sampling_rate": 16000, "duration": 11.392, "dataset": "VocalSet", "harmonicity": "yes"}

{"id": "train_000005", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/NSynth/nsynth-train/audio/vocal_synthetic_006-069-075.wav", "sampling_rate": 16000, "duration": 2.214, "dataset": "NSynth", "harmonicity": "yes"}

{"id": "train_000008", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Harmonicity/wavs/train_000008.wav", "sampling_rate": 16000, "duration": 3.545, "dataset": "LoFiDrums", "harmonicity": "no"}
```

---

## Task Usage

### 1. Harmonicity Classification
- **Target field:** `harmonicity`
- **Task:** Predict whether the audio contains harmonic content (`yes`) or non-harmonic content (`no`)

---

## Label Space

### Harmonicity Labels
<details>
<summary>Show 2 available labels:</summary>

`yes` - Harmonic sounds (periodic, pitch-bearing)
`no` - Non-harmonic sounds (aperiodic, noise-like, percussive)

</details>

### Label Interpretation
- **yes (harmonic)**: Sounds with clear periodicity and pitch perception
  - Speech, singing, musical instruments (melodic)
  - Harmonic vocal sounds (laughter, sigh)
  - Harmonic environmental sounds (animal vocalizations, sirens)
- **no (non-harmonic)**: Sounds lacking clear periodicity
  - Noise (white, pink, brown)
  - Percussion and drums
  - Non-harmonic vocal sounds (cough, sneeze, sniff, throat clearing)
  - Non-harmonic environmental sounds (wind, rain, crashes)

---

## Source Datasets

### Harmonic Sources
- **LibriSpeech**: Read speech from audiobooks
- **VocalSet**: Singing voice with various techniques
- **VocalSound**: Laughter, sigh
- **NSynth**: Musical instrument notes
- **FSD50K**: Environmental sounds (filtered for harmonic content)
- **ESC-50**: Environmental sounds (filtered for harmonic content)

### Non-Harmonic Sources
- **Synthetic Noise**: White, pink, brown noise (generated procedurally)
- **LoFiDrums**: Drum samples
- **VocalSound**: Cough, sneeze, sniff, throat clearing
- **FSD50K**: Environmental sounds (filtered for non-harmonic content)
- **ESC-50**: Environmental sounds (filtered for non-harmonic content)

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** (1.5s to 15.0s) with average ~4.7s.
- The dataset is approximately **balanced** (50% harmonic, 50% non-harmonic).
- **Split separation**: Train and test use corresponding splits from source datasets
  - Train: LibriSpeech train-clean-100/360, VocalSet train, NSynth train, FSD50K train
  - Test: LibriSpeech test-clean/other, VocalSet test, NSynth test, FSD50K test
  - LoFiDrums and synthetic noise are shared across splits
- **FSD50K and ESC-50** are filtered based on harmonicity classification TSV files that map sound event labels to harmonic/non-harmonic categories
- **Synthetic noise** is generated on-the-fly (not pre-stored)
- **LoFiDrums** samples are cropped to variable durations
- Most samples reference **original file paths** from source datasets; only noise and LoFiDrums samples write new files
- **Audio processing**:
  - Random cropping within 1.5-15s duration range
  - Mono conversion if stereo
  - Resampling to 16 kHz
  - Peak normalization for LoFiDrums and noise
- The dataset evaluates:
  - **Harmonic structure understanding**: Distinguishing periodic from aperiodic signals
  - **Spectral analysis**: Identifying harmonic vs. broadband spectra
  - **Cross-domain generalization**: Performance across speech, music, environmental sounds, and synthetic audio
- **Evaluation metrics**: Binary accuracy, precision, recall, F1 score
- This is a **fundamental acoustic property** classification task relevant for:
  - Audio analysis and feature extraction
  - Music information retrieval (harmonic vs. percussive separation)
  - Speech/non-speech discrimination
  - Audio quality assessment
  - Source separation preprocessing
