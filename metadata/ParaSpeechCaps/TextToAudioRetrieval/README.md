# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Text-to-Audio Retrieval**, where models must retrieve the correct audio sample given a paralinguistic style caption from among multiple audio candidates.

## Supported Tasks
1. **Text-to-Audio Retrieval**

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
| `id` | Unique identifier (from ground truth audio) |
| `paths` | List of paths to audio candidates (ground truth + distractors) |
| `sampling_rates` | List of sampling rates for each audio candidate (Hz) |
| `durations` | List of durations for each audio candidate (seconds) |
| `caption` | Text query describing paralinguistic style |
| `label` | Index of the correct audio in the paths list (0-indexed) |

---

## Example Entries

```json
{"id": "voxceleb2_dev_aac_id04284_gn81NY9kB7A_00251_voicefixer", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p084/sentences_02_whisper.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id04284/gn81NY9kB7A/00251_voicefixer.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id08348/H8FkOhjVL9I/00136_voicefixer.wav"], "sampling_rates": [48000, 44100, 44100], "durations": [14.4, 4.8, 8.6], "caption": " In a very clean environment, a female speaker delivers her words hesitantly, exhibiting a husky, medium-pitched voice with a distinct Canadian accent. Her speech is characterized by a measured speed and occasional slurred pronunciation.", "label": 1}

{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex02_disgusted_ex04-ex02_disgusted_012_channel1_segment_50.0_59.58", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex02/disgusted/ex04-ex02_disgusted_012_channel1_segment_50.0_59.58.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id01234/abcd1234/00100_voicefixer.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p025/sentences_05_normal.wav"], "sampling_rates": [48000, 44100, 48000], "durations": [9.58, 6.2, 12.1], "caption": " A female speaker with an American accent delivers her words in a disgusted manner, exhibiting a medium-pitched voice with clear articulation in a clean environment.", "label": 0}

{"id": "EN_B00010_S03798", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex01-ex03/calm/ex01-ex03_calm_007_channel2_segment_22.4_28.1.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id05678/xyz5678/00250_voicefixer.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00010/EN_B00010_S03798/mp3/EN_B00010_S03798_W000153.mp3"], "sampling_rates": [48000, 44100, 44100], "durations": [5.7, 7.3, 5.909], "caption": " In a very clean environment, a female speaker delivers her words with angry and scared emotions, exhibiting a high-pitched, stressful voice with rapid articulation.", "label": 2}
```

---

## Task Usage

### 1. Text-to-Audio Retrieval
- **Input:** Text caption describing paralinguistic style
- **Target field:** `label` (index of correct audio)
- **Candidates:** Multiple audio files in `paths` list (typically 3 candidates)

---

## Label Space

*This is a retrieval task without a predefined label space. The `label` field indicates which audio in the `paths` list matches the query caption.*

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

All splits are designed for cross-modal retrieval evaluation with randomly sampled audio distractors from the same split.

---

## Notes
- Audio candidates may have **different sampling rates** (44.1 kHz or 48 kHz) depending on source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional speech from audiobooks (44.1 kHz)
- **Retrieval format**: Given a text caption query, the model must select the correct audio from typically 3 candidates.
- **Label format**: The `label` field is a 0-indexed integer indicating which position in `paths` contains the ground truth audio.
- **Distractor sampling**: 2 incorrect audio files are randomly sampled from other entries in the same split.
- The ground truth audio can appear at **any position** in the candidate list (indicated by `label`).
- Captions are **content-agnostic** - they describe *how* speech sounds, not *what* is said.