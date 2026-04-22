# VoxCeleb1 - Speaker Discriminability (ABX)

## Overview
**VoxCeleb1** is a large-scale text-independent speaker recognition corpus collected automatically from YouTube interview videos, with speech recorded under realistic in-the-wild conditions such as background noise, overlapping speech, and channel variation. It contains over **100,000 utterances** from **1,251 celebrities**, and is widely used for speaker identification and speaker verification research.

This **ABX** subset contains **triplet speaker comparisons** for speaker discriminability evaluation using the ABX paradigm. In this task, given three utterances **(A, B, X)**, the goal is to determine whether utterance **X** is spoken by the same speaker as **A** or **B**. This tests a model's ability to discriminate between speakers and make relative similarity judgments. Audio is recorded at **16 kHz** and the task is formulated as binary classification where `label=0` means X matches B, and `label=1` means X matches A.

## Supported Tasks
1. **Speaker Discriminability (ABX)**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 50,000 |
| test | 2,000 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique triplet ID (format: utteranceA___utteranceB___utteranceX) |
| `paths` | List of 3 paths to audio files [A, B, X] |
| `sampling_rates` | List of 3 sampling rates (all 16000 Hz) |
| `durations` | List of 3 audio durations in seconds |
| `dataset` | Source dataset |
| `label` | Triplet label: `-1` (X is different speaker), `0` (X matches A), or `1` (X matches B) |

---

## Example Entries

```json
{"id": "id10617__kLMI9NQeYo_00005___id10829_yDmlMdgj02k_00001___id10829_fGhSkJg4Sd4_00004", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10617/_kLMI9NQeYo/00005.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10829/yDmlMdgj02k/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10829/fGhSkJg4Sd4/00004.wav"], "sampling_rates": [16000, 16000, 16000], "durations": [7.52, 16.44, 9.28], "dataset": "VoxCeleb1", "label": 1}

{"id": "id10755_TDyD4qWf1YI_00006___id10765_PX4U75dJiHc_00001___id10755_TDyD4qWf1YI_00011", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10755/TDyD4qWf1YI/00006.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10765/PX4U75dJiHc/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10755/TDyD4qWf1YI/00011.wav"], "sampling_rates": [16000, 16000, 16000], "durations": [4.6, 7.52, 4.48], "dataset": "VoxCeleb1", "label": 0}

{"id": "id10920_tSK2L3U4D0I_00001___id10741_OzoaS8Y07ao_00005___id10242_RMDXpJ5e_kE_00003", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10920/tSK2L3U4D0I/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10741/OzoaS8Y07ao/00005.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10242/RMDXpJ5e_kE/00003.wav"], "sampling_rates": [16000, 16000, 16000], "durations": [8.08, 4.96, 6.6], "dataset": "VoxCeleb1", "label": -1}

{"id": "id10286_9K2YB1d8BqY_00004___id10300_Xroutc-3_SU_00004___id10300_Fi8lnFPYgII_00001", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/test/wav/id10286/9K2YB1d8BqY/00004.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/test/wav/id10300/Xroutc-3_SU/00004.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/test/wav/id10300/Fi8lnFPYgII/00001.wav"], "sampling_rates": [16000, 16000, 16000], "durations": [4.08, 11.44, 6.0], "dataset": "VoxCeleb1", "label": 1}
```

---

## Task Usage

### 1. Speaker Discriminability (ABX)
- **Input:** Three audio utterances (`paths[0]`, `paths[1]`, `paths[2]`)
  - **A** = `paths[0]` (anchor from speaker 1)
  - **B** = `paths[1]` (anchor from speaker 2)
  - **X** = `paths[2]` (test utterance to classify)
- **Target field:** `label` (3-way classification)
- **Task:** Determine whether X matches A, matches B, or is from a different speaker

---

## Label Space

### ABX Labels
<details>
<summary>Show 3 available labels:</summary>

`-1` - X is from a different speaker (neither A nor B)
`0` - X matches A (utterance X is from the same speaker as anchor A)
`1` - X matches B (utterance X is from the same speaker as anchor B)

</details>

### Label Distribution (Training Set)
- **Different speaker (`-1`)**: 16,668 samples (33.3%)
- **X matches A (`0`)**: 16,666 samples (33.3%)
- **X matches B (`1`)**: 16,666 samples (33.3%)

