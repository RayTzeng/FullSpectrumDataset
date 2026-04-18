# AudioSet Question Answering (QA)

## Overview
**AudioSet Question Answering (QA)** is a large-scale dataset for audio-based question answering, created by pairing AudioSet audio clips with open-ended questions and answers from the **FusionAudio-1.2M** dataset. The dataset contains **4.8 million QA pairs** spanning **1.2 million unique audio clips**, with an average of **~4 QA pairs per audio clip**. Questions are designed to test deep audio understanding, including acoustic analysis, contextual reasoning, temporal dynamics, and semantic interpretation. Audio is sampled at **16 kHz** in **WAV format**, with clips typically lasting **~10 seconds**.

## Supported Tasks
1. **Audio Question Answering**

---

## Dataset Statistics

| Split | # QA Pairs | # Unique Audio | Avg QA/Audio |
|-------|-----------|----------------|--------------|
| train | 4,807,312 | 1,224,668 | 3.93 |

**Audio Characteristics:**
- Average duration: ~10 seconds
- Sampling rate: 16 kHz (all clips)
- Format: WAV (uncompressed)

**QA Characteristics:**
- Average question length: 14.8 words
- Average answer length: 26.4 words
- QA pairs per audio: 1-10+ (average 3.93)
- Question types: Open-ended, reasoning-based, interpretive

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID (AudioSet ID + QA index) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset ("AudioSet") |
| `question` | Question text about the audio |
| `answer` | Answer text |

---

## Example Entries

```json
{"id": "---2_BBVHAA_30_40_QA0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "question": "What might the rhythmic pauses in the speaker's voice suggest about their current activity?", "answer": "The pauses could indicate that the speaker is multitasking, such as performing tasks with metallic objects while conversing, or they might be pausing to allow an unseen participant to respond in a collaborative discussion."}

{"id": "---2_BBVHAA_30_40_QA1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "question": "How might the persistent clattering sounds affect the listener's interpretation of the conversation's setting?", "answer": "The background noise suggests a location filled with metallic objects, likely a kitchen environment. However, it could also imply another space where similar objects are commonly used, leaving ambiguity about the exact setting."}

{"id": "---2_BBVHAA_30_40_QA2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "question": "What potential reasons could explain the speaker's active vocal delivery despite the background noise?", "answer": "The speaker might be intentionally projecting their voice to overcome the clattering sounds, or their energetic tone could reflect enthusiasm about the topic being discussed amidst their tasks."}
```

---

## Task Usage

### 1. Audio Question Answering
- **Input:** Audio clip (from `path`) + Question (from `question`)
- **Target:** Answer (from `answer`)

**Task Description:** Given an audio clip and a natural language question about the audio, generate a detailed answer that demonstrates understanding of the audio content, acoustic characteristics, contextual cues, and reasoning capabilities.

---

## Question Types and Characteristics

### Question Categories

The dataset includes diverse question types that test various aspects of audio understanding:

1. **Acoustic Analysis Questions**
   - "What acoustic characteristics distinguish the primary sound source?"
   - "How would you describe the timbre/pitch/rhythm of the audio?"
   - "What spatial properties can be inferred from the audio?"

2. **Contextual Reasoning Questions**
   - "What might the background sounds suggest about the environment?"
   - "What activity is likely taking place based on the audio?"
   - "What could explain the relationship between different sound sources?"

3. **Temporal Dynamics Questions**
   - "How do the sounds evolve over time?"
   - "What sequence of events can be identified in the audio?"
   - "What changes occur in the audio characteristics?"

4. **Interpretive Questions**
   - "What emotional tone is conveyed by the audio?"
   - "What might the speaker's delivery suggest about their intent?"
   - "How might listeners interpret the overall atmosphere?"

5. **Comparative Questions**
   - "How do the foreground and background sounds differ?"
   - "What distinguishes this sound from similar audio events?"

6. **Causal Questions**
   - "What might cause the observed acoustic patterns?"
   - "Why might the speaker adjust their vocal delivery?"

### Answer Characteristics

Answers in the dataset are:
- **Detailed**: Average 26.4 words (vs. 14.8-word questions)
- **Reasoning-based**: Often include explanations and justifications
- **Context-aware**: Consider multiple interpretations and possibilities
- **Technically informed**: Use appropriate audio terminology
- **Nuanced**: Acknowledge ambiguity and alternative explanations

---

## Label Space

*This is an open-vocabulary generation task - answers are free-form natural language descriptions with no predefined vocabulary.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips are approximately **10 seconds** long.
- Audio format is **WAV** (uncompressed).
- This is a **generative QA task**, not multiple-choice.
- Questions and answers are sourced from **FusionAudio-1.2M**, which provides richer, more context-aware understanding by combining audio with multimodal contextual cues.
- **Multiple QA pairs per audio**:
  - Average: 3.93 QA pairs per audio clip
  - Range: 1-10+ pairs per clip
  - Different questions probe different aspects of the same audio
  - Enables comprehensive evaluation of audio understanding
- **Question complexity**:
  - Open-ended questions requiring reasoning and interpretation
  - Not simple factual questions (e.g., "Is there speech?")
  - Test deep understanding beyond surface-level audio classification
  - Require integration of acoustic, semantic, and contextual knowledge
- **Answer characteristics**:
  - Detailed explanations (average 26.4 words)
  - Often include reasoning, alternatives, and caveats
  - Use technical audio terminology appropriately
  - Acknowledge uncertainty and multiple interpretations
- The dataset inherits AudioSet's diversity:
  - **Music**: Various genres, instruments, vocal styles
  - **Speech**: Conversations, monologues, broadcasts
  - **Environmental sounds**: Nature, urban, indoor, outdoor
  - **Mechanical sounds**: Vehicles, tools, machinery
  - **Animal sounds**: Domestic and wild animals
