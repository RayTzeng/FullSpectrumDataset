# VoxCeleb1 - Speaker Similarity Estimation

## Overview
**VoxCeleb1** is a large-scale text-independent speaker recognition corpus collected automatically from YouTube interview videos, with speech recorded under realistic in-the-wild conditions such as background noise, overlapping speech, and channel variation. It contains over **100,000 utterances** from **1,251 celebrities**, and is widely used for speaker identification and speaker verification research.

This **similarity** subset contains **pairwise speaker comparisons** with continuous similarity ratings for speaker similarity estimation tasks, based on the **VoxSIM (VoxCeleb Speaker Similarity)** dataset. Unlike binary verification, this task requires models to predict **fine-grained similarity scores** ranging from **1.0 (completely different)** to **6.0 (identical)**, reflecting the degree of perceptual similarity between two voices. Audio is recorded at **16 kHz** and similarity ratings are derived from human perceptual judgments collected via crowdsourced listening tests as described in the VoxSIM paper.

## Supported Tasks
1. **Speaker Similarity Estimation**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 23,671 |
| test | 2,597 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique pair ID (format: utterance1___utterance2) |
| `paths` | List of 2 paths to audio files |
| `sampling_rates` | List of 2 sampling rates (both 16000 Hz) |
| `durations` | List of 2 audio durations in seconds |
| `dataset` | Source dataset |
| `label` | Binary label: `0` (different speakers) or `1` (same speaker) |
| `similarity` | Continuous similarity score (1.0-6.0) |

---

## Example Entries

```json
{"id": "id10001_1zcIwhmdeo4_00001___id10453_2q9ZA1_VeGM_00003", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10001/1zcIwhmdeo4/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10453/2q9ZA1_VeGM/00003.wav"], "sampling_rates": [16000, 16000], "durations": [8.12, 7.08], "dataset": "VoxCeleb1", "label": 0, "similarity": 3.0}

{"id": "id10001_7gWzIy6yIIk_00001___id10001_7gWzIy6yIIk_00003", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10001/7gWzIy6yIIk/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10001/7gWzIy6yIIk/00003.wav"], "sampling_rates": [16000, 16000], "durations": [8.64, 6.56], "dataset": "VoxCeleb1", "label": 1, "similarity": 6.0}

{"id": "id10016_5xGJYiNH2Jw_00001___id10016_ocnz4PPv-RQ_00004", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10016/5xGJYiNH2Jw/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10016/ocnz4PPv-RQ/00004.wav"], "sampling_rates": [16000, 16000], "durations": [5.28, 5.92], "dataset": "VoxCeleb1", "label": 1, "similarity": 4.0}
```

---

## Task Usage

### 1. Speaker Similarity Estimation
- **Input:** Two audio utterances (`paths[0]` and `paths[1]`)
- **Target field:** `similarity` (continuous regression)
- **Alternative target:** `label` (binary classification as auxiliary task)
- **Task:** Predict the perceptual similarity score between two voices

---

## Label Space

### Similarity Scores
- **Range**: 1.0 to 6.0
- **Type**: Continuous regression task (discretized to 0.1 intervals)
- **Granularity**: 21 unique values (1.0, 1.3, 1.5, 1.7, 2.0, ..., 5.5, 5.7, 6.0)
- **Interpretation**:
  - **1.0**: Completely different - Clearly distinct speakers with no perceptual similarity
  - **2.0-3.0**: Low similarity - Different speakers with some shared vocal characteristics
  - **4.0**: Moderate similarity - Noticeably similar voices but still distinguishable
  - **5.0**: High similarity - Very similar sounding speakers, difficult to distinguish
  - **6.0**: Identical - Same speaker, or perceptually indistinguishable voices

### Binary Labels
<details>
<summary>Show 2 available labels:</summary>

`0` - Different speakers
`1` - Same speaker

**Note:** The `label` field provides ground-truth speaker identity, which can be used as an auxiliary signal alongside the continuous `similarity` scores.

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration**, typically ranging from 3 to 20 seconds.
- Each sample contains **two audio files** forming a comparison pair.
- This is a **pairwise regression** task where the model must predict fine-grained perceptual similarity.
- Similarity scores are based on **human perceptual judgments** from the **VoxSIM** paper.
- The **VoxSIM (VoxCeleb Speaker Similarity)** annotations were collected as follows:
  - Crowdsourced listening tests with human raters
  - Multiple raters per pair to ensure reliability
  - Scores aggregated and averaged across raters to produce the final similarity ratings
  - Raters were asked to judge perceptual similarity on a scale from 1 (completely different) to 6 (identical)
- Both **same-speaker** and **different-speaker** pairs are included:
  - Same-speaker pairs typically have higher similarity scores (4.0-6.0)
  - Different-speaker pairs have more variable scores (1.0-5.0) depending on voice similarity
- **Important distinction from verification:**
  - Verification: Binary decision (same/different speaker)
  - Similarity: Continuous scale capturing **degree** of perceptual similarity
  - Different speakers can have high similarity scores if their voices sound alike
- **Evaluation metrics**:
  - Mean Squared Error (MSE) or Mean Absolute Error (MAE) for regression
  - Spearman/Pearson correlation with human ratings
  - Ranking metrics (e.g., Kendall's tau) for relative comparisons
- This dataset captures **in-the-wild variability** including:
  - Background noise (music, laughter, ambient sounds)
  - Acoustic conditions (different rooms, microphones, compression)
  - Speaking styles (conversational, interview, debate)
  - Channel effects (YouTube compression, various recording devices)
  - Spontaneous speech characteristics
- Applications include:
  - **Voice casting**: Finding similar-sounding voice actors or speakers
  - **Speaker clustering**: Grouping voices by perceptual similarity
  - **Voice conversion evaluation**: Assessing how similar converted voices are to targets
  - **Psychoacoustic research**: Studying perceptual dimensions of voice similarity
  - **Fine-grained speaker retrieval**: Finding speakers with similar vocal characteristics
  - **Voice synthesis quality assessment**: Evaluating naturalness and speaker similarity
- The **text-independent** nature means no constraints on spoken content—similarity must be judged on vocal characteristics alone.
- The dataset is particularly challenging due to:
  - **Subjective perception**: Similarity is inherently subjective and varies across listeners
  - **Multi-dimensional similarity**: Voice similarity depends on pitch, timbre, accent, speaking rate, etc.
  - **Real-world noise**: Uncontrolled recording environments affect perception
  - **Context dependency**: Similarity judgments can be influenced by speaking context
- Unlike binary verification, this task requires models to learn **nuanced perceptual representations** that correlate with human similarity judgments.
- The `id` field concatenates both utterance identifiers with `___` separator for easy pair tracking.
- Speaker IDs are embedded in the file paths (e.g., `id10001`, `id10016`).

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{nagrani2017voxceleb,
  title={VoxCeleb: A Large-Scale Speaker Identification Dataset},
  author={Nagrani, Arsha and Chung, Joon Son and Zisserman, Andrew},
  booktitle={Proc. INTERSPEECH},
  pages={2616--2620},
  year={2017}
}

@article{huh2023voxsim,
  title={Towards Measuring Perceptual Similarity of Voices},
  author={Huh, Jee-weon and Chung, Joon Son and Huh, Jaesung and Zisserman, Andrew},
  journal={arXiv preprint arXiv:2312.01174},
  year={2023}
}
```

## References
- Official website: https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html
- VoxCeleb1 paper: https://arxiv.org/abs/1706.08612
- VoxSIM paper: https://arxiv.org/abs/2312.01174
- VoxSIM data: https://www.robots.ox.ac.uk/~vgg/data/voxsim/
