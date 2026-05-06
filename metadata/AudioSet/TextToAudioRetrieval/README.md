# AudioSet Text-to-Audio Retrieval (T2A)

## Overview
**AudioSet Text-to-Audio Retrieval (T2A)** is a dataset designed for evaluating text-to-audio retrieval models, where the task is to select the correct audio clip that matches a given text caption from a set of candidate audio files. The dataset pairs detailed captions from **FusionAudio-1.2M** with AudioSet audio clips, with carefully selected distractor audio files based on caption edit distance to create challenging retrieval scenarios. Each sample contains one ground truth audio and 1-4 distractor audio files (resulting in 2-5 total candidates) selected at different caption similarity levels, making the task progressively more difficult. Audio is sampled at **16 kHz** in **WAV format**, with clips typically lasting **~10 seconds**.

## Supported Tasks
1. **Text-to-Audio Retrieval**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 80,000 |
| test | 1,000 |

**Retrieval Configuration:**
- Candidates per sample: 2-5 audio files (1 ground truth + 1-4 distractors)
- Distractor selection: Caption edit distance percentiles (min, 25th, 50th, 75th)
- Number of distractors: Randomly varies (1, 2, 3, or 4 per sample)

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (from ground truth audio) |
| `paths` | List of audio file paths (shuffled: 1 ground truth + distractors) |
| `sampling_rates` | List of sampling rates for each audio file |
| `durations` | List of durations (seconds) for each audio file |
| `caption` | Text caption describing the ground truth audio |
| `label` | Index of the ground truth audio in the `paths` list |

**Task Format:** Given the `caption`, select the correct audio from `paths[label]` among all candidates in `paths`.

---

## Example Entries

```json
{"id": "---2_BBVHAA_30_40", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/NSfRk9QKkVc.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav"], "sampling_rates": [16000, 16000], "durations": [9.984, 10.016], "caption": "Clear speech dominated the audio with rhythmic pauses, accompanied by persistent clattering of dishes, pots, and pans in the background. The vocal delivery suggests active participation in a conversation, possibly alongside tasks involving metallic objects.", "label": 1}

{"id": "---B_v8ZoBY_30_40", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/8WsZTrCsv_I.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---B_v8ZoBY.wav"], "sampling_rates": [16000, 16000], "durations": [10.016, 10.016], "caption": "An energetic live music performance featuring a blend of country rock and blues styles is heard, with a punchy snare drum, shimmering cymbals, and a prominent bassline. The recording exhibits a raw, noisy quality with mono sound, accompanied by enthusiastic audience clapping and lively crowd reactions. A dynamic vocal performance with distortion and rhythmic engagement is central to the track.", "label": 1}

{"id": "---fcVQUf3E_30_40", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/srm46EYK2uA.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/8eYEfvta0RM.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/0r9HPRJUaFo.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---fcVQUf3E.wav", "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/EnZA9bw-VY0.wav"], "sampling_rates": [16000, 16000, 16000, 16000, 16000], "durations": [9.952, 9.984, 10.016, 10.016, 10.016], "caption": "A prominent vehicle engine sound dominates the audio, likely characteristic of a water vehicle, accompanied by sustained wind and water environmental sounds. Intermittent low-frequency impact noises are heard, possibly corresponding to wave collisions against a submerged structure or nearby objects. The audio maintains consistent outdoor ambiance with marine environmental characteristics throughout.", "label": 3}
```

---

## Task Usage

### 1. Text-to-Audio Retrieval
- **Input:** Text caption
- **Candidates:** Audio files in `paths` (2-5 audio clips total)
- **Target:** Select the audio at index `label` (ground truth)

**Task Description:** Given a text description, rank or select the correct audio clip from a set of candidate audio files. The model must match textual descriptions to the most accurate audio while rejecting plausible but incorrect distractor audio clips.

---

## Distractor Selection Strategy

### Caption Edit Distance-Based Selection
Distractor audio files are selected based on **edit distance** between their captions and the ground truth caption:

1. **Sample Pool**: For each sample, sample 1,000 entries from the full dataset
2. **Calculate Distances**: Compute edit distance between ground truth caption and sampled captions
3. **Select Audio by Caption Similarity**: Choose distractor audio files whose captions are at specific edit distance percentiles

### Distractor Difficulty Levels

**Number of distractors varies randomly (1, 2, 3, or 4):**

- **1 distractor**: Min (most similar caption) → 2 total candidates
- **2 distractors**: Min + 50th percentile → 3 total candidates
- **3 distractors**: Min + 25th + 50th percentile → 4 total candidates
- **4 distractors**: Min + 25th + 50th + 75th percentile → 5 total candidates

**Why this matters:**
- **Min (0th percentile)**: Audio with most similar caption → Hardest to distinguish
- **25th-75th percentiles**: Audio with moderately similar captions → Increasingly easier
- This creates a **difficulty gradient** within each sample
- Variable candidate set sizes test model robustness

### Example Difficulty Spectrum

For caption "dog barking in park":
- **Min**: Audio of dog barking outdoors in grassy area (very similar)
- **25th**: Audio of animal vocalizations in outdoor environment (moderate)
- **50th**: Audio of outdoor sounds with intermittent animal noises (less similar)
- **75th**: Audio of music playing with background nature sounds (dissimilar)

---

## Label Space

