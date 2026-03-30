# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, Expresso, and Emilia, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Stress Detection in Speech**, a binary classification task distinguishing between stressful (anxious, scared) and non-stressful emotional states. The dataset is **balanced** with equal numbers of stressful and non-stressful samples.

## Supported Tasks
1. **Stress Detection (Binary Classification)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 12,714 |
| dev | 138 |
| test | 122 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (44100 or 48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `source` | Source corpus (voxceleb, ears, expresso, emilia) |
| `emotions` | List of target emotions found in the audio |
| `stress` | Stress label (stressful or non-stressful) |

---

## Example Entries

```json
{"id": "EN_B00010_S03798", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00010/EN_B00010_S03798/mp3/EN_B00010_S03798_W000153.mp3", "sampling_rate": 44100, "duration": 5.909, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["angry", "scared"], "stress": "stressful"}

{"id": "EN_B00009_S02390", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00009/EN_B00009_S02390/mp3/EN_B00009_S02390_W000000.mp3", "sampling_rate": 44100, "duration": 19.292, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["admiring"], "stress": "non-stressful"}

{"id": "voxceleb2_dev_aac_id08661_ZR6mIEixsP8_00034_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id08661/ZR6mIEixsP8/00034_voicefixer.wav", "sampling_rate": 44100, "duration": 4.8, "dataset": "ParaSpeechCaps", "source": "voxceleb", "emotions": ["anxious"], "stress": "stressful"}
```

---

## Task Usage

### 1. Stress Detection
- **Target field:** `stress` (stressful or non-stressful)

---

## Label Space

### Stress Labels
<details>
<summary>Show 2 available labels:</summary>

`stressful`, `non-stressful`

**Definitions:**
- **stressful** - Speech containing anxious or scared emotions, characterized by heightened physiological arousal
- **non-stressful** - Speech containing other emotional states (admiring, angry, awed, bored, calm, confused, desirous, disgusted, enthusiastic, guilt, happy, pained, saddened, sarcastic, sleepy, sympathetic)

</details>

### Emotion Categories

<details>
<summary>Show emotion-to-stress mapping:</summary>

**Stressful Emotions (2 total)**:
- anxious
- scared

**Non-stressful Emotions (16 total)**:
- admiring
- angry
- awed
- bored
- calm
- confused
- desirous
- disgusted
- enthusiastic
- guilt
- happy
- pained
- saddened
- sarcastic
- sleepy
- sympathetic

**Classification Logic**:
- If `emotions` contains "anxious" OR "scared" → **stressful**
- If `emotions` contains only other target emotions → **non-stressful**
- Entries with multiple emotions where ANY is stressful → **stressful**

</details>

---

## Class Balance

This dataset is **balanced** to ensure equal representation:

- **Before balancing**: Stressful samples are naturally rare (~5-10% of emotional speech)
- **After balancing**: Exactly 50% stressful, 50% non-stressful in each split
- **Balancing method**: Random sampling to match minority class size (stressful)
- **Random seeds**: train=1337, dev=1338, test=1339 (for reproducibility)

The minority class (stressful) determines the final dataset size. For example:
- If train has 6,357 stressful and 100,000 non-stressful → output has 12,714 total (6,357 + 6,357)
- If dev has 69 stressful and 5,000 non-stressful → output has 138 total (69 + 69)

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits with class balancing:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled), then balanced
- **Dev**: From `dev` split, then balanced
- **Test**: From `test` split, then balanced

All splits maintain 50-50 class balance through random undersampling of the majority class.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-20 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional audiobooks (44.1 kHz)
- This is a **binary classification** task where each sample is labeled as either stressful or non-stressful.
- The `emotions` field lists the specific emotions detected in the audio (can be multiple).
- **Multiple emotions**: An entry can have multiple emotions; if ANY is stressful (anxious/scared), the entire entry is classified as stressful.
- **Class balancing** ensures equal training on both classes, preventing bias toward non-stressful majority.
- Only entries with at least one of the 18 target emotions are included (entries without target emotions are filtered out).
- This is particularly valuable for:
  - **Stress detection systems**: Identifying speakers under psychological stress
  - **Mental health monitoring**: Detecting anxiety or fear in speech
  - **Call center analytics**: Identifying stressful customer interactions
  - **Emergency response**: Prioritizing calls based on stress levels
  - **Affective computing**: Understanding emotional states from voice
- Stress detection has applications in healthcare, customer service, security, and human-computer interaction.
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.
- All audio files are verified for existence before inclusion.
- Different runs with the same seed will produce identical balanced datasets (reproducible).

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{paraspeechcaps2024,
  title{ParaSpeechCaps: A Large-Scale Corpus for Paralinguistic Speech Understanding},
  author={[Authors TBD]},
  booktitle={Proceedings of [Conference]},
  year={2024}
}
```

## References
- HuggingFace dataset: https://huggingface.co/datasets/ajd12342/paraspeechcaps
- 59 paralinguistic style tags covering diverse speaking characteristics
- Human-annotated (PSC-Base: 342 hours) and automatically annotated (PSC-Scaled: 2,427 hours) subsets
