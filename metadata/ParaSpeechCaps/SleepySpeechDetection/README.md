# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, Expresso, and Emilia, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Sleepy Speech Detection**, a binary classification task distinguishing between sleepy and awake emotional states. The dataset is **balanced** with equal numbers of sleepy and awake samples.

## Supported Tasks
1. **Sleepy Speech Detection**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 7,860 |
| dev | 84 |
| test | 50 |

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
| `sleepiness` | Sleepiness label (sleepy or awake) |

---

## Example Entries

```json
{"id": "EN_B00014_S03174", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00014/EN_B00014_S03174/mp3/EN_B00014_S03174_W000069.mp3", "sampling_rate": 44100, "duration": 3.362, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["bored"], "sleepiness": "awake"}

{"id": "EN_B00019_S07689", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00019/EN_B00019_S07689/mp3/EN_B00019_S07689_W000061.mp3", "sampling_rate": 44100, "duration": 16.146, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["enthusiastic", "happy"], "sleepiness": "awake"}

{"id": "EN_B00025_S09123", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EN/EN_B00025/EN_B00025_S09123/mp3/EN_B00025_S09123_W000045.mp3", "sampling_rate": 44100, "duration": 8.521, "dataset": "ParaSpeechCaps", "source": "emilia", "emotions": ["sleepy"], "sleepiness": "sleepy"}
```

---

## Task Usage

### 1. Sleepy Speech Detection
- **Target field:** `sleepiness` (sleepy or awake)

---

## Label Space

### Sleepiness Labels
<details>
<summary>Show 2 available labels:</summary>

`sleepy`, `awake`

**Definitions:**
- **sleepy** - Speech containing the "sleepy" emotion, characterized by reduced energy, slower articulation, and monotone delivery
- **awake** - Speech containing other emotional states (admiring, angry, anxious, awed, bored, calm, confused, desirous, disgusted, enthusiastic, guilt, happy, pained, saddened, sarcastic, scared, sympathetic)

</details>

### Emotion Categories

<details>
<summary>Show emotion-to-sleepiness mapping:</summary>

**Sleepy Emotions (1 total)**:
- sleepy

**Awake Emotions (17 total)**:
- admiring
- angry
- anxious
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
- scared
- sympathetic

**Classification Logic**:
- If `emotions` contains "sleepy" → **sleepy**
- If `emotions` contains only other target emotions → **awake**
- Entries with multiple emotions where ANY is "sleepy" → **sleepy**

</details>

---

## Class Balance

This dataset is **balanced** to ensure equal representation:

- **Before balancing**: Sleepy samples are very rare (~1-3% of emotional speech)
- **After balancing**: Exactly 50% sleepy, 50% awake in each split
- **Balancing method**: Random sampling to match minority class size (sleepy)
- **Random seeds**: train=2024, dev=2025, test=2026 (for reproducibility)

The minority class (sleepy) determines the final dataset size. For example:
- If train has 3,930 sleepy and 100,000 awake → output has 7,860 total (3,930 + 3,930)
- If dev has 42 sleepy and 5,000 awake → output has 84 total (42 + 42)

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
- This is a **binary classification** task where each sample is labeled as either sleepy or awake.
- The `emotions` field lists the specific emotions detected in the audio (can be multiple).
- This is particularly valuable for:
  - **Drowsiness detection**: Identifying tired drivers or operators
  - **Sleep disorder monitoring**: Detecting sleepiness patterns in clinical settings
  - **Workplace safety**: Monitoring alertness in safety-critical jobs
  - **Health monitoring**: Tracking fatigue levels through voice
  - **Student attention**: Detecting engagement in educational settings
- Sleepy speech characteristics include:
  - **Reduced energy**: Lower overall amplitude
  - **Slower articulation**: Decreased speaking rate
  - **Monotone delivery**: Reduced pitch variation
  - **Imprecise articulation**: Less distinct phoneme boundaries
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.
