# SpokenMQA - Spoken Mathematical Question Answering

## Overview
**SpokenMQA** is a benchmark dataset for **spoken mathematical reasoning**, designed to evaluate whether speech-based models can solve math problems directly from spoken input. The dataset covers **pure arithmetic**, **single-step contextual reasoning**, and **multi-step reasoning problems**, enabling evaluation of both cascade systems (ASR + LLMs) and end-to-end speech LLMs.

The original dataset contains **2,269 question-answer pairs** with unique audio recordings. We have enhanced this to **9,076 total entries (4.0x expansion)** by creating different task variants. Audio is sampled at **16 kHz** in **WAV format**, with durations ranging from 2.46 to 50.02 seconds (average ~13.79s).

## Supported Tasks
1. **Spoken Mathematical QA** (Direct Answer)

---

## Dataset Statistics

| Split | # Samples | Description |
|-------|-----------|-------------|
| train | 9,076 | All task variants combined |

**Breakdown by task variant:**
- Direct answer (refined): 2,269 entries
- Cascade (transcription+answer): 2,269 entries
- Multiple-choice: 4,538 entries (2 variants per original)

**Audio Characteristics:**
- Unique audio clips: 2,269
- Duration range: 2.46s - 50.02s
- Average duration: 13.79s
- Total duration: ~8.7 hours
- Sampling rate: 16 kHz (all clips)

**Question Type Distribution:**
- short_digit: 100 original (400 total with variants)
- long_digit: 173 original (692 total with variants)
- single_step_reasoning: 594 original (2,376 total with variants)
- multi_step_reasoning: 1,402 original (5,608 total with variants)

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique question ID |
| `path` | Path to audio file (spoken math problem) |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset ("SpokenMQA") |
| `question` | Question prompt |
| `answer` | Answer text |
| `question_type` | Type of math problem (short_digit, long_digit, single_step_reasoning, multi_step_reasoning) |
| `text` | Transcription of the spoken problem |

**Additional fields for specific variants:**
- `task_type`: Task variant identifier (`"transcription_then_answer"` or `"multiple_choice"`)
- `options`: List of answer choices (MCQ only)
- `correct_option`: Correct answer letter (MCQ only)

**ID Formats:**
- Direct answer: `{question_type}_{index}` (e.g., `"short_digit_000000"`)
- Cascade: `{question_type}_{index}_transcribe_answer`
- Multiple-choice: `{question_type}_{index}_mcq_{variant_num}` (variant 1 or 2)

---

## Example Entries

### Direct Answer (Refined):
```json
{"id": "short_digit_000000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenMQA/audio/short_digit_000000.wav", "sampling_rate": 16000, "duration": 4.2, "dataset": "SpokenMQA", "question": "Perform the required arithmetic operation and provide the result.", "answer": "731", "question_type": "short_digit", "text": "what is 892 minus 161"}
```

### Cascade (Transcription+Answer):
```json
{"id": "short_digit_000000_transcribe_answer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenMQA/audio/short_digit_000000.wav", "sampling_rate": 16000, "duration": 4.2, "dataset": "SpokenMQA", "question": "Listen to the question carefully. Transcribe the math problem first followed by providing the answer.", "answer": "Transcription: what is 892 minus 161\nAnswer: 731", "question_type": "short_digit", "text": "what is 892 minus 161", "task_type": "transcription_then_answer"}
```

### Multiple-Choice:
```json
{"id": "short_digit_000000_mcq_1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenMQA/audio/short_digit_000000.wav", "sampling_rate": 16000, "duration": 4.2, "dataset": "SpokenMQA", "question": "Listen to the question carefully. What is the correct answer for the question? (A) 730 (B) 161 (C) 892 (D) 731", "answer": "(D) 731", "question_type": "short_digit", "text": "what is 892 minus 161", "options": ["730", "161", "892", "731"], "correct_option": "D", "task_type": "multiple_choice"}
```

---

## Task Usage

### 1. Spoken Math Question Answering (Direct Answer)
- **Input:** Audio math problem
- **Target field:** `answer`
- **Task:** Listen to the spoken math problem and provide the answer directly

