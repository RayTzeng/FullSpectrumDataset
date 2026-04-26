# Speech-in-Sound (Reasoning QA)

## Overview
**Speech-in-Sound** is a speech-aware audio understanding resource built from **YouTube8M** clips where spoken content co-occurs with ambient sounds or music, modeling realistic acoustic scenes rather than clean speech alone. It was introduced as part of the **AudioFlamingo3** collection. A derived QA collection of approximately **3.06 million question–answer pairs** is provided for reasoning over both the spoken content and the surrounding acoustic scene. Each ~10-second clip is paired with either a multiple-choice question about the acoustic context or a free-form audio captioning prompt. Audio is stored as **MP3** at variable sampling rates (predominantly 44.1 kHz and 48 kHz).

## Supported Tasks
1. **Speech-in-Sound Reasoning QA** — Given a short audio clip containing speech mixed with ambient sounds or music, answer a multiple-choice question about the acoustic context or spoken content
2. **Audio Scene Captioning** — Generate a descriptive caption of the auditory scene, integrating spoken content, background sounds, and music

---

## Dataset Statistics

| Split | # Entries | Total Duration | Avg Duration |
|-------|----------:|---------------:|-------------:|
| train | 3,063,948 | ~8,538.1h | ~10.0s |
| test | 100 | ~0.3h | ~10.0s |

Audio duration ranges from ~2.7 to ~10.9 seconds. The vast majority of clips are exactly ~10 seconds.

### Train Shards

The training set is distributed across 11 shards:

| Shard | # Entries |
|-------|----------:|
| `train_shard1.jsonl.gz` | 138,660 |
| `train_shard2.jsonl.gz` | 51,043 |
| `train_shard3.jsonl.gz` | 146,054 |
| `train_shard4.jsonl.gz` | 388,811 |
| `train_shard5.jsonl.gz` | 165,613 |
| `train_shard6.jsonl.gz` | 518,564 |
| `train_shard7.jsonl.gz` | 161,902 |
| `train_shard8.jsonl.gz` | 234,998 |
| `train_shard9.jsonl.gz` | 380,739 |
| `train_shard10.jsonl.gz` | 418,424 |
| `train_shard11.jsonl.gz` | 459,140 |
| **Total** | **3,063,948** |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID derived from YouTube8M video ID and time offset (e.g., `--A5-Li6guA_36_10`) |
| `path` | Path to audio clip (MP3) |
| `sampling_rate` | Audio sampling rate (Hz); typically 44100 or 48000 |
| `duration` | Audio duration in seconds |
| `question` | Multiple-choice question with inline answer choices, or a free-form captioning prompt |
| `answer` | Correct answer letter with label (MC), or free-form caption text |

The `question` field may optionally contain a `<sound>` token indicating the position at which the audio is inserted relative to the question text.

---

## Example Entries

### Multiple-Choice QA
```json
{"id": "--A5-Li6guA_36_10", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/YouTube8M/batch1/Xbox_360/--A5-Li6guA_36_10.mp3", "sampling_rate": 44100, "duration": 10.03102, "question": "In what kind of setting is the speech most likely being delivered? Choose one among the following options:\n(A) A sports stadium\n(B) A lecture hall\n(C) A courtroom\n(D) A busy street", "answer": "(B) lecture hall"}

{"id": "-aAAeyZvmPQ_78_10", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/YouTube8M/batch6/Pac-Man/-aAAeyZvmPQ_78_10.mp3", "sampling_rate": 48000, "duration": 10.032, "question": "Based on the given audio, what likely enhances the emotional impact of the speech? Choose one among the following options:\n(A) Background traffic noise\n(B) Synth melody\n(C) Silence\n(D) Bird chirping\n<sound>", "answer": "(B) Synth melody"}
```

### Audio Scene Captioning
```json
{"id": "--C_O5tEeBE_36_10", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/YouTube8M/batch1/Weight_training/--C_O5tEeBE_36_10.mp3", "sampling_rate": 48000, "duration": 10.032, "question": "Generate a caption describing the auditory scene in the input audio, considering spoken content, background sounds, and music.", "answer": "Two male voices engage in a neutral-toned, moderate-paced conversation about working at Phoenix Beach after returning from Mississippi, while a softly singing man adds a gentle ambient layer to the background."}
```

---

## Task Usage

### 1. Speech-in-Sound Reasoning QA
- **Input:** Audio (speech mixed with ambient sounds or music) + `question` (text, with 4 inline choices)
- **Target field:** `answer` (correct choice letter and label, e.g., `(B) lecture hall`)

### 2. Audio Scene Captioning
- **Input:** Audio (speech mixed with ambient sounds or music) + `question` (captioning prompt)
- **Target field:** `answer` (free-form descriptive caption)

---

## Label Space

### Multiple-Choice QA
Questions have **4 answer choices** labeled `(A)`–`(D)` inline within the `question` field. The `answer` field contains the correct choice letter followed by the label text (e.g., `(B) lecture hall`). Answer choices are approximately balanced across A–D.

### Audio Scene Captioning
*This task generates open-vocabulary text — there is no predefined label space.*

Captions are free-form descriptions integrating spoken content, speaker characteristics, background sounds, and music. They average ~28 words in length.

---

## Manifest Organization

| File | # Entries | Description |
|------|----------:|-------------|
| `train.jsonl.gz` | 3,063,948 | Full training set (all shards merged) |
| `train_shard{1–11}.jsonl.gz` | varies | Individual training shards |
| `test_manifest.jsonl.gz` | 100 | Test set |

---

## Notes
- Audio files are stored as **MP3**. Sampling rates are predominantly 48,000 Hz or 44,100 Hz.
- All clips are sourced from **YouTube8M** and are approximately **10 seconds** in duration. Clip IDs encode the source video ID and time offset (e.g., `--A5-Li6guA_36_10` = video `--A5-Li6guA`, starting at 36s, duration 10s).
- The `<sound>` token in some questions marks where the audio embedding is inserted relative to the question text. Its presence and position (before or after the question) vary across entries.
- Questions span a variety of acoustic reasoning topics, including: speech delivery setting, speaker characteristics, background sound identification, music genre classification, and the emotional context of the acoustic scene.
- The dataset was introduced as part of the **AudioFlamingo3** collection. See the AudioFlamingo3 paper for full details on the data generation pipeline.
- The original audio clips are drawn from **YouTube8M**, a large-scale labeled video dataset covering thousands of categories.
