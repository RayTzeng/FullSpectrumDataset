# MELD (Reasoning QA)

## Overview
**MELD** (Multimodal EmotionLines Dataset) is a multimodal, multi-party emotion recognition corpus built from the TV series *Friends*, containing about **1,433 dialogues** and roughly **13,000 utterances**, with each utterance labeled using seven emotion categories and accompanied by text, audio, and visual modalities.
In the **AudioFlamingo3** LongAudio-XL training pipeline, MELD is repurposed as a source for derived speech QA data, covering tasks such as **comprehension**, **causal reasoning**, and **emotion understanding**. Each audio file is constructed by **concatenating multiple MELD utterances from the same episode** into a single longer segment, creating extended conversation contexts for reasoning tasks. Audio is stored as **WAV** at **16 kHz**.

## Supported Tasks
1. **Conversational Reasoning QA** — Given a multi-party dialogue, answer open-ended questions requiring comprehension of emotions, relationships, actions, and conversational dynamics

---

## Dataset Statistics

| Split | # QA Pairs | # Unique Audio Files | Total Duration | Avg Duration |
|-------|----------:|---------------------:|---------------:|-------------:|
| train | 25,789 | 1,037 | ~8.3h | ~32.0s |

Audio duration ranges from ~1.1 to ~107.8 seconds (~1.8 minutes). Each audio file has 2–35 QA pairs, with an average of ~24.9 QA pairs per file.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique QA pair ID encoding audio file and question index (e.g., `298_Q0`) |
| `path` | Path to audio file (WAV) |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`MELD`) |
| `question` | Open-ended question about the conversation content |
| `answer` | Free-form text answer |

The ID format is `{episode_id}_Q{index}`, where multiple QA pairs sharing the same `{episode_id}` prefix refer to the same audio file.

---

## Example Entries

```json
{"id": "298_Q0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD-concat/train/298.wav", "sampling_rate": 16000, "duration": 15.872, "dataset": "MELD", "question": "Summarize the key points discussed in the given input spoken conversation.", "answer": "Participants express frustration over being left with responsibilities and observe the onset of snow."}

{"id": "298_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD-concat/train/298.wav", "sampling_rate": 16000, "duration": 15.872, "dataset": "MELD", "question": "For the given input spoken conversation, summarize the main emotions expressed.", "answer": "The conversation involves anger, frustration, joy, and sadness."}

{"id": "706_Q0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD-concat/train/706.wav", "sampling_rate": 16000, "duration": 24.234688, "dataset": "MELD", "question": "For the given input spoken conversation, summarize the key emotions and actions described.", "answer": "Participants express joy and surprise during a massage session, highlighting pleasure and relief from sore muscles."}

{"id": "706_Q1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD-concat/train/706.wav", "sampling_rate": 16000, "duration": 24.234688, "dataset": "MELD", "question": "Summarize the negotiation mentioned in the input spoken conversation.", "answer": "The negotiation involves trading massages, with one participant expressing satisfaction from receiving pain relief, while another requests their turn."}
```

---

## Task Usage

### 1. Conversational Reasoning QA
- **Input:** Audio (multi-party dialogue) + `question` (text)
- **Target field:** `answer` (free-form text)

**Task Description:** Answer open-ended questions about conversational content, requiring understanding of emotions, relationships, causal reasoning, and multi-party dynamics in extended dialogue contexts.

---

## Label Space

### Question Types

*This task generates open-vocabulary text — there is no predefined label space.*

Questions span multiple reasoning categories:

<details>
<summary>Show common question patterns:</summary>

**Summarization Questions:**
- "Summarize the key points discussed in the given input spoken conversation."
- "Summarize the input spoken conversation provided."
- "For the given input spoken conversation, summarize the main topics discussed."

**Emotion-Focused Questions:**
- "For the given input spoken conversation, summarize the main emotions expressed."
- "What emotions are conveyed by the speakers during the conversation?"
- "Describe the emotional tone of the interaction."

**Action & Event Questions:**
- "For the given input spoken conversation, summarize the main action items."
- "What actions or decisions are discussed in the conversation?"
- "Describe the sequence of events mentioned."

