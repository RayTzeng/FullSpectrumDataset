# GigaSpeech

## Overview
**GigaSpeech** is a large-scale, multi-domain English automatic speech recognition (ASR) corpus built from audiobooks, podcasts, and YouTube audio. The dataset covers both read and spontaneous speech across a wide range of topics, providing 10,000 hours of high-quality transcribed audio. It is widely used as a benchmark for large-scale ASR research. This dataset uses the **medium** split of GigaSpeech. Audio is recorded at **16 kHz** and paired with verbatim transcripts.

## Supported Tasks
1. **Automatic Speech Recognition (ASR)**

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
| `text` | Ground-truth transcription |

---

## Example Entries

```json
{"id": "YOU1000000044_S0001436", "path": "/saltpool0/scratch/tseng/hf_cache/datasets/downloads/extracted/68fe3b3fd16a6142e7d456f4dfd3a49f805a1c49ef88e782a5311a2cae31625c/dev_chunks_0000/YOU1000000044_S0001436.wav", "duration": "8.260", "dataset": "GigaSpeech", "text": "A LOT OF IT BEEN THE MARKETING OUR SITE THAT REALLY IS JUST GETTING PEOPLE TO WATCH IT AH THAT'S BEEN THE BIGGEST PART OF ALL FOR GROWING", "sampling_rate": 16000}

{"id": "POD1000000017_S0000124", "path": "/saltpool0/scratch/tseng/hf_cache/datasets/downloads/extracted/68fe3b3fd16a6142e7d456f4dfd3a49f805a1c49ef88e782a5311a2cae31625c/dev_chunks_0000/POD1000000017_S0000124.wav", "duration": "4.700", "dataset": "GigaSpeech", "text": "BECAUSE SHOWBIZ IN THE EIGHTEEN THIRTIES LOOKED LIKE THIS", "sampling_rate": 16000}

{"id": "YOU1000000134_S0000042", "path": "/saltpool0/scratch/tseng/hf_cache/datasets/downloads/extracted/4a35b557bb1e258ee4b920290105c0d209fed970fdacc2f1c54cb012386f437c/test_chunks_0000/YOU1000000134_S0000042.wav", "duration": "9.871", "dataset": "GigaSpeech", "text": "ONE OF THEIR STANFORD PROFESSORS USED TO SAY WELL THE DIFFERENCE BETWEEN THE TWO OF THEM WAS THAT SERGEI WOULD JUST BURST INTO MY OFFICE WITHOUT ASKING LARRY WOULD KNOCK AND THEN BURST IN", "sampling_rate": 16000}
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
- Transcriptions are in **all uppercase** and the original punctuation are removed.
- The dataset uses the **medium** split from GigaSpeech, which provides approximately 10,000 hours of audio.
- Audio sources include:
  - **Audiobooks** (read speech)
  - **Podcasts** (spontaneous speech)
  - **YouTube** (varied content)
- Some samples may contain empty transcriptions (non-speech segments like music or silence).
- The dataset covers diverse topics and speaking styles, making it suitable for training robust ASR models.
- ID prefixes indicate source: `YOU` (YouTube), `POD` (Podcast), `AUD` (Audiobook).
