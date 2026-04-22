# SpokenSQuAD - Spoken Question Answering

## Overview
**SpokenSQuAD** is a benchmark for **spoken question answering** (also known as listening comprehension) in which the document/passage is provided as **speech** while the question is given as **text**, adapting the original SQuAD task to the spoken domain. It was created by converting SQuAD passages into spoken audio using text-to-speech synthesis, and is presented as the first large-scale spoken question answering dataset. The dataset contains **37,111 training** and **5,351 test** question-answer pairs derived from **16,035 training** and **1,896 test** audio passages, with audio recorded at **24 kHz** and passage durations ranging from less than 1 second to over 80 seconds (average ~13 seconds).

Unlike traditional text-based question answering, SpokenSQuAD requires models to process spoken language in addition to understanding the semantic content, presenting challenges such as handling variability in prosody, speaker characteristics, and the sequential nature of audio.

## Supported Tasks
1. **Spoken Question Answering**

---

## Dataset Statistics

| Split | # Audio Passages | # Q&A Pairs |
|-------|----------------:|------------:|
| train | 16,035 | 37,111 |
| test | 1,896 | 5,351 |

---

## Data Format

The dataset provides two manifest formats:

### Format 1: One Q&A pair per line
Files: `train.jsonl.gz`, `test.jsonl.gz`