- **Modeling challenges**:
  - Long-form answer generation (26+ words)
  - Multi-hop reasoning over audio and question
  - Fine-grained acoustic understanding
  - Contextual interpretation and inference
  - Handling ambiguity and multiple valid interpretations
- The dataset is particularly valuable for:
  - **Audio-language understanding**: Bridging audio and natural language
  - **Reasoning evaluation**: Testing models' ability to reason about audio
  - **Fine-grained comprehension**: Beyond simple classification
  - **Accessibility**: Generating explanatory answers about audio content
  - **Conversational audio AI**: Natural language interaction about audio
- **Compared to other QA datasets**:
  - Larger scale: 4.8M QA pairs (vs. typical audio QA datasets with <100k)
  - More audio diversity: AudioSet's 527+ sound classes
  - Longer answers: 26.4 words (vs. short factual answers)
  - Open-ended reasoning: Not constrained to yes/no or multiple-choice
  - Multiple questions per audio: Comprehensive coverage of audio content
- **Training considerations**:
  - Each audio has multiple associated QA pairs
  - Can train on individual QA pairs or leverage shared audio encodings
  - Batching strategies can exploit audio reuse for efficiency
  - Questions probe complementary aspects of the same audio

---

## Evaluation Metrics

Audio question answering models are typically evaluated using:

### Generation Metrics
- **BLEU**: N-gram overlap with reference answers
- **METEOR**: Semantic similarity with synonym matching
- **ROUGE-L**: Longest common subsequence
- **CIDEr**: Consensus-based evaluation (adapted from captioning)
- **BERTScore**: Contextualized embedding similarity
- **BLEURT**: Learned evaluation metric

### Reasoning Metrics
- **Answer accuracy**: Factual correctness of generated answers
- **Reasoning quality**: Logical coherence and justification
- **Completeness**: Coverage of key information

### Human Evaluation Dimensions
- **Relevance**: Answer addresses the question appropriately
- **Correctness**: Factual accuracy relative to audio content
- **Completeness**: Sufficient detail and coverage
- **Fluency**: Grammatical correctness and readability
- **Reasoning**: Quality of explanations and justifications

---

## Modeling Approaches

### 1. Audio Encoder + Language Model
```
Audio → Audio Encoder → Audio Embeddings
Question → Text Encoder → Question Embeddings
[Audio Embeddings, Question Embeddings] → Language Decoder → Answer
```
**Example**: Pre-trained audio encoder (CLAP, AudioMAE) + T5/GPT decoder

### 2. End-to-End Multimodal Transformer
```
Audio + Question → Joint Multimodal Encoder-Decoder → Answer
```
**Example**: Unified transformer with cross-attention between audio and text

### 3. Retrieval-Augmented Generation
```
Audio + Question → Retrieve Similar Examples → Generate with Context → Answer
```
**Example**: Retrieve similar QA pairs, use as few-shot context for generation

### 4. Instruction-Tuned Audio-Language Models
```
Audio + "Question: {question}\nAnswer:" → Instruction-Tuned LLM → Answer
```
**Example**: LLaMA/GPT fine-tuned with audio prefix encoders

---

## Training Strategies

### Supervised Fine-Tuning
- Train on (audio, question) → answer pairs
- Standard cross-entropy loss on answer tokens
- Can leverage pre-trained audio and language models

### Multi-Task Learning
- Joint training on QA + captioning + retrieval tasks
- Share audio encoder across tasks
- Improves audio representation quality

### Data Efficiency
- **Audio reuse**: Each audio has multiple QA pairs
- **Batching strategy**: Group QA pairs by audio to reuse encodings
- **Progressive training**: Start with simpler questions, increase difficulty

### Curriculum Learning
- Order training by question complexity
- Start with factual questions, progress to reasoning questions
- Gradually increase answer length requirements

---

## Implementation Example

```python
import json
import gzip
import torch
from torch.utils.data import Dataset

class AudioQADataset(Dataset):
    def __init__(self, manifest_file, audio_processor, text_processor):
        self.audio_processor = audio_processor
        self.text_processor = text_processor

        # Load manifest
        self.samples = []
        with gzip.open(manifest_file, 'rt', encoding='utf-8') as f:
            for line in f:
                self.samples.append(json.loads(line))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        # Process audio
        audio_features = self.audio_processor(sample['path'])

        # Process question
        question_tokens = self.text_processor(sample['question'])

        # Process answer (target)
        answer_tokens = self.text_processor(sample['answer'])

        return {
            'audio': audio_features,
            'question': question_tokens,
            'answer': answer_tokens,
            'id': sample['id']
        }
```

---

## Citation

If using this dataset, please cite:

```bibtex
@article{fusionaudio2024,
  title={FusionAudio: A Large-Scale Dataset for Fine-Grained Audio Captioning},
  author={[Authors TBD]},
  journal={arXiv preprint},
  year={2024}
}

@inproceedings{audioset2017,
  title={Audio Set: An ontology and human-labeled dataset for audio events},
  author={Gemmeke, Jort F and Ellis, Daniel PW and Freedman, Dylan and Jansen, Aren and Lawrence, Wade and Moore, R Channing and Plakal, Manoj and Ritter, Marvin},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={776--780},
  year={2017},
  organization={IEEE}
}
```

## References
- FusionAudio dataset: https://huggingface.co/datasets/SatsukiVie/FusionAudio
- AudioSet: https://research.google.com/audioset/
- Task: Open-ended audio question answering with reasoning
- Related work: Audio-language pre-training models (CLAP, AudioGen, LTU)
