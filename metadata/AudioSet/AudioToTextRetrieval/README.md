# AudioSet Audio-to-Text Retrieval (A2T)

## Overview
**AudioSet Audio-to-Text Retrieval (A2T)** is a dataset designed for evaluating audio-to-text retrieval models, where the task is to select the correct text caption that matches a given audio clip from a set of candidate captions. The dataset pairs AudioSet audio clips with detailed captions from **FusionAudio-1.2M**, with carefully selected distractor captions based on edit distance to create challenging retrieval scenarios. Each sample contains one ground truth caption and 2-4 distractor captions selected at different similarity levels (percentiles: min, 25th, 50th, 75th), making the task progressively more difficult. Audio is sampled at **16 kHz** in **WAV format**, with clips typically lasting **~10 seconds**.

## Supported Tasks
1. **Audio-to-Text Retrieval**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 80,000 |
| test | 1,000 |

**Retrieval Configuration:**
- Candidates per sample: 3-5 (1 ground truth + 2-4 distractors)
- Distractor selection: Edit distance percentiles (min, 25th, 50th, 75th)
- Number of distractors: Randomly varies (2, 3, or 4 per sample)

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique AudioSet clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `ground_truth` | Correct caption for the audio |
| `distractors` | List of 2-4 distractor captions |

**Task Format:** Given the audio at `path`, select the correct caption from the set `{ground_truth} ∪ distractors`.

---

## Example Entries

```json
{"id": "---2_BBVHAA_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "ground_truth": "Clear speech dominated the audio with rhythmic pauses, accompanied by persistent clattering of dishes, pots, and pans in the background. The vocal delivery suggests active participation in a conversation, possibly alongside tasks involving metallic objects.", "distractors": ["Clear speech dominates the audio with intermittent laughter, accompanied by subtle background noises characteristic of a small indoor environment. The vocal interactions create an atmosphere that sounds relaxed and casual.", "A clear speech is heard alongside the consistent, rhythmic operation of a sewing machine in the background. The speech appears instructional, providing guidance on fabric alignment and stitching process, while the sewing machine maintains a steady, repetitive stitching sound throughout the audio.", "The audio features simultaneous speech and music throughout. A male voice speaks continuously with clear articulation, accompanied by sporadic bursts of cheering, whooping, and laughter in the background. The music maintains a consistent presence but remains indistinct in its instrumentation and rhythmic pattern, blending with the vocal content in an overlapping manner.", "A vibrant piano melody with shimmering bell interruptions is the primary auditory element, overlain by a female voice delivering a clear public address announcement. Background chatter and overlapping noises create a dynamic soundscape suggesting a bustling public environment. The music carries a playful and energetic tone while the announcement maintains auditory dominance despite ambient interference."]}

{"id": "---B_v8ZoBY_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---B_v8ZoBY.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "ground_truth": "An energetic live music performance featuring a blend of country rock and blues styles is heard, with a punchy snare drum, shimmering cymbals, and a prominent bassline. The recording exhibits a raw, noisy quality with mono sound, accompanied by enthusiastic audience clapping and lively crowd reactions. A dynamic vocal performance with distortion and rhythmic engagement is central to the track.", "distractors": ["A live jazz performance features a passionate female vocalist accompanied by punchy snare and kick drum hits, shimmering cymbals, a groovy bassline, and wide acoustic rhythm guitar. The recording has a slightly noisy quality characteristic of low fidelity. Breathing is faintly audible at the end of the vocal performance, contributing to the emotional resonance of the piece.", "A loud pig oinking is heard alongside clear human speech that appears conversational. Faint environmental sounds suggest an outdoor setting. The speech is steady and potentially carries a calm or encouraging tone."]}
```

---

## Task Usage

### 1. Audio-to-Text Retrieval
- **Input:** Audio clip (from `path`)
- **Candidates:** `{ground_truth} ∪ distractors` (3-5 captions total)
- **Target:** Select the `ground_truth` caption

**Task Description:** Given an audio clip, rank or select the correct textual description from a set of candidate captions. The model must match audio content to the most accurate caption while rejecting plausible but incorrect distractors.

---

## Distractor Selection Strategy

### Edit Distance-Based Selection
Distractors are selected based on **edit distance** (Levenshtein distance) between the ground truth caption and a large pool of candidate captions:

1. **Sample Pool**: For each audio, sample 1,000 captions from the full dataset
2. **Calculate Distances**: Compute edit distance between ground truth and all sampled captions
3. **Select by Percentiles**: Choose distractors at specific edit distance percentiles

### Distractor Difficulty Levels

**Number of distractors varies randomly (2, 3, or 4):**

- **2 distractors**: Min (most similar) + 50th percentile
- **3 distractors**: Min + 25th percentile + 50th percentile
- **4 distractors**: Min + 25th percentile + 50th percentile + 75th percentile

