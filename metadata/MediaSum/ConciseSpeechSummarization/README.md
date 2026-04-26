# MediaSum — Concise Speech Summarization

## Overview
**MediaSum (Concise Speech Summarization)** is the large-scale subset of the MediaSum NPR interview corpus paired with **automatically extracted abstractive summaries** drawn from NPR show metadata. These summaries are sourced from the original **MediaSum** dataset (Zhu et al., NAACL 2021), which constructed them from overview and topic descriptions written by NPR editorial staff — not from human annotators listening to or reading the interviews. Each of the 9,787 entries pairs a unique interview audio file with one concise summary. Audio is stored as **MP3** at variable sampling rates (predominantly 44.1 kHz).

## Supported Tasks
1. **Concise Speech Summarization** — Generate a short abstractive summary of a spoken NPR interview

---

## Dataset Statistics

| Split | # Entries | Total Duration | Avg Duration |
|-------|----------:|---------------:|-------------:|
| train | 9,587 | ~527.9h | ~198.2s |
| test | 200 | ~9.7h | ~173.9s |
| **Total** | **9,787** | **~537.5h** | **~197.7s** |

Audio duration ranges from ~21.6 to ~299.9 seconds.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio file ID (e.g., `NPR-3`) |
| `path` | Path to interview audio file (MP3) |
| `sampling_rate` | Audio sampling rate (Hz); most files are 44100 Hz |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`MediaSum`) |
| `summary` | Concise abstractive summary extracted from NPR show metadata |

---

## Example Entries

```json
{"id": "NPR-3", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MediaSum/audio/NPR-3.mp3", "sampling_rate": 44100, "duration": 268.5025, "dataset": "MediaSum", "summary": "In this week's snapshot, actor and playwright Jeff Obafemi Carr stumbles across some old and new pitfalls in the Nashville neighborhood where he grew up."}

{"id": "NPR-23624", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MediaSum/audio/NPR-23624.mp3", "sampling_rate": 44100, "duration": 124.802875, "dataset": "MediaSum", "summary": "The new movie The Giver stars Meryl Streep and Jeff Bridges. It's an adaptation of the young adult novel by Lois Lowry about a world where emotion and feeling have been done away with."}
```

---

## Task Usage

### 1. Concise Speech Summarization
- **Input:** Audio (spoken NPR interview)
- **Target field:** `summary` (concise abstractive summary extracted from show metadata)

---

## Label Space

*This task generates open-vocabulary text — there is no predefined label space.*

Summaries are short and concise, typically 1–2 sentences, written by NPR editorial staff as show overviews or topic descriptions rather than post-hoc summaries of the interview content. They are generally less detailed than the expert-annotated summaries in `../DetailedSpeechSummarization/`.

---

## Manifest Organization

| File | # Entries | Description |
|------|----------:|-------------|
| `train.jsonl.gz` | 9,587 | Training split |
| `test.jsonl.gz` | 200 | Test split |
| `manifest.jsonl.gz` | 9,787 | Combined manifest (all entries) |

---

## Notes
- Audio files are stored as **MP3** (not WAV). Sampling rates vary: most files are 44,100 Hz, with a small number at 48,000 Hz or 22,050 Hz.
- All audio is from **NPR** interview recordings.
- Each audio file has exactly **one summary** (one-to-one mapping), unlike `../DetailedSpeechSummarization/` which has 4–6 summaries per file.
- Summaries are **automatically extracted** from the `news_dialogue.json` metadata in the original MediaSum release — they are NPR editorial descriptions, not written by annotators listening to the audio.
- This subset is **disjoint** from the detailed summary set: none of the 9,787 files here appear in `../DetailedSpeechSummarization/`.
- The original MediaSum dataset is described in: Zhu et al., "MediaSum: A Large-Scale Media Interview Dataset for Dialogue Summarization" (NAACL 2021).
- The parent manifest at `../train.jsonl.gz` merges this concise subset with the detailed summary entries into a single combined training manifest.
