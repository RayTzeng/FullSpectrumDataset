# ASCEND

## Overview
**ASCEND** (A Spontaneous Chinese-English Dataset) is a speech corpus for Mandarin–English code-switching ASR, built from **spontaneous multi-turn conversational dialogue** rather than read speech. The dataset contains approximately **10.6 hours** of audio from **23 bilingual speakers** engaging in natural conversations that seamlessly mix Chinese (Mandarin) and English. Unlike scripted code-switching datasets, ASCEND captures authentic patterns of language mixing that occur in real-world bilingual communication, making it particularly valuable for studying recognition of naturally code-switched conversational speech. Audio is recorded at **16 kHz** and includes utterance-level language labels indicating whether each segment is primarily Chinese, primarily English, or code-mixed.

## Supported Tasks
1. **Code-Switching Automatic Speech Recognition (CS-ASR)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 9,869 |
| dev | 1,130 |
| test | 1,315 |

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
| `text` | Ground-truth transcription (mixed Chinese and English) |
| `language` | Language label: `zh` (Chinese), `en` (English), or `mixed` (code-switched) |

---

## Example Entries

```json
{"id": "ascend_train_00000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/ASCEND/train/00000.wav", "sampling_rate": 16000, "duration": "1.560", "dataset": "ASCEND", "text": "我刚刚开始record", "language": "mixed"}

{"id": "ascend_train_00003", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/ASCEND/train/00003.wav", "sampling_rate": 16000, "duration": "5.700", "dataset": "ASCEND", "text": "今天呢我非常希望能够通过这个机会去跟你make friends", "language": "mixed"}

{"id": "ascend_validation_00001", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/ASCEND/validation/00001.wav", "sampling_rate": 16000, "duration": "4.600", "dataset": "ASCEND", "text": "小朋友我回想一下when i was in elementary school", "language": "mixed"}

{"id": "ascend_validation_00002", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/ASCEND/validation/00002.wav", "sampling_rate": 16000, "duration": "1.740", "dataset": "ASCEND", "text": "like year three", "language": "en"}

{"id": "ascend_train_00004", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/ASCEND/train/00004.wav", "sampling_rate": 16000, "duration": "2.020", "dataset": "ASCEND", "text": "嗯你知道就是", "language": "zh"}
```

---

## Task Usage

### 1. Code-Switching Automatic Speech Recognition (CS-ASR)
- **Target field:** `text` (mixed Chinese-English transcription)

---

## Label Space

### Language Labels
<details>
<summary>Show 3 language categories:</summary>

`zh` - Chinese (Mandarin) only
`en` - English only
`mixed` - Code-switched (both languages present in utterance)

</details>

### Language Distribution (Training Set)
- **Chinese-only (`zh`)**: 4,799 samples (48.6%)
- **Code-switched (`mixed`)**: 2,739 samples (27.8%)
- **English-only (`en`)**: 2,331 samples (23.6%)

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration**, typically ranging from 0.14 to 15 seconds, with an average of ~3.2 seconds.
- Total dataset duration: **~10.6 hours** across all splits.
- Transcriptions use **mixed-script representation**:
  - Chinese text appears in **simplified Chinese characters** (汉字)
  - English text appears in **lowercase Latin alphabet**
  - No explicit language boundary markers are used — languages are interleaved naturally
- The dataset captures **spontaneous conversational speech** including:
  - Natural disfluencies (嗯, 呃, etc.)
  - Intra-sentential code-switching (switching within a sentence)
  - Inter-sentential code-switching (switching between sentences)
  - Conversational fillers and hesitations
- All recordings are from **23 bilingual speakers** engaged in multi-turn conversations.
- The `language` field provides utterance-level labels but does not mark intra-utterance switching points:
  - `zh`: Utterance contains only Mandarin Chinese
  - `en`: Utterance contains only English
  - `mixed`: Utterance contains both languages (code-switched)
- Code-switching patterns in this dataset reflect **naturalistic bilingual communication** rather than artificially constructed language mixing.
- The dataset is particularly challenging for ASR systems due to:
  - **Spontaneous speech characteristics**: Incomplete sentences, restarts, and overlapping speech
  - **Acoustic code-switching**: Rapid transitions between different phonological systems
  - **Lexical ambiguity**: Words that could belong to either language
  - **Prosodic variation**: Different intonation patterns for Chinese and English segments
- Applications include:
  - Training code-switching ASR models for bilingual communities
  - Studying naturalistic language mixing patterns
  - Developing language identification systems for mixed-language speech
  - Analyzing conversational dynamics in bilingual dialogue
  - Building robust multilingual speech recognition systems
- The dataset uses the standard HuggingFace split names: `train`, `validation` (mapped to `dev` in this manifest), and `test`.
- Audio extraction was performed from the original **CAiRE/ASCEND** dataset on HuggingFace, with resampling to 16 kHz.