Each sample is a single question-answer pair with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique Q&A ID (format: passage_id_Q{num}, e.g., "0_0_0_Q1") |
| `path` | Path to audio file (spoken passage) |
| `sampling_rate` | Audio sampling rate (24000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `question` | Text question about the audio passage |
| `answer` | Text answer (extractive span from original passage text) |

### Format 2: Multiple Q&A pairs per audio
Files: `train_merged.jsonl.gz`, `test_merged.jsonl.gz`

Each sample groups all question-answer pairs for a single audio passage:

| Field | Description |
|------|-------------|
| `id` | Unique passage ID (e.g., "0_0_0") |
| `path` | Path to audio file (spoken passage) |
| `sampling_rate` | Audio sampling rate (24000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `questions` | List of text questions about the audio passage |
| `answers` | List of text answers corresponding to each question |

---

## Example Entries

### Format 1 (One Q&A per line)

```json
{"id": "0_0_0_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenSQuAD/Spoken-SQuAD_audio/train_wav/0_0_0.wav", "sampling_rate": 24000, "duration": 3.768, "dataset": "SpokenSQuAD-train", "question": "What is in front of the Notre Dame Main Building?", "answer": "a copper statue of christ"}

{"id": "0_0_0_Q2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenSQuAD/Spoken-SQuAD_audio/train_wav/0_0_0.wav", "sampling_rate": 24000, "duration": 3.768, "dataset": "SpokenSQuAD-train", "question": "The Basilica of the Sacred heart at Notre Dame is beside to which structure?", "answer": "the main building"}
```

### Format 2 (Multiple Q&A per audio)

```json
{"id": "0_0_0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpokenSQuAD/Spoken-SQuAD_audio/train_wav/0_0_0.wav", "sampling_rate": 24000, "duration": 3.768, "dataset": "SpokenSQuAD-train", "questions": ["What is in front of the Notre Dame Main Building?", "The Basilica of the Sacred heart at Notre Dame is beside to which structure?"], "answers": ["a copper statue of christ", "the main building"]}
```

---

## Task Usage

### 1. Spoken Question Answering
- **Input:**
  - Audio passage (spoken document)
  - Text question about the passage content
- **Target field:** `answer` (Format 1) or `answers` (Format 2)
- **Task:** Listen to the spoken passage and answer the text question based on the information conveyed in the audio
- **Answer type:** Extractive text spans from the original passage (before TTS conversion)

---

## Dataset Characteristics

### Passage Statistics
- **Total audio passages**: 16,035 training, 1,896 test
- **Duration range**: 0.72s to 86.98s
- **Average duration**: ~12.85 seconds
- **Sampling rate**: 24 kHz

### Question-Answer Statistics
- **Total Q&A pairs**: 37,111 training, 5,351 test
- **Q&A pairs per passage**: 1 to 17 (average ~2.31 per passage)
- **Question format**: Natural language text questions
- **Answer format**: Extractive text spans (lowercase)

---

## Notes
- All audio files are sampled at **24 kHz**.
- Audio passages have **variable duration**, ranging from less than 1 second to over 86 seconds, with an average of approximately 13 seconds.
- **Two manifest formats** are provided for different use cases:
  - **Format 1** (`train.jsonl.gz`, `test.jsonl.gz`): One Q&A pair per line, suitable for training models that process individual questions
  - **Format 2** (`train_merged.jsonl.gz`, `test_merged.jsonl.gz`): All Q&A pairs for a passage grouped together, suitable for batch processing or efficient audio loading
- **Multimodal task**: Models must process both **audio** (spoken passage) and **text** (question) inputs to generate text answers.
- **Audio generation**: Passages were synthesized from SQuAD text using text-to-speech (TTS) systems, providing consistent high-quality audio.
- **Answer format**: Answers are provided as text spans extracted from the original passage before TTS conversion, normalized to lowercase.
- **Comparison to text-based SQuAD**:
  - Original SQuAD: Both passage and question are text
  - SpokenSQuAD: Passage is audio, question is text
  - Introduces challenges: speech recognition, temporal processing, prosody understanding
  - Preserves the same question-answer pairs from SQuAD
- **Task challenges**:
  - **Auditory processing**: Models must process sequential audio input rather than random-access text
  - **Speech understanding**: Requires handling TTS artifacts, prosody, and speaking rate variations
  - **Information extraction**: Must locate and extract relevant information from temporal audio
  - **Cross-modal reasoning**: Integrating audio passage understanding with text question comprehension
  - **Long-form audio**: Some passages exceed 80 seconds, requiring long-context audio processing
- **Evaluation metrics**:
  - **Exact Match (EM)**: Percentage of predictions that exactly match ground truth answers
  - **F1 Score**: Token-level overlap between predicted and ground truth answers
  - Standard SQuAD evaluation metrics applied to predicted text answers
- **Applications include**:
  - **Voice assistants**: Answering questions about spoken content (podcasts, lectures, audiobooks)
  - **Audio indexing**: Extracting specific information from audio documents
  - **Accessibility**: Enabling Q&A over audio content for users who prefer or require audio interfaces
  - **Educational technology**: Testing listening comprehension in language learning
  - **Meeting analytics**: Answering queries about recorded conversations or presentations
- **Model approaches**:
  - **Pipeline**: Speech recognition → text QA
  - **End-to-end**: Direct audio-to-text QA without intermediate ASR
  - **Multimodal transformers**: Joint audio-text encoding
- **Dataset construction**:
  - Source: Stanford Question Answering Dataset (SQuAD)
  - Passages converted to audio via TTS synthesis
  - Questions and answers retained from original SQuAD
  - Maintains same data splits and question-answer associations
- **Key differences from related tasks**:
  - Unlike **Audio Question Answering (AudioQA)**: Questions are text, not audio
  - Unlike **Speech Recognition**: Requires understanding and reasoning, not just transcription
  - Unlike **Audio Captioning**: Answers specific questions rather than general descriptions
- The `id` field format in Format 1 includes `_Q{num}` suffix to distinguish multiple questions for the same audio passage.
- **Note on answer alignment**: Answers are text spans from the original passage; models need to understand the spoken audio well enough to locate these spans conceptually, though they predict the text directly.
- Some passages have only 1 question while others have up to 17 questions, reflecting the varying complexity and information density of different passages.

---

## Citation

If using this dataset, please cite:

```bibtex
@article{li2018spoken,
  title={Spoken SQuAD: A Study of Mitigating the Impact of Speech Recognition Errors on Listening Comprehension},
  author={Li, Chia-Hsuan and Lee, Szu-Lin and Chung, Chi-Liang and Lee, Hung-yi},
  journal={arXiv preprint arXiv:1804.00320},
  year={2018}
}

@inproceedings{rajpurkar2016squad,
  title={SQuAD: 100,000+ Questions for Machine Comprehension of Text},
  author={Rajpurkar, Pranav and Zhang, Jian and Lopyrev, Konstantin and Liang, Percy},
  booktitle={Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing},
  pages={2383--2392},
  year={2016}
}
```

## References
- SpokenSQuAD paper: https://arxiv.org/abs/1804.00320
- Original SQuAD: https://rajpurkar.github.io/SQuAD-explorer/
- SQuAD paper: https://arxiv.org/abs/1606.05250
