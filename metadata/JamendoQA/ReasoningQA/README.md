# JamendoQA Reasoning QA

## Overview
**JamendoQA Reasoning QA** is a large-scale benchmark for music question answering, built on freely licensed music from the Jamendo platform. This dataset contains **58,680 question-answer pairs** derived from **7,335 unique music tracks**, with an average of **8 questions per track**. Questions target specific musical attributes such as genre, tempo, key signature, instrumentation, lyrical themes, song structure, and harmonic analysis. The dataset supports research in music understanding, multimodal audio-text learning, music information retrieval, and zero-shot evaluation of music-QA systems.

## Supported Tasks
1. **Music Question Answering**

---

## Dataset Statistics

| Split | # Samples | # Unique Tracks | Avg Q/Track |
|-------|----------:|----------------:|------------:|
| train | 58,680 | 7,335 | 8.0 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique identifier (format: `{track_id}_Q{question_number}`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `question` | Natural language question about the music |
| `answer` | Ground-truth answer extracted from detailed caption |

---

## Example Entries

```json
{"id": "accordion_AGeordieFarewell_Q0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_AGeordieFarewell.wav", "sampling_rate": 16000, "duration": 205.69, "dataset": "JamendoQA", "question": "What is the primary genre of this track?", "answer": "The track is a Folk‑Rock/Acoustic‑Rock piece."}

{"id": "accordion_AGeordieFarewell_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_AGeordieFarewell.wav", "sampling_rate": 16000, "duration": 205.69, "dataset": "JamendoQA", "question": "What are the tempo and time signature of this song?", "answer": "It moves at 100 BPM in a 4/4 meter."}

{"id": "accordion_AGeordieFarewell_Q2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_AGeordieFarewell.wav", "sampling_rate": 16000, "duration": 205.69, "dataset": "JamendoQA", "question": "In which key is the song rooted, and which relative major does it often lift into?", "answer": "The song is rooted in B minor and often lifts into its relative major, D major."}
```

---

## Task Usage

### 1. Music Question Answering
- **Input:** Audio file + question about musical characteristics
- **Target field:** `answer` (ground-truth answer)

---

## Label Space

*This is an open-vocabulary generation task without a predefined label space.*

### Question Categories

Questions cover diverse musical attributes including:

1. **Genre Identification**: "What is the primary genre of this track?"
2. **Tempo & Meter**: "What are the tempo and time signature of this song?"
3. **Key Signature**: "In which key is the song rooted?"
4. **Instrumentation**: "What instruments are featured in the arrangement?"
5. **Production Details**: "How is the stereo field organized?"
6. **Vocal Characteristics**: "What is the timbre and delivery style of the vocals?"
7. **Lyrical Themes**: "What themes are explored in the lyrics?"
8. **Song Structure**: "What is the structure of this composition?"
9. **Harmonic Analysis**: "What chord progressions are used?"
10. **Duration**: "How long is this track?"

---

## Notes
- All audio files are sampled at **16 kHz** in **WAV format**.
- Audio clips have **variable duration** ranging from **29 to 2,035 seconds** (average: ~233 seconds / ~3.9 minutes).
- Each track has **8 question-answer pairs on average**, targeting different musical attributes.
- Questions and answers are derived from detailed, human-authored captions with expert-level musical analysis.
- The dataset contains **full-length music tracks** from the Jamendo platform (freely licensed Creative Commons).
- **No dev/test splits** are provided; users should create their own evaluation splits.
- The `id` format `{track_id}_Q{number}` links multiple questions to the same audio track.
- Answers are **extractive or abstractive** summaries from the source captions, providing concise, factual responses.
- This dataset is designed as a scalable resource for both **supervised training** and **zero-shot evaluation** of music-QA systems.
- Audio is sourced from the **Jamendo music platform**, ensuring all content is freely licensed for research use.

---

## Related Tasks

For other tasks using the JamendoQA dataset, see:
- [Music Captioning](../MusicCaptioning/README.md): Generate detailed text descriptions from music audio
