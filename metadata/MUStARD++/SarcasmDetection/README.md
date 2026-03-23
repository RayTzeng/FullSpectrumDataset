# MUStARD++ - Sarcasm Detection in Speech

## Overview
**MUStARD++** is a multimodal sarcasm dataset built from sitcom dialogue clips, where each instance includes a target utterance together with its conversational context and aligned text, audio, and visual information for studying sarcasm in realistic interactions. This task focuses on **binary sarcasm detection** in speech, determining whether an utterance is sarcastic or not.

## Supported Tasks
1. **Sarcasm Detection in Speech**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 962 |
| test | 239 |

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
| `sarcasm` | Ground-truth sarcasm detection label |
| `sarcasm_type` | Type of sarcasm (see Sarcasm Type Classification task) |
| `implicit_emotion` | Underlying emotion conveyed |
| `explicit_emotion` | Surface-level emotion expressed |

---

## Example Entries

```json
{"id": "1_4352_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/1_4352_u.wav", "sampling_rate": 16000, "duration": 7.018688, "dataset": "MUStARD++", "sarcasm": "no", "sarcasm_type": "none", "implicit_emotion": "sad", "explicit_emotion": "sad"}

{"id": "3_S03E03_126_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/3_S03E03_126_u.wav", "sampling_rate": 16000, "duration": 3.073313, "dataset": "MUStARD++", "sarcasm": "yes", "sarcasm_type": "propositional", "implicit_emotion": "disgust", "explicit_emotion": "surprise"}

{"id": "1_S10E03_282_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MUStARD++/bigdata/final_utterance_videos_wav/1_S10E03_282_u.wav", "sampling_rate": 16000, "duration": 4.308, "dataset": "MUStARD++", "sarcasm": "no", "sarcasm_type": "none", "implicit_emotion": "fear", "explicit_emotion": "fear"}
```

---

## Task Usage

### 1. Sarcasm Detection in Speech
- **Target field:** `sarcasm` (binary sarcasm label)

---

## Label Space

### Sarcasm Labels
<details>
<summary>Show 2 available labels:</summary>

`yes`, `no`

</details>

### Label Definitions
<details>
<summary>Show detailed descriptions for each label:</summary>

- **yes**: The utterance is sarcastic, conveying meaning that is contrary to or different from the literal interpretation
- **no**: The utterance is non-sarcastic, with the literal meaning matching the speaker's intent

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- This is a **binary classification** task where each utterance is labeled as sarcastic or non-sarcastic.
- The dataset includes both the target utterance and conversational context, making it suitable for studying context-dependent sarcasm.
- Duration varies across samples, typically ranging from 2 to 11 seconds.
- Each sample includes additional metadata such as `sarcasm_type`, `implicit_emotion`, and `explicit_emotion`, which can provide additional insights but are not the primary target for this task.
- When `sarcasm` is "no", the `sarcasm_type` field is set to "none".
- The data is sourced from sitcom dialogue, providing naturalistic conversational speech with diverse speaking styles and emotional expressions.
- This is part of a multimodal dataset that also includes text and visual information, though this manifest focuses on the audio modality.