*This is a retrieval task with no predefined label space - models must match text captions to the correct audio from the candidate set.*

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips are approximately **10 seconds** long.
- Audio format is **WAV** (uncompressed).
- This is a **ranking/selection task**, not generation.
- The dataset uses **FusionAudio-1.2M** captions, which are significantly more detailed than traditional audio captions (~48 words average).
- **Distractor selection methodology**:
  - Based on **caption edit distance** (character-level similarity)
  - Distractor audio selected when their captions are similar to ground truth
  - This creates acoustically diverse but semantically similar options
  - Percentile-based selection ensures diversity in difficulty
  - Excludes identical captions and the same audio
  - Sample pool: 1,000 entries per sample
  - Distractor pool: 100,000 randomly sampled entries
- **Random variability**: Each sample has 1-4 distractors (randomly selected)
  - This creates samples with 2-5 total candidate audio files
  - Tests model robustness across different set sizes
  - Simulates real-world retrieval scenarios with variable result sets
- **Key difference from A2T**:
  - **T2A (this task)**: Given text, find matching audio among audio candidates
  - **A2T**: Given audio, find matching text among text candidates
  - T2A is often considered harder because audio distractors with similar captions can sound quite different
- **Challenge aspects**:
  - **Caption-based distractor selection**: Audio distractors have similar captions but different acoustics
  - **Semantic vs. acoustic alignment**: Models must handle cases where similar descriptions have different sounds
  - **Fine-grained audio discrimination**: Distinguishing between acoustically diverse clips with similar semantics
  - **Long caption understanding**: Average ~48 words requires detailed comprehension
  - **Variable set sizes**: 2-5 candidates per sample
- The dataset is particularly valuable for:
  - **Text-to-audio search**: Retrieving audio based on textual queries
  - **Cross-modal retrieval**: Bridging language and audio modalities
  - **Audio-text alignment**: Learning joint representations
  - **Content discovery**: Finding relevant audio from descriptions
- **Compared to other retrieval datasets**:
  - More detailed captions (48 words vs. ~10 words)
  - Intelligent distractor selection (caption edit distance)
  - Variable candidate set sizes (2-5 candidates)
  - Larger audio diversity (AudioSet's 527+ sound classes)
  - Caption-based audio distractor selection (unique approach)
- **Modeling approaches**:
  - Dual-encoder models (separate text and audio encoders)
  - Contrastive learning (CLIP-style)
  - Cross-modal attention mechanisms
  - Ranking-based objectives (triplet loss, InfoNCE)
- The test set is very small (10 samples) and primarily for quick validation
- Train set provides 40,000 retrieval instances with diverse audio content
- **Shuffling**: Audio candidates are shuffled, and `label` indicates the correct position
  - This prevents models from learning positional biases
  - Models must evaluate all candidates independently

---

## Evaluation Metrics

Text-to-audio retrieval models are typically evaluated using:

### Ranking Metrics
- **Recall@K (R@K)**: Percentage where ground truth is in top-K predictions
  - R@1: Exact match (ground truth ranked first)
  - R@5: Ground truth in top-5 (applicable when candidates > 5)
  - R@10: Ground truth in top-10 (applicable when candidates > 10)
- **Mean Reciprocal Rank (MRR)**: Average of 1/rank of ground truth
- **Median Rank**: Median position of ground truth in rankings

### Accuracy Metrics
- **Top-1 Accuracy**: Percentage where ground truth is ranked first
- **Top-K Accuracy**: Percentage where ground truth is in top-K

**Note**: For this dataset with 2-5 candidates, R@1 (Top-1 Accuracy) is the most relevant metric.

### Per-Set-Size Evaluation
Evaluate separately for different candidate set sizes:
- 2-candidate accuracy (1 distractor)
- 3-candidate accuracy (2 distractors)
- 4-candidate accuracy (3 distractors)
- 5-candidate accuracy (4 distractors)

---

## Modeling Approaches

### 1. Dual-Encoder Architecture
```
Text → Text Encoder → Text Embedding
Audio → Audio Encoder → Audio Embedding
Similarity = cos(Text Embedding, Audio Embedding)
```
**Example**: CLAP (Contrastive Language-Audio Pretraining)

### 2. Cross-Modal Attention
```
Text → Text Encoder ──┐
                      ├─→ Cross-Attention → Score
Audio → Audio Encoder ┘
```
**Example**: Transformer with cross-attention layers

### 3. Joint Embedding Space
```
[Text, Audio] → Joint Encoder → Similarity Score
```
**Example**: Unified multimodal transformer

---

## Training Strategies

### Contrastive Learning
- **Positive pair**: (caption, audio_at_label)
- **Negative pairs**: (caption, audio_i) for i ≠ label in paths
- **Loss**: InfoNCE, triplet loss, or contrastive loss

### Ranking Loss
- Optimize for ground truth audio to rank higher than all distractors
- Pairwise ranking loss, listwise ranking loss

### Hard Negative Mining
- Distractors are already hard negatives (similar captions)
- Can further mine within-batch negatives

### Data Augmentation
- **Audio augmentation**: time stretching, pitch shifting, noise addition, SpecAugment
- **Text augmentation**: Use with caution (paraphrasing may change semantics)

---

## Implementation Example

```python
import json
import gzip
import torch
from torch.utils.data import Dataset

class T2ARetrievalDataset(Dataset):
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

        # Process caption
        caption_embed = self.text_processor(sample['caption'])

        # Process all audio candidates
        audio_embeds = []
        for audio_path in sample['paths']:
            audio_embed = self.audio_processor(audio_path)
            audio_embeds.append(audio_embed)

        audio_embeds = torch.stack(audio_embeds)
        label = sample['label']

        return {
            'caption': caption_embed,
            'audio_candidates': audio_embeds,
            'label': label
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
- Task: Text-to-audio retrieval with caption edit distance-based hard negatives
- Related work: CLAP, AudioCLIP, Wav2CLIP
