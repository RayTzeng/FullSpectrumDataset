# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. This task extends the standard ASR dataset by providing **speaking rate estimation** in words per minute (WPM). Each audio file is paired with word count and calculated speaking rate metrics derived from word-level timestamps obtained through Montreal Forced Alignment (MFA). This dataset enables research on prosody analysis, speech tempo modeling, speaker characterization, and speech rate normalization.

## Supported Tasks
1. **Word Counting**
2. **Speaking Rate Estimation**

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 123,936 |
| dev | 2,703 |
| test | 2,620 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Total audio duration (seconds) |
| `dataset` | Source dataset |
| `word_count` | Number of words (excluding silence) |
| `WPM` | Speaking rate in words per minute |

---

## Example Entries

```json
{"id": "1272-128104-0000", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0000.flac", "duration": "5.855", "dataset": "LibriSpeech", "sampling_rate": 16000, "word_count": 17, "WPM": 203.59}

{"id": "1272-128104-0001", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0001.flac", "duration": "4.815", "dataset": "LibriSpeech", "sampling_rate": 16000, "word_count": 11, "WPM": 169.67}

{"id": "1089-134686-0000", "path": "/saltpool0/data/tseng/LibriSpeech/test-clean/1089/134686/1089-134686-0000.flac", "duration": "10.435", "dataset": "LibriSpeech", "sampling_rate": 16000, "word_count": 28, "WPM": 174.64}
```

---

## Task Usage

### 1. Word Counting
- **Target field:** `word_count` (number of words in utterance)

### 2. Speaking Rate Estimation
- **Target field:** `WPM` (speaking rate in words per minute)

---

## Label Space

### Word Count
- **Range**: 1 to ~100+ words per utterance
- **Type**: Integer regression task

### Speaking Rate (WPM)
- **Typical range**: 34-387 WPM (observed in training set)
- **Average**: ~173 WPM
- **Type**: Continuous regression task
- **Normal speaking rate**: 130-170 WPM (typical conversational speech)
- **Fast speaking rate**: 170-200+ WPM

---

## Speaking Rate Calculation

The speaking rate is calculated using word-level timestamps from Montreal Forced Alignment (MFA):

### Formula:
```
WPM = (word_count / speech_duration_seconds) × 60
```

### Calculation Steps:
1. **Extract word timings** from TextGrid files (word tier)
2. **Filter silence markers**: Remove `sil` (silence) and `sp` (short pause) markers
3. **Count words**: Count remaining non-silence words
4. **Calculate speech duration**: Time from first word start to last word end
5. **Compute rate**: Apply formula to get words per minute

### Example:
```
Word count: 17 words
Speech duration: 5.01 seconds (from first to last word)
Speaking rate: (17 / 5.01) × 60 = 203.59 WPM
```

---

## Notes
- All audio files are sampled at **16 kHz**.
- Word-level timestamps are obtained from **Montreal Forced Alignment (MFA)** TextGrid files.
- **Speech duration** used in WPM calculation excludes leading and trailing silence, measuring only from the first spoken word to the last spoken word.
- **Silence markers** (`sil`, `sp`) are filtered out and not counted as words.
- Speaking rate varies significantly across speakers and content:
  - Audiobook narration tends to have consistent speaking rates
  - Individual speaker characteristics affect tempo
  - Content complexity may influence speaking rate
- The dataset is derived from LibriSpeech's **clean subsets** only:
  - **train** (`train-clean-100` and `train-clean-360`)
  - **dev** (`dev-clean`)
  - **test** (`test-clean`)
- Speaking rate estimation can be used for:
  - Speaker characterization and verification
  - Prosody analysis and modeling
  - Speech rate normalization for ASR
  - Detecting fast/slow speakers
  - Audio indexing and retrieval
