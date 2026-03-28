# GigaSpeech

## Overview
**GigaSpeech** is a large-scale, multi-domain English automatic speech recognition (ASR) corpus built from audiobooks, podcasts, and YouTube audio. The dataset covers both read and spontaneous speech across a wide range of topics, providing 10,000 hours of high-quality transcribed audio. This version includes **punctuated transcriptions** where punctuation marks and proper capitalization have been restored. This dataset uses the **medium** split of GigaSpeech.

## Supported Tasks
1. **Punctuated Automatic Speech Recognition**

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 910,140 |
| dev | 6,750 |
| test | 25,619 |

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
| `text` | Ground-truth transcription with punctuation |

---

## Example Entries

```json
{"id": "YOU1000000044_S0001436", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GigaSpeech/Correct-ASR/validation/YOU1000000044_S0001436.wav", "duration": "8.260", "dataset": "GigaSpeech", "text": "A lot of it been the marketing our site, that, really is just getting people to watch it, ah that's been the biggest part of all for growing.", "sampling_rate": 16000}

{"id": "POD1000000017_S0000124", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GigaSpeech/Correct-ASR/validation/POD1000000017_S0000124.wav", "duration": "4.700", "dataset": "GigaSpeech", "text": "Because showbiz in the eighteen thirties looked like this.", "sampling_rate": 16000}

{"id": "YOU1000000134_S0000042", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GigaSpeech/Correct-ASR/test/YOU1000000134_S0000042.wav", "duration": "9.871", "dataset": "GigaSpeech", "text": "One of their Stanford professors used to say, well, the difference between the two of them was that sergei would just burst into my office without asking. Larry would knock and then burst in.", "sampling_rate": 16000}
```

---

## Task Usage

### 1. Punctuated Automatic Speech Recognition
- **Target field:** `text`

---

## Label Space

*This task does not have a predefined label space - it generates open-vocabulary text transcriptions with punctuation.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Transcriptions include **proper punctuation** (commas, periods, etc.) and **mixed case** formatting.
- Models must predict both word sequences and punctuation marks.
- The dataset uses the **medium** split from GigaSpeech, which provides approximately 10,000 hours of audio.
- Audio sources include:
  - **Audiobooks** (read speech)
  - **Podcasts** (spontaneous speech)
  - **YouTube** (varied content)
- Special tags are used for non-speech segments:
  - `<MUSIC>` - Musical content
  - `<OTHER>` - Other non-speech audio
- The dataset covers diverse topics and speaking styles, making it suitable for training robust punctuated ASR models.
- ID prefixes indicate source: `YOU` (YouTube), `POD` (Podcast), `AUD` (Audiobook).
- Punctuation restoration enables more natural and readable transcriptions suitable for real-world applications.
