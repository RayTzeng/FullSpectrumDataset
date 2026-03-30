# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Audio-to-Text Retrieval**, where models must retrieve the correct paralinguistic style caption given an audio sample from among multiple text candidates.

## Supported Tasks
1. **Audio-to-Text Retrieval**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 80,000 |
| dev | 11,967 |
| test | 14,756 |

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
| `ground_truth` | Correct paralinguistic style caption |
| `distractors` | List of 3 incorrect captions from other samples |

---

## Example Entries

```json
{"id": "voxceleb2_dev_aac_id04284_gn81NY9kB7A_00251_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id04284/gn81NY9kB7A/00251_voicefixer.wav", "sampling_rate": 44100, "duration": 4.8, "dataset": "ParaSpeechCaps", "ground_truth": " In a very clean environment, a female speaker delivers her words hesitantly, exhibiting a husky, medium-pitched voice with a distinct Canadian accent. Her speech is characterized by a measured speed and occasional slurred pronunciation.", "distractors": [" In a slightly noisy environment, a male speaker delivers a flowing, guttural, and deep-pitched speech with a distinct American accent. His speech is characterized by a measured speed and slurred articulation, resulting in a low-pitched and expressive tone.", " A male speaker with an American accent delivers his words at a measured speed in a loud voice, despite the presence of a noisy environment. His speech flows smoothly with a medium-pitched tone.", " A male speaker with a deep, flowing Jamaican accent delivers his words at a measured speed in a slightly clean environment. His voice has a medium-pitched tone."]}

{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex02_disgusted_ex04-ex02_disgusted_012_channel1_segment_50.0_59.58", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex02/disgusted/ex04-ex02_disgusted_012_channel1_segment_50.0_59.58.wav", "sampling_rate": 48000, "duration": 9.58, "dataset": "ParaSpeechCaps", "ground_truth": " A female speaker with an American accent delivers her words in a disgusted manner, exhibiting a medium-pitched voice with clear articulation in a clean environment.", "distractors": [" In a balanced environment, a male speaker delivers authoritative speech with a raspy, high-pitched voice and an American accent at a measured pace.", " A female speaker delivers calm, flowing speech in a clean environment with a high-pitched, breathy voice and a British accent.", " A male speaker with a deep, flowing Canadian accent delivers his words at a measured speed in a slightly clean environment."]}

{"id": "EN_B00010_S03798", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00010/EN_B00010_S03798/mp3/EN_B00010_S03798_W000153.mp3", "sampling_rate": 44100, "duration": 5.909, "dataset": "ParaSpeechCaps", "ground_truth": " In a very clean environment, a female speaker delivers her words with angry and scared emotions, exhibiting a high-pitched, stressful voice with rapid articulation.", "distractors": [" A male speaker with a low-pitched, calm voice delivers his words at a slow, measured pace in a clean environment.", " In a noisy environment, a female speaker delivers enthusiastic speech with a medium-pitched voice and flowing articulation.", " A male speaker with a deep, breathy voice delivers hesitant speech in a slightly reverberant environment."]}
```

---

## Task Usage

### 1. Audio-to-Text Retrieval
- **Input:** Audio file
- **Target field:** `ground_truth` (correct paralinguistic caption)
- **Candidates:** `ground_truth` + `distractors` (4 total candidates)

---

## Label Space

*This is a retrieval task without a predefined label space. Each audio has a unique paralinguistic style caption describing how it is spoken.*

### Caption Content

Captions describe **paralinguistic style** across multiple dimensions:

<details>
<summary>Show 59 style tags covered:</summary>

**Intrinsic Traits (Speaker characteristics)**:
- **Gender**: male, female
- **Pitch**: low-pitched, medium-pitched, high-pitched
- **Accent**: American, British, Canadian, Australian, Jamaican, etc.
- **Voice quality**: husky, breathy, nasal, guttural, raspy, etc.

**Situational Styles (Utterance-level)**:
- **Speaking speed**: slow, measured, fast, rushed
- **Articulation**: clear, slurred, mumbled
- **Emotion**: happy, sad, angry, calm, anxious, scared, enthusiastic, disgusted, etc. (18 emotions)
- **Environment**: clean, noisy, reverberant
- **Volume**: quiet, normal, loud
- **Speech flow**: hesitant, flowing, choppy

**Total**: 59 distinct style tags combining intrinsic and situational characteristics

</details>

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled)
- **Dev**: From `dev` split
- **Test**: From `test` split

All splits are designed for cross-modal retrieval evaluation with randomly sampled distractors from the same split.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional speech from audiobooks (44.1 kHz)
- **Retrieval format**: Given an audio query, the model must select the correct caption from 4 candidates (1 correct + 3 distractors).
- Captions are **content-agnostic** - they describe *how* speech sounds, not *what* is said.
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.