### 2. Transcription-then-Answer (Cascade Task)
- **Input:** Audio math problem
- **Target field:** `answer`
- **Task:** First transcribe the spoken math problem, then provide the solution
- **Format:** `"Transcription: {text}\nAnswer: {answer}"` or `"Transcription: {text}\n\nSolution:\n{steps}\n\nAnswer: {answer}"`

### 3. Multiple-Choice Question Answering
- **Input:** Audio math problem + Multiple-choice options
- **Target field:** `answer`
- **Task:** Select the correct answer from 4 options (A, B, C, D)
- **Format:** `"(D) 731"` or `"Solution:\n{steps}\n\nAnswer: (B) 18"`

---

## Label Space

*This is primarily an open-vocabulary generation task - answers are numeric values or step-by-step explanations. For MCQ variants, the label space is {A, B, C, D}.*

### Question Types

<details>
<summary>Show 4 question types:</summary>

**1. Short Digit (100 entries)**
Simple arithmetic with small numbers (2-3 digits).
- Example: "what is 892 minus 161" → "731"

**2. Long Digit (173 entries)**
Arithmetic with larger numbers (4+ digits).
- Example: "what is 5432 multiplied by 3" → "16296"

**3. Single-Step Reasoning (594 entries)**
Word problems requiring one logical step and basic arithmetic.
- Example: "John has 5 apples. He buys 3 more. How many apples does he have?" → "8"

**4. Multi-Step Reasoning (1,402 entries)**
Complex word problems requiring multiple logical steps and calculations.
- 94.1% include detailed step-by-step solutions
- Example: "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?"
- Answer: "Solution:\nJanet sells 16 - 3 - 4 = 9 duck eggs a day.\nShe makes 9 * 2 = $18 every day at the farmer's market.\n\nAnswer: 18"

</details>

---

## Notes
- All audio files are sampled at **16 kHz** in **WAV format**.
- **Duration range**: 2.46s to 50.02s (average: 13.79s).
- **Multiple variants per audio**: Each unique audio clip has 4 associated variants (refined, cascade, 2× MCQ).
- **Template variety**: 20-40 different prompt templates per question type prevent pattern exploitation.
- **Answer formatting**: All `<<equation>>` markup removed for readability; multi-step solutions formatted with clear "Solution:" and "Answer:" labels.
- **MCQ distractor quality**: Distractors extracted from transcription/solution text or generated numerically close to correct answer.
- **Task characteristics**:
  - **Spoken understanding**: Models must process audio directly
  - **Mathematical reasoning**: Requires arithmetic computation and logical reasoning
  - **Multi-task evaluation**: Same audio used for direct QA, cascade, and MCQ tasks
- **Modeling challenges**:
  - Understanding spoken numbers and mathematical terms
  - Multi-hop reasoning for complex problems
  - Transcription accuracy for cascade task
  - Option selection for MCQ task
- **Applications**:
  - Educational technology and automated math tutoring
  - Accessibility for students with visual or reading difficulties
  - Voice assistants for math problem solving
  - Benchmarking audio-language models on mathematical reasoning
- **Evaluation metrics**:
  - **Direct answer/MCQ**: Exact match accuracy
  - **Cascade**: Transcription WER + answer accuracy
  - **Multi-step**: Step-by-step reasoning quality + final answer accuracy

---

## Citation

If using this dataset, please cite:

```bibtex
@article{ma2025spokenmqa,
  title={Towards Spoken Mathematical Reasoning: Benchmarking Speech-based Models over Multi-faceted Math Problems},
  author={Ma, Wenyi and Li, Zhouyuan and Liang, Yuping and Wang, Tianzi and Liu, Mingjie and Chen, Deyi and Wang, Yiming and Yu, Dong},
  journal={arXiv preprint arXiv:2503.00924},
  year={2025}
}
```

## References
- Paper: https://arxiv.org/abs/2503.00924
- Original dataset: https://huggingface.co/datasets/amao0o0/spoken-mqa
- Related work: GSM8K (text math), SpokenSQuAD (spoken QA), MathVerse (multimodal math)