The dataset is **perfectly balanced** across all three label categories.

---

## ABX Task Formulation

The **ABX paradigm** is a classic perceptual discrimination task adapted for speaker recognition:

1. **Given:** Three utterances **(A, B, X)**
   - A and B are from **different speakers** (anchors)
   - X can be from **A's speaker**, **B's speaker**, or a **third different speaker**

2. **Question:** Does X match A, match B, or neither?

3. **Decision rule:**
   - Compute similarity: `sim(A, X)` and `sim(B, X)`
   - If `sim(A, X)` and `sim(B, X)` are both below threshold: Predict `label=-1` (different speaker)
   - Else if `sim(A, X) > sim(B, X)`: Predict `label=0` (X matches A)
   - Else: Predict `label=1` (X matches B)

4. **Evaluation:** 3-way classification accuracy

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration**, typically ranging from 3 to 20 seconds.
- Each sample contains **three audio files** forming an ABX triplet.
- This is a **triplet-based 3-way classification** task testing speaker discrimination and identification.
- **Key properties of this ABX variant:**
  - A and B are always from **different speakers**
  - X can be from **A's speaker**, **B's speaker**, or a **third different speaker**
  - The task combines **relative similarity judgment** with **speaker identification**
  - The `-1` label adds an **open-set** element to the traditional closed-set ABX task
- **Advantages of this ABX variant:**
  - Tests both **closed-set** discrimination (choosing between A and B) and **open-set** detection (identifying third speaker)
  - More realistic than traditional ABX by including out-of-set speakers
  - Requires models to learn both similarity ranking and threshold-based rejection
  - Provides richer evaluation of speaker embedding quality
  - Combines aspects of verification (threshold decision) and identification (relative comparison)
- **Model requirements:**
  - Must compute speaker embeddings or similarity scores
  - Must make relative comparisons: `sim(A,X)` vs `sim(B,X)`
  - Does not require threshold tuning (unlike verification EER)
- This dataset captures **in-the-wild variability** including:
  - Background noise (music, laughter, ambient sounds)
  - Acoustic conditions (different rooms, microphones, compression)
  - Speaking styles (conversational, interview, debate)
  - Channel effects (YouTube compression, various recording devices)
  - Spontaneous speech characteristics
- Applications include:
  - **Speaker embedding evaluation**: Testing quality of learned representations
  - **Similarity metric learning**: Training and evaluating distance metrics
  - **Few-shot speaker recognition**: Discriminating speakers with minimal examples
  - **Perceptual modeling**: Comparing model decisions to human perception
  - **Robustness testing**: Evaluating discrimination under noisy conditions
- **Evaluation metric**: 3-way classification accuracy (percentage of correct predictions across all three classes)
- The **text-independent** nature means no constraints on spoken content—discrimination must rely on vocal characteristics alone.
- The dataset is particularly challenging due to:
  - **Real-world noise**: Uncontrolled recording environments
  - **Duration mismatch**: The three utterances may have very different lengths
  - **Within-speaker variability**: X may be from a different video/session than the matching anchor
  - **Between-speaker similarity**: Some speaker pairs are acoustically very similar
  - **Channel mismatch**: Different utterances may have different acoustic conditions
- **Triplet structure** enables:
  - **Metric learning**: Training triplet loss or contrastive loss models
  - **Embedding space evaluation**: Testing whether embeddings preserve speaker identity
  - **Relative similarity**: Comparing distances in embedding space
- The `id` field concatenates all three utterance identifiers with `___` separator for easy triplet tracking.
- Speaker IDs are embedded in the file paths (e.g., `id10617`, `id10829`, `id10755`).
- **Relationship to other tasks:**
  - **Verification**: Pairwise same/different decision
  - **Similarity**: Continuous similarity rating
  - **ABX**: Forced-choice relative discrimination (this task)
- ABX is particularly useful for:
  - Evaluating speaker embeddings without threshold tuning
  - Cross-dataset evaluation (more transferable than verification)
  - Human-model comparison studies (ABX is a natural human task)

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
```

## References
- Official website: https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html
- VoxCeleb1 paper: https://arxiv.org/abs/1706.08612
- ABX evaluation: https://docs.cognitive-ml.fr/ABXpy/
