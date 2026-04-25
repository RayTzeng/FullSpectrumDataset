# Stress-17K (Stressed Speech Understanding)

## Overview
**Stress-17K** (released as **Stress-17K-raw**) is a synthetic speech dataset designed for research on **sentence stress understanding**, specifically how prosodic emphasis shifts the meaning of an utterance. This manifest (`understanding`) reformats the base dataset as **instruction-following QA pairs** in four distinct prompt styles, covering both stress detection and stress meaning tasks. Each audio clip is paired with a natural-language question and a corresponding answer, making these manifests suitable for training and evaluating instruction-tuned speech language models. The dataset was introduced alongside the **StressTest: Can YOUR Speech LM Handle the Stress?** work. Audio is synthesized at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Stressed Speech Understanding** — Answer natural-language questions about which words are stressed and what that stress communicates

---

## Dataset Statistics

### Combined Manifests (`train.jsonl.gz`, `test.jsonl.gz`)

| Split | # QA Pairs | # Unique Audio Files |
|-------|----------:|---------------------:|
| train | 16,600 | 4,150 |
| test | 1,000 | 250 |

Each unique audio file contributes **4 QA pairs** (one per prompt style).

### Task-Specific Manifests

| File | # QA Pairs | Task |
|------|----------:|------|
| `stress_detection.jsonl.gz` | 4,400 | Identify which words are stressed |
| `e2e_stress_meaning.jsonl.gz` | 4,400 | Multiple-choice stress meaning (direct) |
| `cascade_reasoning.jsonl.gz` | 4,400 | Multiple-choice stress meaning (chain-of-thought) |
| `elaborated_explanation.jsonl.gz` | 4,400 | Open-ended explanation of stress meaning |

The task-specific files cover the full training set (4,400 = 4,150 train + 250 used as test source audio).

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID (audio ID + prompt-style suffix `_1`–`_4`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`Stress17K`) |
| `question` | Natural-language prompt presented to the model |
| `answer` | Expected model response |

---

## Example Entries

```json
{"id": "stress17k_train_00000_4", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00000.wav", "duration": "2.513", "sampling_rate": 16000, "dataset": "Stress17K", "question": "The speaker said \"leonardo painted a remarkable fresco.\". \nAccording to the audio, what words did the speaker stress?\nAnswer format: [stressed_word_1, ...]\nAnswer:", "answer": "leonardo"}

{"id": "stress17k_train_00000_1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00000.wav", "duration": "2.513", "sampling_rate": 16000, "dataset": "Stress17K", "question": "Out of the following answers, according to the speaker's stressed words, what is most likely the underlying intention of the speaker?\n1. Highlighting that it was Leonardo, not other artists, who painted it. \n2. Emphasizing that the fresco was remarkable, not ordinary. \nAnswer:", "answer": "1. Highlighting that it was Leonardo, not other artists, who painted it."}

{"id": "stress17k_train_00000_3", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00000.wav", "duration": "2.513", "sampling_rate": 16000, "dataset": "Stress17K", "question": "The speaker stressed some words. What is the speaker trying to communicate? \n1. Highlighting that it was Leonardo, not other artists, who painted it. \n2. Emphasizing that the fresco was remarkable, not ordinary. \nThink about the transcription and the stressed words. Then, answer like this: \"answer_number. correct_answer\"", "answer": "The speaker said \"leonardo painted a remarkable fresco.\" and emphasized \"leonardo\".\nTherefore, the correct answer is: 1. Highlighting that it was Leonardo, not other artists, who painted it."}

{"id": "stress17k_train_00000_2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Stress17K/train/00000.wav", "duration": "2.513", "sampling_rate": 16000, "dataset": "Stress17K", "question": "According to the speaker's stressed words, what is the speaker's underlying intention? \n1. Highlighting that it was Leonardo, not other artists, who painted it. \n2. Emphasizing that the fresco was remarkable, not ordinary. \nElaborate, then answer in the following way: \"answer_number. correct_answer\"", "answer": "Highlighting that it was Leonardo, as opposed to other artists, who painted the fresco. Therefore, the correct answer is: 1. Highlighting that it was Leonardo, not other artists, who painted it."}
```

---

## Task Usage

### 1. Stressed Speech Understanding
- **Input:** Audio (synthesized English speech with prosodic stress) + `question` (natural-language prompt)
- **Target field:** `answer` (expected model response, format varies by prompt style)

---

## Prompt Styles

Each audio file is paired with four distinct prompt styles, identified by the suffix in the `id` field:

| ID Suffix | Style | Task | Answer Format |
|-----------|-------|------|---------------|
| `_4` | **Stress Detection** | Identify stressed word(s) from the transcription | `[word_1, ...]` (list) |
| `_1` | **E2E Stress Meaning** | Multiple-choice: pick the correct pragmatic interpretation (direct) | `N. answer text` |
| `_3` | **Cascade Reasoning** | Multiple-choice: identify stressed words first, then choose interpretation | Full reasoning chain + `N. answer text` |
| `_2` | **Elaborated Explanation** | Multiple-choice: provide a free-form explanation, then choose interpretation | Explanation + `N. answer text` |

The `train.jsonl.gz` and `test.jsonl.gz` combined manifests interleave all four styles.

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, ranging from ~1.1 to ~6.5 seconds, with an average of ~2.97 seconds.
- The `understanding` manifests reuse the same audio files as `../raw/`; there are no additional recordings.
- Each unique audio file contributes exactly **4 QA pairs** (one per prompt style), so `# QA pairs = 4 × # unique audio files`.
- The four task-specific files (`stress_detection`, `e2e_stress_meaning`, `cascade_reasoning`, `elaborated_explanation`) each contain all 4,400 samples from the combined train+test audio pool; the combined `train.jsonl.gz` covers only the 4,150 training audio files (16,600 pairs) and `test.jsonl.gz` covers the held-out 250 test audio files (1,000 pairs).
- All speech is **synthesized** (text-to-speech), not recorded from human speakers. Prosodic emphasis is rendered acoustically by the TTS system.
- The dataset is structured around **contrastive stress pairs**: each base sentence appears in multiple versions emphasizing different words, each conveying a distinct pragmatic meaning.
- The `cascade_reasoning` style prompts the model to first identify stressed words before selecting an interpretation — this represents a two-step reasoning approach useful for evaluating chain-of-thought capabilities in speech LMs.
- Audio was extracted from the **slprl/Stress-17K-raw** HuggingFace dataset and resampled to 16 kHz.
- The companion manifest at `../raw/` provides the same data in structured classification format (with `text`, `description`, `possible_answers`, and `label` fields) suitable for discriminative modeling.
