# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, Expresso, and Emilia, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Speech Emotion Recognition**, a multi-label classification task identifying emotional states from speech across 18 emotion categories.

## Supported Tasks
1. **Speech Emotion Recognition**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 85,693 |
| dev | 1,142 |
| test | 1,158 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (44100 or 48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `source` | Source corpus (voxceleb, ears, expresso, emilia) |
| `emotions` | List of target emotions found in the audio |

---

## Example Entries

```json
{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex02_disgusted_ex04-ex02_disgusted_012_channel1_segment_50.0_59.58", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex02/disgusted/ex04-ex02_disgusted_012_channel1_segment_50.0_59.58.wav", "sampling_rate": 48000, "duration": 9.58, "dataset": "ParaSpeechCaps", "source": "expresso", "emotions": ["disgusted"]}

{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex01_sympathetic-sad_ex04-ex01_sympathetic-sad_013_channel1_segment_144.12_155.35", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex01/sympathetic-sad/ex04-ex01_sympathetic-sad_013_channel1_segment_144.12_155.35.wav", "sampling_rate": 48000, "duration": 11.23, "dataset": "ParaSpeechCaps", "source": "expresso", "emotions": ["sympathetic"]}

{"id": "EN_B00010_S03798", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00010/EN_B00010_S03798/mp3/EN_B00010_S03798_W000153.mp3", "sampling_rate": 44100, "duration": 5.909, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["angry", "scared"]}
```

---

## Task Usage

### 1. Speech Emotion Recognition
- **Target field:** `emotions` (list of emotion labels)

---

## Label Space

### Emotion Labels
<details>
<summary>Show 18 available emotion labels:</summary>

`admiring`, `angry`, `anxious`, `awed`, `bored`, `calm`, `confused`, `desirous`, `disgusted`, `enthusiastic`, `guilt`, `happy`, `pained`, `saddened`, `sarcastic`, `scared`, `sleepy`, `sympathetic`
</details>

### Multi-label Classification

This is a **multi-label** classification task:
- Each sample can have **one or more** emotion labels
- The `emotions` field is a **list** (e.g., `["angry", "scared"]`)
- Approximately **5-10%** of samples have multiple emotions
- Models must predict all applicable emotions for each utterance

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits filtered for emotion content:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled), filtered for 18 target emotions
- **Dev**: From `dev` split, filtered for 18 target emotions
- **Test**: From `test` split, filtered for 18 target emotions

Only entries containing at least one of the 18 target emotions are included.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-20 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional audiobooks (44.1 kHz)
- This is a **multi-label classification** task where each sample can have one or more emotions.
- The `emotions` field is stored as a **list** to accommodate multiple simultaneous emotions.
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.
