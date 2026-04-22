# VoxCeleb1 - Speaker Verification

## Overview
**VoxCeleb1** is a large-scale text-independent speaker recognition corpus collected automatically from YouTube interview videos, with speech recorded under realistic in-the-wild conditions such as background noise, overlapping speech, and channel variation. It contains over **100,000 utterances** from **1,251 celebrities**, and is widely used for speaker identification and speaker verification research.

This **verification** subset contains **pairwise speaker comparisons** for binary speaker verification tasks, where the goal is to determine whether two utterances are spoken by the same speaker or different speakers. Audio is recorded at **16 kHz** and pairs include both same-speaker (positive) and different-speaker (negative) examples in a balanced configuration.

## Supported Tasks
1. **Speaker Verification**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 300,000 |
| test | 37,611 |

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
| `label` | Binary verification label: `0` (different speakers) or `1` (same speaker) |

---

## Example Entries

```json
{"id": "id10372_9cHYiZfF3rs_00002___id10316_rCYnEz7eZWo_00002", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10372/9cHYiZfF3rs/00002.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10316/rCYnEz7eZWo/00002.wav"], "sampling_rates": [16000, 16000], "durations": [7.6, 7.64], "dataset": "VoxCeleb1", "label": 0}

{"id": "id10591_oai4Kpbc1n4_00002___id10591_5wZiZlZQYjE_00010", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10591/oai4Kpbc1n4/00002.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/dev/wav/id10591/5wZiZlZQYjE/00010.wav"], "sampling_rates": [16000, 16000], "durations": [4.24, 14.8], "dataset": "VoxCeleb1", "label": 1}

{"id": "id10270_5r0dWxy17C8_00001___id10270_5r0dWxy17C8_00022", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/test/wav/id10270/5r0dWxy17C8/00001.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VoxCeleb1/test/wav/id10270/5r0dWxy17C8/00022.wav"], "sampling_rates": [16000, 16000], "durations": [8.36, 7.0], "dataset": "VoxCeleb1", "label": 1}
```

---

## Task Usage

### 1. Speaker Verification
- **Input:** Two audio utterances (`paths[0]` and `paths[1]`)
- **Target field:** `label` (binary classification)
- **Task:** Predict whether the two utterances are from the same speaker

---

## Label Space

### Verification Labels
<details>
<summary>Show 2 available labels:</summary>

`0` - Different speakers (negative pair)
`1` - Same speaker (positive pair)

</details>

### Label Distribution (Training Set)
- **Different speakers (`0`)**: 150,000 samples (50.0%)
- **Same speaker (`1`)**: 150,000 samples (50.0%)

The dataset is **perfectly balanced** between positive and negative pairs.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration**, typically ranging from 3 to 20 seconds.
- Each sample contains **two audio files** forming a verification pair.
- This is a **pairwise binary classification** task where the model must determine speaker identity match.
- The dataset uses the standard **VoxCeleb1 verification protocol**:
  - **Train split**: Contains pairs from the development (dev) set speakers
  - **Test split**: Uses the official VoxCeleb1 test set (speaker-disjoint from training)
- Speaker IDs are embedded in the file paths (e.g., `id10270`, `id10591`).
- The training set is **balanced** with equal numbers of same-speaker and different-speaker pairs.
- **Evaluation metric**: Equal Error Rate (EER) is the standard metric for this task, along with minimum Detection Cost Function (minDCF).
- This dataset captures **in-the-wild variability** including:
  - Background noise (music, laughter, ambient sounds)
  - Acoustic conditions (different rooms, microphones, compression)
  - Speaking styles (conversational, interview, debate)
  - Channel effects (YouTube compression, various recording devices)
  - Spontaneous speech characteristics
- Applications include:
  - **Biometric authentication**: Voice-based identity verification
  - **Forensic speaker comparison**: Legal and investigative use cases
  - **Voice anti-spoofing**: Distinguishing genuine speakers from impostors
  - **Speaker embedding learning**: Training deep speaker representations
  - **Cross-channel verification**: Robust matching across different recording conditions
- The **text-independent** nature means no constraints on spoken content—verification must rely on vocal characteristics alone.
- The dataset is particularly challenging due to:
  - **Real-world noise**: Uncontrolled recording environments
  - **Short utterances**: Some clips are only a few seconds long
  - **Within-speaker variability**: Same speakers recorded across different videos and time periods
  - **Between-speaker similarity**: Some speakers may sound acoustically similar
- The `id` field concatenates both utterance identifiers with `___` separator for easy pair tracking.

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
- Paper: https://arxiv.org/abs/1706.08612
- VoxCeleb1 test protocol: http://www.robots.ox.ac.uk/~vgg/data/voxceleb/meta/veri_test2.txt
