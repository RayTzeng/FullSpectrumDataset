# PAM

## Overview
**PAM** (Prompting Audio-Language Models for Audio Quality Assessment) is a benchmark for perceptual audio quality assessment of generated audio. It contains **500 sound clips** and **500 music clips**, including both natural and generated samples, paired with text descriptions and human overall-quality ratings for evaluating how well automatic metrics align with listener judgments. This task focuses on **audio quality assessment**, where models predict the overall perceptual quality of audio clips based on human ratings.

## Supported Tasks
1. **Audio Quality Assessment (MOS Prediction)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 900 |
| test | 100 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (PAM-Audio or PAM-Music) |
| `quality_MOS` | Overall quality mean opinion score (1.0-5.0) |

---

## Example Entries

```json
{"id": "audio_audiogen_m_generated_audio_index_106", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/audio/audiogen_m/generated_audio_index_106.wav", "sampling_rate": 16000, "duration": 5.0, "dataset": "PAM-Audio", "quality_MOS": 4.4}

{"id": "music_musicgen_large_generated_music_index_042", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/music/musicgen_large/generated_music_index_042.wav", "sampling_rate": 32000, "duration": 8.5, "dataset": "PAM-Music", "quality_MOS": 3.2}

{"id": "audio_real_real_audio_index_015", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/audio/real/real_audio_index_015.wav", "sampling_rate": 44100, "duration": 6.3, "dataset": "PAM-Audio", "quality_MOS": 4.7}
```

---

## Task Usage

### 1. Audio Quality Assessment (MOS Prediction)
- **Target field:** `quality_MOS` (overall perceptual quality score)

---

## Label Space

### Audio Quality MOS
- **Range**: 1.0 to 5.0
- **Type**: Continuous regression task
- **Average**: ~3.04 (audio), ~2.66 (music)
- **Interpretation**:
  - **5.0**: Excellent - High-quality audio with professional clarity
  - **4.0**: Good - Pleasant audio with minor imperfections
  - **3.0**: Fair - Acceptable audio with noticeable issues
  - **2.0**: Poor - Audio with significant quality problems
  - **1.0**: Bad - Very low quality or incoherent audio

---

## Quality Assessment Criteria

Human raters evaluate the **overall audio quality** based on:
- **Fidelity**: Audio clarity and resolution
- **Naturalness**: How realistic and authentic the audio sounds
- **Artifact presence**: Absence of glitches, distortions, or unnatural sounds
- **Production quality**: Overall listening experience and polish

---

## Notes
- Audio files have **mixed sampling rates** (16 kHz for most generated audio, varies for real samples).
- Audio clips have **variable duration**, typically 5-10 seconds.
- The dataset contains samples from multiple generative models:
  - **Audio models**: audiogen_m, audiolm_l, audiolm_l2, e2edef
  - **Music models**: audioldm2, musicgen_large, musicgen_melody, musicldm
  - **Real samples**: Ground-truth reference audio and music for comparison
- The `dataset` field distinguishes between "PAM-Audio" (sound effects) and "PAM-Music" (music clips).
- The `id` field follows the format `{dataset_type}_{model}_{file_name}`.
- MOS scores represent **human ratings for overall quality** (OVL column from scores.csv).
- The dataset includes **100 unique prompts** for audio and **100 unique prompts** for music.
- Train/test split is randomized with a 9:1 ratio (seed=42 for reproducibility).
- The complete dataset is available in `all.jsonl.gz` (1,000 samples).
