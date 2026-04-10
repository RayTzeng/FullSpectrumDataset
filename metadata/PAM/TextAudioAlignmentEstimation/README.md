# PAM

## Overview
**PAM** (Prompting Audio-Language Models for Audio Quality Assessment) is a benchmark for perceptual audio quality assessment of generated audio. It contains **500 sound clips** and **500 music clips**, including both natural and generated samples, paired with text descriptions and human overall-quality ratings for evaluating how well automatic metrics align with listener judgments. This task focuses on **text-audio alignment estimation**, where models assess how well generated audio matches its text prompt based on human ratings.

## Supported Tasks
1. **Text-Audio Alignment Estimation (MOS Prediction)**

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
| `prompt` | Text description used to generate the audio |
| `alignment_MOS` | Text-audio alignment mean opinion score (1.0-5.0) |

---

## Example Entries

```json
{"id": "audio_audiogen_m_generated_audio_index_106", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/audio/audiogen_m/generated_audio_index_106.wav", "sampling_rate": 16000, "duration": 5.0, "dataset": "PAM-Audio", "prompt": "a baby is laughing while a young girl speaks repeatedly and an adult female chuckles softly", "alignment_MOS": 4.0}

{"id": "music_musicgen_large_generated_music_index_042", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/music/musicgen_large/generated_music_index_042.wav", "sampling_rate": 32000, "duration": 8.5, "dataset": "PAM-Music", "prompt": "A digital drum is playing a simple rhythm along with a synth bassline. A very pregnant synth lead is playing a catchy and repeating melody in the higher register.", "alignment_MOS": 3.5}

{"id": "audio_real_real_audio_index_015", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PAM/human_eval/audio/real/real_audio_index_015.wav", "sampling_rate": 44100, "duration": 6.3, "dataset": "PAM-Audio", "prompt": "wind blows hard then a man speaks", "alignment_MOS": 5.0}
```

---

## Task Usage

### 1. Text-Audio Alignment Estimation (MOS Prediction)
- **Input fields:** `prompt` (text description)
- **Target field:** `alignment_MOS` (text-audio alignment score)

---

## Label Space

### Text-Audio Alignment MOS
- **Range**: 1.0 to 5.0
- **Type**: Continuous regression task
- **Average**: ~3.34 (audio), ~3.23 (music)
- **Interpretation**:
  - **5.0**: Excellent - Audio perfectly matches the text description
  - **4.0**: Good - Audio aligns well with most aspects of the prompt
  - **3.0**: Fair - Audio partially matches the description
  - **2.0**: Poor - Audio has limited alignment with the prompt
  - **1.0**: Bad - Audio does not match the description at all

---

## Alignment Assessment Criteria

Human raters evaluate **text-audio alignment** based on how well the generated audio matches the prompt's:
- **Sound events**: Specified sounds, actions, or sources (e.g., "baby laughing", "wind blowing")
- **Instrumentation**: Musical instruments and ensembles (for music prompts)
- **Genre/Style**: Musical genre or audio category
- **Temporal structure**: Sequence of events described in the prompt
- **Acoustic characteristics**: Volume, pitch, timbre, or other sound qualities
- **Contextual elements**: Background sounds, environmental acoustics, or scene description

---

## Example Prompts

### Audio Prompts
- "a baby is laughing while a young girl speaks repeatedly and an adult female chuckles softly"
- "a bell ringing followed by a camera muffling then plastic scrapping on a wooden surface proceeded by a clock ticking"
- "wind blows hard then a man speaks"

### Music Prompts
- "A digital drum is playing a simple rhythm along with a synth bassline. A very pregnant synth lead is playing a catchy and repeating melody in the higher register. In the background you can hear feet stumping noises. This song may be playing in a club."
- "A male singer sings this Latin dance melody. The tempo is fast with a harpist playing fast passages with an acoustic guitar strumming rhythm. The song is emotional and energetic."

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
- MOS scores represent **human ratings for text-audio alignment** (REL column from scores.csv).
- The dataset includes **100 unique prompts** for audio and **100 unique prompts** for music.
- Prompts are preserved exactly as provided in the original scores CSV.
- Train/test split is randomized with a 9:1 ratio (seed=42 for reproducibility).
- The complete dataset is available in `all.jsonl.gz` (1,000 samples).
- Each sample includes the original text prompt, making it suitable for **multimodal** evaluation tasks.
