# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **dual-purpose** speech understanding: generating rich paralinguistic style captions (describing *how* speech sounds) and performing automatic speech recognition with punctuation (transcribing *what* is said).

## Supported Tasks
1. **Speaking Style Captioning**
2. **Punctuated Automatic Speech Recognition (ASR)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 1,041,167 |
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
| `source` | Source corpus (voxceleb, ears, expresso) |
| `caption` | Paralinguistic style description (how it's spoken) |
| `text` | Transcription with punctuation (what is said) |

---

## Example Entries

```json
{"id": "voxceleb2_dev_aac_id04284_gn81NY9kB7A_00251_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id04284/gn81NY9kB7A/00251_voicefixer.wav", "sampling_rate": 44100, "duration": 4.8, "dataset": "ParaSpeechCaps", "source": "voxceleb", "caption": " In a very clean environment, a female speaker delivers her words hesitantly, exhibiting a husky, medium-pitched voice with a distinct Canadian accent. Her speech is characterized by a measured speed and occasional slurred pronunciation.", "text": " Apparently, one in 100 people have this kind of an aura, so it's almost like autism, which is..."}

{"id": "voxceleb2_dev_aac_id04014_sfXqZEdOBcE_00269_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id04014/sfXqZEdOBcE/00269_voicefixer.wav", "sampling_rate": 44100, "duration": 26.2, "dataset": "ParaSpeechCaps", "source": "voxceleb", "caption": " A male speaker with an American accent delivers authoritative and deep-toned speech, exhibiting a raspy texture to his high-pitched voice. His measured pace ensures clarity in a balanced environment.", "text": " California is no stranger to this fight. For a long time, we've been fighting efforts to reduce vehicle emissions, to improve our environment. And in recent years, we've taken even more aggressive steps. The California vehicle emission standards became the national standards. California drove the United States. The Obama administration responded to the California Air Resources Board."}

{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex02_disgusted_ex04-ex02_disgusted_012_channel1_segment_50.0_59.58", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex02/disgusted/ex04-ex02_disgusted_012_channel1_segment_50.0_59.58.wav", "sampling_rate": 48000, "duration": 9.58, "dataset": "ParaSpeechCaps", "source": "expresso", "caption": " A female speaker with an American accent delivers her words in a disgusted manner, exhibiting a medium-pitched voice with clear articulation in a clean environment.", "text": " I can't believe they would do something like that. It's absolutely ridiculous and completely unacceptable."}
```

---

## Task Usage

### 1. Speaking Style Captioning
- **Input field:** Audio
- **Target field:** `caption` (paralinguistic style description)

### 2. Punctuated ASR
- **Input field:** Audio
- **Target field:** `text` (transcription with punctuation)

---

## Label Space

*These are generation tasks without predefined label spaces.*

### Speaking Style Captioning

Generate natural language descriptions capturing:

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

### Punctuated ASR

Transcribe speech with proper punctuation including:
- **Sentence boundaries**: Periods (.), question marks (?), exclamation points (!)
- **Commas**: Clause separation, pauses (,)
- **Apostrophes**: Contractions (it's, don't, we're)
- **Quotation marks**: Direct speech ("")
- **Ellipsis**: Trailing off or incomplete thoughts (...)
- **Capitalization**: Proper nouns, sentence starts

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled)
- **Dev**: From `dev` split
- **Test**: From `test` split

All splits contain both style captions and punctuated transcriptions for dual-task training.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz, 2-10 seconds)
  - **EARS**: Emotional acted speech (48 kHz, 5-15 seconds)
  - **Expresso**: Expressive read speech (48 kHz, 3-8 seconds)
- **Evaluation metrics**:
  - For style captioning: BLEU, ROUGE, CIDEr, BERTScore, human evaluation
  - For punctuated ASR: WER, punctuation F1, capitalization accuracy, sentence segmentation
- Unlike standard ASR (word-only) or punctuated ASR (text-only), this task captures **full speech spectrum** (both content and style).
- The large training set (1M+ samples) enables training of large-scale models for both tasks.
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.