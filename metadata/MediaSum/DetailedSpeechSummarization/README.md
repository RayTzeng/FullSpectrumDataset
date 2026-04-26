# MediaSum — Detailed Speech Summarization

## Overview
**MediaSum (Detailed Speech Summarization)** is a curated subset of the MediaSum NPR interview corpus paired with **human-written abstractive summaries** collected by third-party expert annotators. The summaries were gathered as part of the study **"Speech vs. Transcript: Does It Matter for Human Annotators in Speech Summarization?"**, which examined whether annotators produce different summaries when working from audio versus text transcripts. Each of the 1,002 interview recordings is annotated with up to 6 summaries across three annotation modalities: audio-based (`AudioSum`), transcript-based (`TextSum`), and Whisper-ASR-based (`WhisperSum`). Audio is stored as **MP3** at variable sampling rates (predominantly 44.1 kHz).

## Supported Tasks
1. **Detailed Speech Summarization** — Generate a detailed abstractive summary of a spoken NPR interview

---

## Dataset Statistics

| Split | # Entries | # Unique Audio Files | Total Duration | Avg Duration |
|-------|----------:|---------------------:|---------------:|-------------:|
| train | 3,716 | 886 | ~240.0h | ~232.6s |
| test | 68 | 17 | ~4.6h | ~243.8s |
| **Total** | **3,784** | **903** | **~244.6h** | **~232.8s** |

### Summary Type Breakdown (train split)

| Summary Type | # Entries | Description |
|-------------|----------:|-------------|
| `AudioSum` | 1,772 | Summary written by annotators who listened to the audio |
| `TextSum` | 1,772 | Summary written by annotators who read the transcript |
| `WhisperSum` | 172 | Summary written from Whisper ASR-generated transcription |

### Summary Type Breakdown (test split)

| Summary Type | # Entries | Description |
|-------------|----------:|-------------|
| `AudioSum` | 34 | Summary written by annotators who listened to the audio |
| `TextSum` | 34 | Summary written by annotators who read the transcript |

Audio duration ranges from ~16.1 to ~587.0 seconds, with an average of ~232.8 seconds (~3.9 minutes) per entry.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique entry ID encoding audio file and summary type (e.g., `NPR-12_AudioSum1`, `NPR-12_TextSum2`) |
| `path` | Path to interview audio file (MP3) |
| `sampling_rate` | Audio sampling rate (Hz); most files are 44100 Hz |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`MediaSum`) |
| `summary` | Detailed abstractive summary of the interview content |

---

## Example Entries

```json
{"id": "NPR-12_AudioSum1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MediaSum/audio/NPR-12.mp3", "sampling_rate": 44100, "duration": 231.696, "dataset": "MediaSum", "summary": "A new survey out from the employment firm, Manpower, finds that about a quarter of employers will add jobs this summer for adults. For teenagers, this summer's job market is shaping up to be the weakest in more than 50 years. Tough economy, a lot of college graduates going into the market taking the jobs that would normally go to teens, and a lot of older people holding onto their jobs not retiring because they can't afford to. That puts teens at the end of the line for these jobs. Just keep looking if you are a teen in search of a job."}

{"id": "NPR-12_TextSum1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MediaSum/audio/NPR-12.mp3", "sampling_rate": 44100, "duration": 231.696, "dataset": "MediaSum", "summary": "While a new survey from the employment firm Manpower says about a quarter of employers will add jobs this summer for both adult men and women, the summer's job outlook for teenagers may be the weakest in more than 50 years. Michelle Singletary, personal finance contributor for Day to Day, says that we're in a tough economy, which means jobs that usually go to teens, like jobs in retail and restaurants, are going to college students and grad, people who lost their jobs, and older people still working because they can't afford to retire."}

{"id": "NPR-142_WhisperSum1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MediaSum/audio/NPR-142.mp3", "sampling_rate": 44100, "duration": 314.399625, "dataset": "MediaSum", "summary": "Alan Judd, an investigative reporter with the Atlanta Journal Constitution, discussed the legal requirements for churches and religious organizations concerning their nonprofit status and reporting. Churches are not required to file Form 990 with the IRS, which is something that typical foundations or nonprofits would have to file."}
```

---

## Task Usage

### 1. Detailed Speech Summarization
- **Input:** Audio (spoken NPR interview)
- **Target field:** `summary` (detailed abstractive summary of the interview)

---

## Label Space

*This task generates open-vocabulary text — there is no predefined label space.*

Summaries are multi-sentence and abstractive, typically 2–6 sentences in length. The three annotation modalities produce distinct summary characteristics:
- **AudioSum**: Written by annotators listening to the audio; may reflect prosodic cues and spoken emphasis.
- **TextSum**: Written by annotators reading the transcript; tends to be more lexically faithful to the transcript.
- **WhisperSum**: Written from Whisper ASR output; quality may vary with ASR transcription accuracy.

Each modality produces **2 independent summaries** per audio file (suffixes `1` and `2`), enabling within-modality comparison.

---

## ID Naming Convention

| ID Pattern | Meaning |
|-----------|---------|
| `NPR-{N}_AudioSum{1\|2}` | Audio-based summary (annotator listened to the recording) |
| `NPR-{N}_TextSum{1\|2}` | Transcript-based summary (annotator read the text) |
| `NPR-{N}_WhisperSum{1\|2}` | Whisper-ASR-based summary (annotator read Whisper output) |

`WhisperSum` entries are only available for a subset of 96 audio files.

---

## Manifest Organization

| File | # Entries | Description |
|------|----------:|-------------|
| `train.jsonl.gz` | 3,716 | Training split |
| `test.jsonl.gz` | 68 | Test split |

---

## Notes
- Audio files are stored as **MP3** (not WAV). Sampling rates vary: most files are 44,100 Hz, with a small number at 48,000 Hz or 22,050 Hz.
- All audio is from **NPR** interview recordings.
- This subset is **disjoint** from the concise summary set: none of the 1,002 files here appear in `../ConciseSpeechSummarization/`.
- Summaries were collected by **third-party expert annotators** under the study "Speech vs. Transcript: Does It Matter for Human Annotators in Speech Summarization?", which investigates whether the annotation modality (audio vs. transcript) influences the content and quality of human-written summaries.
- The broader MediaSum dataset is described in: Zhu et al., "MediaSum: A Large-Scale Media Interview Dataset for Dialogue Summarization" (NAACL 2021).
- The parent manifest at `../train.jsonl.gz` merges this detailed subset with the concise summary entries into a single combined training manifest.
