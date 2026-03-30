# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **48 kHz** for whispered speech samples. This manifest focuses on **Whispered Speech Recognition**, filtering for entries containing the whispered speech where voicing is absent and spectral characteristics differ significantly from normal speech.

## Supported Tasks
1. **Whispered ASR**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 2,534 |
| dev | 162 |
| test | 205 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `source` | Source corpus (ears or expresso) |
| `text` | Ground-truth transcription with punctuation |

---

## Example Entries

```json
{"id": "EARS_audio_p028_sentences_03_whisper", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p028/sentences_03_whisper.wav", "sampling_rate": 48000, "duration": 13.7, "dataset": "ParaSpeechCaps", "source": "ears", "text": "Had it been but one, it had been easy. We have boxed the compass among us. I shall rush out and prevent it. All that is mean slander. The doctor seemed tired and in a hurry."}

{"id": "expresso_audio_48khz_read_ex04_whisper_base_ex04_whisper_00204", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/read/ex04/whisper/base/ex04_whisper_00204.wav", "sampling_rate": 48000, "duration": 2.405, "dataset": "ParaSpeechCaps", "source": "expresso", "text": "I *don't* use it period!"}

{"id": "expresso_audio_48khz_conversational_vad_segmented_ex04-ex03_whisper_ex04-ex03_whisper_003_channel1_segment_181.04_187.22", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/conversational_vad_segmented/ex04-ex03/whisper/ex04-ex03_whisper_003_channel1_segment_181.04_187.22.wav", "sampling_rate": 48000, "duration": 6.18, "dataset": "ParaSpeechCaps", "source": "expresso", "text": " Yeah, it's him. He's a teenager too. It's a pretty good one. We should see it after this."}
```

---

## Task Usage

### 1. Whispered Speech Recognition
- **Target field:** `text` (transcription with punctuation)

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions with punctuation.*

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits filtered for whispered speech:

- **Train**: From `train_base` (PSC-Base) filtered for "whispered" tag
- **Dev**: From `dev` split filtered for "whispered" tag
- **Test**: From `test` split filtered for "whispered" tag

Only entries containing the "whispered" situational tag are included, making this a specialized subset (~1-5% of original dataset).

---

## Notes
- All audio files are sampled at **48 kHz**.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines samples from:
  - **EARS**: Emotional acted speech with whispered mode (48 kHz)
  - **Expresso**: Expressive read speech with whispered utterances (48 kHz)
- **Whispered speech is rare**: Only ~1-5% of ParaSpeechCaps contains whispered speech.
- The dataset includes only human-annotated (PSC-Base) samples in training (no automatically annotated samples for whispered speech).