**Why this matters:**
- **Min (0th percentile)**: Most similar caption → Hardest to distinguish
- **25th-75th percentiles**: Moderate similarity → Increasingly easier
- This creates a **difficulty gradient** within each sample

### Example Difficulty Spectrum

For audio of "dog barking in park":
- **Min**: "A dog barking outdoors in a grassy area" (very similar)
- **25th**: "Animal vocalizations in an outdoor environment" (moderate similarity)
- **50th**: "Outdoor sounds with intermittent animal noises" (less similar)
- **75th**: "Music playing with background nature sounds" (dissimilar)

---

## Label Space

*This is a retrieval task with no predefined label space - models must match audio to the correct caption from the candidate set.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips are approximately **10 seconds** long.
- Audio format is **WAV** (uncompressed).
- This is a **ranking/selection task**, not generation.
- The dataset uses **FusionAudio-1.2M** captions, which are significantly more detailed than traditional audio captions (~48 words average).
- **Distractor selection methodology**:
  - Based on edit distance (character-level similarity)
  - Percentile-based selection ensures diversity in difficulty
  - Excludes identical captions and the same audio
  - Sample pool of 1,000 captions per audio
  - Distractor pool: 80,000 randomly sampled entries
- **Random variability**: Each sample has 2-4 distractors (randomly selected)
  - This creates samples with 3-5 total candidates
  - Tests model robustness across different set sizes
- **Challenge aspects**:
  - **Fine-grained discrimination**: Distractors can be very similar to ground truth
  - **Semantic understanding**: Models must understand both audio and text semantics
  - **Long captions**: Average ~48 words requires detailed comprehension
  - **Acoustic detail**: Captions describe fine-grained audio characteristics
- The dataset is particularly valuable for:
  - **Audio-text alignment**: Learning joint audio-text representations
  - **Cross-modal retrieval**: Bridging audio and language modalities
  - **Contrastive learning**: Training with positive and hard negative samples
  - **Audio understanding evaluation**: Testing comprehension of complex soundscapes
- **Compared to other retrieval datasets**:
  - More detailed captions (48 words vs. ~10 words)
  - Intelligent distractor selection (edit distance percentiles)
  - Variable candidate set sizes (3-5 candidates)
  - Larger audio diversity (AudioSet's 527+ sound classes)
- **Modeling approaches**:
  - Dual-encoder models (separate audio and text encoders)
  - Contrastive learning (CLIP-style)
  - Cross-modal attention mechanisms
  - Ranking-based objectives (triplet loss, InfoNCE)
- The test set is very small (10 samples) and primarily for quick validation
- Train set provides 40,000 retrieval instances with diverse audio content

---

## Evaluation Metrics

Audio-to-text retrieval models are typically evaluated using:

### Ranking Metrics
- **Recall@K (R@K)**: Percentage where ground truth is in top-K predictions
  - R@1: Exact match (ground truth ranked first)
  - R@5: Ground truth in top-5
  - R@10: Ground truth in top-10
- **Mean Reciprocal Rank (MRR)**: Average of 1/rank of ground truth
- **Median Rank**: Median position of ground truth in rankings

### Accuracy Metrics
- **Top-1 Accuracy**: Percentage where ground truth is ranked first
- **Top-K Accuracy**: Percentage where ground truth is in top-K

**Note**: For this dataset with 3-5 candidates, R@1 (Top-1 Accuracy) is the most relevant metric.

---

## Modeling Approaches

### 1. Dual-Encoder Architecture
```
Audio → Audio Encoder → Audio Embedding
Text → Text Encoder → Text Embedding
Similarity = cos(Audio Embedding, Text Embedding)
```
**Example**: CLAP (Contrastive Language-Audio Pretraining)

### 2. Cross-Modal Attention
```
Audio → Audio Encoder ──┐
                        ├─→ Cross-Attention → Score
Text → Text Encoder ────┘
```
**Example**: Transformer with cross-attention layers

### 3. Joint Embedding Space
```
[Audio, Text] → Joint Encoder → Similarity Score
```
**Example**: Unified multimodal transformer

---

## Training Strategies

### Contrastive Learning
- **Positive pair**: (audio, ground_truth)
- **Negative pairs**: (audio, distractor_i) for i ∈ distractors
- **Loss**: InfoNCE, triplet loss, or contrastive loss

### Ranking Loss
- Optimize for ground truth to rank higher than all distractors
- Pairwise ranking loss, listwise ranking loss

### Data Augmentation
- Audio augmentation: time stretching, pitch shifting, noise addition
- Text augmentation: paraphrasing, back-translation (caution: may change semantics)

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
- Task: Audio-to-text retrieval with edit distance-based hard negatives
- Related work: CLAP, AudioCLIP, Wav2CLIP
