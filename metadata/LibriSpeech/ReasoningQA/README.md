# LibriSpeech

## Overview
**LibriSpeech ReasoningQA** is a large-scale dataset for long-form audio reasoning and comprehension, built from concatenated LibriVox audiobook segments paired with LLM-generated reasoning questions. The dataset has been **significantly enhanced** with permutations and varied question types, expanding from 7,976 to **39,916 question-answer pairs** across **585 concatenated audio segments** (average duration: 82.41s). This enhanced dataset prevents pattern exploitation and provides robust evaluation of reasoning, temporal understanding, and causal comprehension over extended audio context.

## Supported Tasks
1. **Long-form Spoken Question Answering**
2. **Audio Topic Sequencing**
3. **Positional Topic Identification**

---

## Dataset Statistics

| Split | # Samples | Description |
|-------|-----------|-------------|
| train | 37,952 | Enhanced main dataset (train.jsonl.gz) |
| train-topic | 1,964 | Positional topic questions (train.topic.jsonl.gz) |
| **Total** | **39,916** | **Combined enhanced dataset** |

**Dataset Expansion:** 5.00x from original 7,976 questions

**Additional Files:**
- `train.bak.jsonl.gz` (7,976 samples): Original dataset backup

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair identifier |
| `path` | Path to concatenated audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `question` | Question text |
| `answer` | Answer text |

**ID Format:**
- Standard questions: `{speaker}_{book}_Q{index}`
- Permuted questions: `{speaker}_{book}_Q{index}_P{permutation}` (1 to N)
- Positional questions: `{speaker}_{book}_Q{index}_T{topic_num}` (1 to 4)

---

## Example Entries

```json
{"id": "6147_34606_Q2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/LibriSpeech-concat/6147/34606/combined.wav", "sampling_rate": 16000, "duration": 145.03, "dataset": "LibriSpeech", "question": "What societal norms or expectations were being challenged according to the speech, and how did the actions of certain individuals contribute to this challenge?", "answer": "The societal norms being challenged were related to personal appearance, specifically the wearing of wigs. The actions of individuals like Eugene Deveria and Lord David, who appeared without wigs and with their natural hair, shook the foundations of society by defying these norms. Their audacity and courage in doing so contributed to a shift in societal expectations regarding personal grooming."}

{"id": "3440_171009_Q8_P7", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/LibriSpeech-concat/3440/171009/combined.wav", "sampling_rate": 16000, "duration": 63.41, "dataset": "LibriSpeech", "question": "Arrange the following topics according to their sequence of appearance in the speech.: (A) Elsie returns from a walk looking refreshed., (B) The young group grows and a new table is arranged in the nursery., (C) Other children are described as tired and irritable., (D) Children express regret about Elsie leaving early and look forward to the Christmas tree event.", "answer": "(B)(A)(C)(D)"}

{"id": "3440_171009_Q8_T1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/LibriSpeech-concat/3440/171009/combined.wav", "sampling_rate": 16000, "duration": 63.41, "dataset": "LibriSpeech", "question": "Which topic is discussed last in the speech?\nChoose the correct option from the following options: (A) Other children are described as tired and irritable, (B) Elsie returns from a walk looking refreshed, (C) The young group grows and a new table is arranged in the nursery, (D) Children express regret about Elsie leaving early and look forward to the Christmas tree event", "answer": "(D) Children express regret about Elsie leaving early and look forward to the Christmas tree event"}
```

---

## Task Usage

### 1. Long-form Spoken Question Answering
- **Target field:** `answer`

### 2. Audio Topic Sequencing
- **Target field:** `answer` (ordered topic sequence)

### 3. Positional Topic Identification
- **Target field:** `answer` (specific topic at position)

---

## Label Space

*This task does not have a predefined label space - it generates open-ended text answers based on reasoning over long-form audio content.*

---

## Question Types

The dataset includes three main categories:

### Standard Reasoning Questions
Questions designed to test higher-level comprehension and reasoning:

- **What** (32.8%): Factual comprehension
- **How** (19.2%): Process and method reasoning
- **Why** (8.1%): Causality and motivation
- **Summarize** (8.2%): Content summarization
- **Temporal** (7.4%): Time-based relationships
- **Other** (24.3%): Comparison, inference, etc.

### Arrangement Questions (train.jsonl.gz)
Questions asking to arrange topics/events in chronological order:

<details>
<summary>Show arrangement question details</summary>

**Format:** "Arrange the following topics in the order they are discussed: (A) topic1, (B) topic2, (C) topic3, (D) topic4"

**Enhancements:**
- N permutations created per question (N = number of topics)
- Topics shuffled to prevent trivial pattern exploitation
- 1,058 unique ordering patterns across dataset
- 97.8% non-trivial answers (vs. 30% in original)

</details>

### Positional Topic Questions (train.topic.jsonl.gz)
Questions asking about specific topic positions with varied phrasings:

<details>
<summary>Show 5 question phrasing variants</summary>

- "What is the [first/second/third/...] topic discussed in the speech?"
- "Which topic is discussed [ordinal] in the speech?"
- "What topic appears [at position] in the speech?"
- "Which topic [opens/concludes] the speech?"
- "Identify the [ordinal] topic mentioned in the speech."

</details>

**Coverage:**
- 4 questions per original arrangement question
- Position distribution: First (26.7%), Second (23.5%), Third (21.8%), Last (25.1%)
- Multiple-choice format with 4 shuffled options

---

## Dataset Enhancements

This dataset has been enhanced from the original version with three major improvements:

### 1. Improved Question Wording
- Topics embedded directly in question stem
- Removed redundant preambles for cleaner format
- More natural, varied phrasings

### 2. Shuffled Permutations for Robust Evaluation
- **Arrangement questions:** N permutations (N = number of topics)
- **Multiple-choice questions:** N permutations (each option as correct answer once)
- **Benefit:** Eliminates trivial pattern exploitation
- **Impact:** 97.8% non-trivial arrangement answers (vs. 30% originally)

### 3. Positional Topic Questions
- New file (train.topic.jsonl.gz) with 1,964 questions
- 4 varied questions per arrangement question
- 5 different phrasings to prevent pattern matching
- Tests fine-grained positional understanding

---

## Audio Construction

### Concatenation Process
Each audio segment is created by concatenating multiple LibriSpeech utterances:

1. **Source:** Original LibriSpeech utterances from same speaker and book
2. **Concatenation:** Multiple utterances combined into single `combined.wav` file
3. **Utterances per segment:** 1-19 utterances (average: 6.52)
4. **Output location:** `/saltpool0/data/tseng/FullSpectrumDataset/corpus/LibriSpeech-concat/{speaker}/{book}/combined.wav`

### QA Generation
- Question-answer pairs generated by LLM based on audio content
- Multiple QA pairs per audio segment (average: 13.6 original pairs)
- Answers focus on reasoning, comprehension, and causal relationships

---

## Notes
- All audio files are sampled at **16 kHz**.
- **Audio duration range:** 16.02s to 147.59s (average: 82.41s).
- **Total audio content:** Approximately 182.58 hours.
- **Unique audio segments:** 585 concatenated files.
- **Original QA pairs:** 7,976 reasoning questions.
- **Enhanced dataset:** 39,916 total questions (5.00x expansion).
- **Average QA pairs per audio:** 13.6 original questions per segment (68+ with permutations).
- Same audio file referenced by multiple QA pairs with different questions and permutations.
- Questions test **multi-hop reasoning**, **temporal understanding**, and **causal comprehension** rather than simple transcription.
- Answers range from 6 to 682 characters (average: 185.6 characters).
- Audio segments maintain speaker and book coherence from original LibriSpeech corpus.
- This dataset is based on the methodology described in the **nvidia/longaudio-xl** (AudioFlamingo3) paper.
- **Enhancement date:** April 2026
- **Original backup:** Available as train.bak.jsonl.gz
