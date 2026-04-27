# VoxCeleb2 (Reasoning QA)

## Overview
**VoxCeleb2** is a large-scale audio-visual speaker recognition corpus collected automatically from online celebrity interviews and talk-show videos, containing over 1 million utterances from more than 6,000 speakers recorded in realistic, noisy, in-the-wild conditions. In the **AudioFlamingo3** long-speech training pipeline, concatenated utterances from the same speaker and video are paired with reasoning question–answer pairs generated over the spoken content, covering tasks such as comprehension, summarization, causal reasoning, and topic inference. Each audio file is a `combined.wav` constructed by concatenating multiple VoxCeleb2 utterances from the same speaker–video combination into a single longer segment. Audio is stored as **WAV** at **16 kHz**.

## Supported Tasks
1. **Spoken Dialogue Reasoning QA** — Given a long-form spoken interview segment, answer an open-ended question requiring comprehension, inference, summarization, or causal reasoning over the spoken content

---

## Dataset Statistics

| Split | # QA Pairs | # Unique Audio Files | # Unique Speakers | Total Duration | Avg Duration |
|-------|----------:|---------------------:|------------------:|---------------:|-------------:|
| train | 41,702 | 6,473 | 341 | ~845.3h | ~73.0s |

Audio duration ranges from ~7.9 to ~1,273.6 seconds (~21 minutes). Each audio file has 1–10 QA pairs, with an average of ~6.4 QA pairs per file (most common: 4 or 10).

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID encoding speaker, video, and question index (e.g., `id07175_KvWODMr9Q1g_Q5`) |
| `path` | Path to concatenated audio file (WAV) |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`VoxCeleb2`) |
| `question` | Open-ended question about the spoken content |
| `answer` | Free-form text answer |

The ID format is `{speaker_id}_{video_id}_Q{index}`, where multiple QA pairs sharing the same `{speaker_id}_{video_id}` prefix refer to the same audio file.

---

## Example Entries

```json
{"id": "id07175_KvWODMr9Q1g_Q5", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/voxceleb2-concat/id07175/KvWODMr9Q1g/combined.wav", "sampling_rate": 16000, "duration": 52.16, "dataset": "VoxCeleb2", "question": "What is the speaker's stance on the political implications of the issue discussed, particularly concerning inter-state relations?", "answer": "The speaker appears to be concerned about the political implications, especially regarding negative remarks from individuals from Bihar about the state of Maharashtra. The speaker seems to feel protective of Maharashtra and may have a political affiliation or respect for a political figure named Balasaheb."}

{"id": "id08627_Louov9bC6yM_Q8", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/voxceleb2-concat/id08627/Louov9bC6yM/combined.wav", "sampling_rate": 16000, "duration": 78.4, "dataset": "VoxCeleb2", "question": "Summarize the main concerns expressed by the speaker regarding their business in the given conversation.", "answer": "The speaker is concerned about affording expenses like tickets, gas, and hotels for their small business amid economic strain."}

{"id": "id08627_4QSn8Gx_lEw_Q7", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/voxceleb2-concat/id08627/4QSn8Gx_lEw/combined.wav", "sampling_rate": 16000, "duration": 156.61, "dataset": "VoxCeleb2", "question": "Why does the speaker reflect on the experience with the bus and the airlines as part of their touring story?", "answer": "The speaker reflects on the experience with the bus and the airlines to illustrate the challenges and discomforts of touring, which contrast with the romanticized view of life on the road."}
```

---

## Task Usage

### 1. Spoken Dialogue Reasoning QA
- **Input:** Audio (long-form spoken interview segment) + `question` (text)
- **Target field:** `answer` (free-form text response)

---

## Label Space

*This task generates open-vocabulary text — there is no predefined label space.*

Answers are free-form and vary in length and complexity depending on the question type. Question topics include:
- **Comprehension / Content QA** — Questions about what is discussed, who is mentioned, or what stance the speaker takes
- **Summarization** — "Summarize the main concerns / points expressed by the speaker..."
- **Causal Reasoning** — "Why does the speaker...?", "What led to...?"
- **Inference** — "What can be inferred about the speaker's view on...?", "What does the speaker imply by...?"
- **Speaker Identification** — "Who is mentioned as...?", "Who was selected for...?"

Questions are formulated with open-ended wording (no multiple-choice options) and require understanding of extended spoken content.

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Each audio file is a concatenation of multiple VoxCeleb2 utterances from the same speaker and video, forming a longer continuous segment (`combined.wav`). Audio durations range widely, from under 10 seconds to over 21 minutes.
- Speaker IDs follow the VoxCeleb2 convention (e.g., `id07175`). There are 341 unique speakers in this split.
- All speech is **natural, in-the-wild** spontaneous speech from celebrity interviews, covering diverse topics, accents, speaking styles, and recording conditions.
- The QA pairs were generated as part of the **AudioFlamingo3** long-speech training pipeline. See the AudioFlamingo3 paper for details on the QA generation process.
- The original VoxCeleb2 dataset is described in: Chung et al., "VoxCeleb2: Deep Speaker Recognition" (Interspeech 2018).
