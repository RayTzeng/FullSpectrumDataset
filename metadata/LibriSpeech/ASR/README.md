# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. Audio is recorded at **16 kHz** and paired with verbatim transcripts. The dataset is widely used for automatic speech recognition research.

## Supported Tasks
1. **Automatic Speech Recognition (ASR)**

## Dataset Statistics

| Split | # Samples |
|------|-----------|
| train | 281,241 |
| dev | 5,559 |
| test | 5,559 |

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
| `text` | Ground-truth transcription |

---

## Example Entries

```json
{"id": "335-125943-0006", "path": "/saltpool0/data/tseng/LibriSpeech/train-clean-360/335/125943/335-125943-0006.flac", "duration": "8.610", "dataset": "LibriSpeech", "text": "AND I SUPPOSE HE IS NOW MORE PROUD THAN EVER OF HIS PERSONAL APPEARANCE HE IS INDEED SAID THE MAN WITH A POLITE BOW", "sampling_rate": 16000}

{"id": "8803-296082-0049", "path": "/saltpool0/data/tseng/LibriSpeech/train-other-500/8803/296082/8803-296082-0049.flac", "duration": "15.115", "dataset": "LibriSpeech", "text": "PLUNGED IN THE BATTERY SMOKE RIGHT THROUGH THE LINE THEY BROKE COSSACK AND RUSSIAN REELED FROM THE SABRE STROKE SHATTERED AND SUNDERED THEN THEY RODE BACK BUT NOT NOT THE SIX HUNDRED", "sampling_rate": 16000}

{"id": "49-121052-0066", "path": "/saltpool0/data/tseng/LibriSpeech/train-other-500/49/121052/49-121052-0066.flac", "duration": "16.600", "dataset": "LibriSpeech", "text": "LUIGI'S HANDS EXCELLENCY THE FRENCHMAN'S CARRIAGE PASSED SEVERAL TIMES THE ONE IN WHICH WAS TERESA THE CHIEF'S MISTRESS YES THE FRENCHMAN THREW HER A BOUQUET TERESA RETURNED IT ALL THIS WITH THE CONSENT OF THE CHIEF WHO WAS IN THE CARRIAGE", "sampling_rate": 16000}
```

---

## Task Usage

### 1. Automatic Speech Recognition (ASR)
- **Target field:** `text`

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Transcriptions are in **all uppercase** without punctuation.
- The dataset contains the following splits:
  - **train** (containing `train-clean-100`, `train-clean-360`, `train-other-500`)
  - **dev** (containing `dev-clean`, `dev-other`)
  - **test** (containing `test-clean`, `test-other`)