**Relationship & Social Dynamics:**
- "What can be inferred about the relationship between the speakers?"
- "How do the participants interact with each other?"
- "What social dynamics are evident in the conversation?"

**Causal Reasoning:**
- "Why did the speaker react in this way?"
- "What motivates the participants' decisions?"
- "What caused the conflict/resolution in the conversation?"

**Specific Content Questions:**
- "What negotiation is mentioned in the conversation?"
- "What plan do the speakers discuss?"
- "What problem is being addressed?"

</details>

**Answer Characteristics:**
- Average length: 104 characters
- Range: 3 to 405 characters
- Answers provide concise summaries or explanations
- Often include emotional context, causal relationships, and key conversational points

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips are **concatenations of multiple MELD utterances** from the same episode, creating extended conversational contexts.
- Duration varies significantly, ranging from ~1 second to ~108 seconds, with most clips between 15-50 seconds.
- The dataset is designed for **multi-party conversational understanding** rather than single-speaker monologues.
- **Original MELD characteristics**:
  - Source: TV series *Friends*
  - Multi-party dialogues with emotional context
  - Seven emotion categories: anger, disgust, fear, joy, neutral, sadness, surprise
  - Each utterance includes speaker identity and emotion labels (though QA pairs focus on reasoning)
- **Audio construction**:
  - Concatenated from original MELD utterances
  - Maintains episode coherence (same conversation thread)
  - Preserves natural conversational flow and turn-taking
  - May include multiple speakers within a single audio file
- **QA generation**:
  - Generated as part of the **AudioFlamingo3** LongAudio-XL training pipeline
  - Questions probe understanding of emotions, relationships, and conversational dynamics
  - Answers derived from conversation content analysis
  - Multiple perspectives per audio (2-35 QA pairs per file)
- **Question distribution** (approximate):
  - Summarization: ~30%
  - Emotion-focused: ~20%
  - Action/event: ~15%
  - Relationship/dynamics: ~10%
  - Causal reasoning: ~10%
  - Specific content: ~15%
- The dataset is particularly valuable for:
  - **Conversational AI**: Understanding multi-party dialogue
  - **Emotion recognition**: Identifying emotions from speech
  - **Social intelligence**: Modeling interpersonal dynamics
  - **Long-form reasoning**: Processing extended conversational context
  - **Multimedia understanding**: Bridging audio and language comprehension
  
---

## Audio Construction

### Concatenation Process
Each audio file is created by concatenating multiple MELD utterances:

1. **Source:** Original MELD utterances from the same episode/dialogue
2. **Concatenation:** Multiple utterances combined into single `{episode_id}.wav` file
3. **Utterances per segment:** Varies by dialogue length and complexity
4. **Output location:** `/saltpool0/data/tseng/FullSpectrumDataset/corpus/MELD/MELD-concat/{split}/{episode_id}.wav`

Audio files are distributed across three directories (train/dev/test) based on the original MELD split, but all are consolidated into a single training manifest for the ReasoningQA task.

### QA Generation
- Question-answer pairs generated by LLM based on dialogue content and emotional context
- Multiple QA pairs per audio segment (average: 24.9 pairs)
- Questions probe different aspects: emotions, actions, relationships, causality
- Answers focus on comprehension, summarization, and reasoning

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{poria2019meld,
  title={MELD: A Multimodal Multi-Party Dataset for Emotion Recognition in Conversations},
  author={Poria, Soujanya and Hazarika, Devamanyu and Majumder, Navonil and Naik, Gautam and Cambria, Erik and Mihalcea, Rada},
  booktitle={Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics},
  pages={527--536},
  year={2019}
}
```

## References
- Original MELD dataset: https://affective-meld.github.io/
- MELD on HuggingFace: https://huggingface.co/datasets/declare-lab/MELD
- Source: TV series *Friends* (1994-2004)
- Emotion categories: anger, disgust, fear, joy, neutral, sadness, surprise
- QA pairs generated via AudioFlamingo3 LongAudio-XL training pipeline
