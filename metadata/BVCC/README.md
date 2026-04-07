# BVCC

## Overview
**BVCC** (Blizzard Challenge and Voice Conversion Challenge Corpus) is a large-scale mean opinion score (MOS) prediction benchmark built from English synthetic speech samples collected from past Blizzard Challenges, Voice Conversion Challenges, and public ESPnet-TTS systems, all re-evaluated in a unified listening test. It contains 7,106 utterances with standardized train/dev/test splits and listener ratings, making it a widely used resource for studying automatic perceptual quality assessment of synthesized and converted speech.

## Supported Tasks
1. **Speech Quality Assessment (MOS Prediction)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 4,974 |
| dev | 1,066 |
| test | 1,066 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `mos` | Mean opinion score (1.0-5.0) |

---

## Example Entries

```json
{"id": "sys00691-utt00e6ae6", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/BVCC/wav/sys00691-utt00e6ae6.wav", "sampling_rate": 16000, "duration": 1.821, "mos": 3.375, "dataset": "BVCC"}

{"id": "sys00691-utt04097bc", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/BVCC/wav/sys00691-utt04097bc.wav", "sampling_rate": 16000, "duration": 2.239, "mos": 3.625, "dataset": "BVCC"}

{"id": "sys00691-utt0682e32", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/BVCC/wav/sys00691-utt0682e32.wav", "sampling_rate": 16000, "duration": 2.347, "mos": 3.375, "dataset": "BVCC"}
```

---

## Task Usage

### 1. Speech Quality Assessment (MOS Prediction)
- **Target field:** `mos` (mean opinion score rating)

---

## Label Space

### Mean Opinion Score (MOS)
- **Range**: 1.0 to 5.0
- **Type**: Continuous regression task
- **Average**: ~2.93 (in training set)
- **Interpretation**:
  - **5.0**: Excellent - Imperceptible differences from natural speech
  - **4.0**: Good - Perceptible but not annoying differences
  - **3.0**: Fair - Slightly annoying differences
  - **2.0**: Poor - Annoying differences
  - **1.0**: Bad - Very annoying differences

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration**, typically 1-3 seconds.
- The dataset combines samples from multiple sources:
  - **Blizzard Challenge**: Text-to-speech synthesis systems
  - **Voice Conversion Challenge**: Voice conversion systems
  - **ESPnet-TTS**: Public TTS systems
- All samples were **re-evaluated in a unified listening test** to ensure consistent rating standards across different source challenges.
- The `id` field follows the format `{system_id}-{utterance_id}`, where the system ID indicates which synthesis/conversion system generated the sample.
- MOS scores represent the **average listener rating** from multiple human evaluators.
- This benchmark is widely used for training and evaluating **automatic speech quality assessment** models that predict human-perceived quality without requiring listening tests.
