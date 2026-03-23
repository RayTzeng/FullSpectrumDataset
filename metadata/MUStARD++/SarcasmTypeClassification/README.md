# MUStARD++ - Sarcasm Type Classification

## Overview
**MUStARD++** is a multimodal sarcasm dataset built from sitcom dialogue clips, where each instance includes a target utterance together with its conversational context and aligned text, audio, and visual information for studying sarcasm in realistic interactions. This task focuses on **sarcasm type classification**, categorizing sarcastic utterances into four distinct types based on how the sarcasm is conveyed.

## Supported Tasks
1. **Sarcasm Type Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 481 |
| test | 120 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `sarcasm` | Binary sarcasm label (always "yes" for this task) |
| `sarcasm_type` | Ground-truth sarcasm type label |
| `implicit_emotion` | Underlying emotion conveyed |
| `explicit_emotion` | Surface-level emotion expressed |

---

## Example Entries

```json
{"id": "1_6020_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/1_6020_u.wav", "sampling_rate": 16000, "duration": 11.008, "dataset": "MUStARD++", "sarcasm": "yes", "sarcasm_type": "propositional", "implicit_emotion": "anger", "explicit_emotion": "neutral"}

{"id": "1_S12E01_139_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/1_S12E01_139_u.wav", "sampling_rate": 16000, "duration": 2.269312, "dataset": "MUStARD++", "sarcasm": "yes", "sarcasm_type": "propositional", "implicit_emotion": "disgust", "explicit_emotion": "neutral"}

{"id": "1_S12E12_043_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/1_S12E12_043_u.wav", "sampling_rate": 16000, "duration": 3.090688, "dataset": "MUStARD++", "sarcasm": "yes", "sarcasm_type": "propositional", "implicit_emotion": "disgust", "explicit_emotion": "excitement"}
```

---

## Task Usage

### 1. Sarcasm Type Classification
- **Target field:** `sarcasm_type` (sarcasm type category label)

---

## Label Space

### Sarcasm Type Labels
<details>
<summary>Show 4 available labels:</summary>

`propositional`, `embedded`, `illocutionary`, `like_prefixed`

</details>

### Label Definitions
<details>
<summary>Show detailed descriptions for each sarcasm type:</summary>

- **propositional**: Context-dependent sarcasm that requires conversational context to be detected. The utterance may seem non-sarcastic without context information.
  - Example: "Your plan sounds fantastic!" (may seem sincere without knowing the plan failed)

- **embedded**: Sarcasm with embedded incongruity within the utterance itself; the text alone is sufficient to detect sarcasm due to internal contradictions or absurdity.
  - Example: "It's so much fun working at 2 am at night"

- **like_prefixed**: Sarcasm that uses a like-phrase to show the incongruity of the argument being stated, often beginning with "Like..."
  - Example: "Like you care"

- **illocutionary**: Sarcasm conveyed through non-textual cues (prosody, intonation, visual gestures) while the text itself is often the opposite of the attitude. The audio or visual modality clearly shows the sarcasm even when the text appears sincere.
  - Example: Rolling eyes while saying "Yeah right" (text is sincere, but prosodic features and eye movement reveal sarcasm)

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- This is a **multi-class classification** task with four sarcasm type categories.
- All samples in this task are sarcastic utterances (`sarcasm` field is always "yes"), unlike the Sarcasm Detection task which includes both sarcastic and non-sarcastic samples.
- The four sarcasm types differ in how they convey sarcasm: through context (propositional), internal text (embedded), phrase structure (like_prefixed), or non-textual cues (illocutionary).
- Duration varies across samples, typically ranging from 2 to 11 seconds.
- **Propositional** sarcasm requires context understanding, making it particularly challenging for models without access to conversational history.
- **Illocutionary** sarcasm is especially relevant for audio analysis, as the sarcasm is primarily conveyed through prosodic features rather than text.
- Each sample includes `implicit_emotion` and `explicit_emotion` fields, which can reveal the mismatch between surface-level and underlying emotional states typical in sarcastic speech.
- The data is sourced from sitcom dialogue, providing naturalistic conversational speech with diverse speaking styles.
- This is part of a multimodal dataset that also includes text and visual information, though this manifest focuses on the audio modality.
