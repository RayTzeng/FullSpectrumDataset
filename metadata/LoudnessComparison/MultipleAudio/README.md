# LoudnessComparison - MultipleAudio

## Overview
**LoudnessComparison-MultipleAudio** is a dataset derived from the **AVID (Audio-Visual Instance Discrimination) corpus** for evaluating audio models' ability to compare loudness across multiple audio files. The dataset contains **60,000 training samples** and **1,000 test samples**, each featuring **2-4 audio files** with different vocal intensity levels from the same or different speakers. Models must compare loudness levels across these files using their actual Sound Pressure Level (SPL) measurements in dB.

The dataset includes two comparison paradigms:
- **Same speaker (66.7% train, 70% test)**: 2-4 recordings from the same speaker saying the same sentence at different intensity levels
- **Cross speaker (33.3% train, 30% test)**: 2-4 recordings from different speakers at different intensity levels, with SPL constraints to ensure distinguishability (≥5 dB separation)

The AVID corpus features:
- **Controlled vocal intensity**: Recordings at soft, normal, loud, and very loud levels
- **Measured SPL**: Actual Sound Pressure Level in dB for each recording
- **High sampling rate**: Original 44.1 kHz audio
- **Natural speech**: Real sentences spoken by multiple speakers

This dataset is unique because it uses **real recordings with calibrated SPL measurements** rather than synthetic gain adjustments, providing an ecologically valid test of loudness perception.

## Supported Tasks
1. **Loudness Comparison Across Files** (Compare loudness of multiple audio files)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 60,000 |
| test | 1,000 |

**Sample Characteristics:**
- Audio files per sample: **2-4 recordings**
- Sampling rate: **44.1 kHz** (original AVID rate)
- Duration range: **~0.5s to 3.5s per audio file**
- SPL range: **~70-100 dB**
- Vocal intensities: **soft, normal, loud, veryloud**

### Sample Type Distribution (Training Set)

| Sample Type | # Samples | Percentage | Description |
|-------------|----------:|-----------:|-------------|
| same_speaker | 40,000 | 66.7% | Same speaker/sentence at different intensities |
| cross_speaker | 20,000 | 33.3% | Different speakers with SPL constraints (≥5 dB) |

### Number of Audio Files (Training Set)

| # Audio Files | # Samples |
|--------------:|----------:|
| 2 | 22,247 |
| 3 | 21,280 |
| 4 | 16,473 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (format: `{speaker_info}_{num_audios}` or `cross_{id}_{num_audios}`) |
| `paths` | List of paths to audio files (2-4 files) |
| `sampling_rates` | List of sampling rates for each audio file (all 44100 Hz) |
| `durations` | List of durations in seconds for each audio file |
| `dataset` | Source dataset (`LoudnessComparison-MultipleAudio`) |
| `SPLs` | List of Sound Pressure Levels in dB for each audio file |
| `vocal_intensities` | List of intensity labels for each audio: `soft`, `normal`, `loud`, or `veryloud` |
| `source_dataset` | Original source dataset (`AVID`) |
| `num_audios` | Number of audio files in the sample (2-4) |
| `group_key` | Speaker/sentence identifier for same-speaker samples |
| `speaker_ids` | List of speaker/sentence IDs for cross-speaker samples |
| `sample_type` | Type of comparison: `same_speaker` or `cross_speaker` |

---

## Example Entries

```json
{"id": "sp6_s2_sen2_4", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp6_s2_sen2_soft.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp6_s2_sen2_normal.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp6_s2_sen2_loud.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp6_s2_sen2_veryloud.wav"], "sampling_rates": [44100, 44100, 44100, 44100], "durations": [0.9008616780045351, 1.012857142857143, 0.9985487528344671, 1.0297505668934241], "dataset": "LoudnessComparison-MultipleAudio", "SPLs": [78.8, 83.3, 87.6, 91.3], "vocal_intensities": ["soft", "normal", "loud", "veryloud"], "source_dataset": "AVID", "num_audios": 4, "group_key": "sp6_s2_sen2", "sample_type": "same_speaker"}

{"id": "sp13_s2_sen23_2", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp13_s2_sen23_soft.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp13_s2_sen23_normal.wav"], "sampling_rates": [44100, 44100], "durations": [1.9460544217687075, 1.9484353741496598], "dataset": "LoudnessComparison-MultipleAudio", "SPLs": [78.2, 80.8], "vocal_intensities": ["soft", "normal"], "source_dataset": "AVID", "num_audios": 2, "group_key": "sp13_s2_sen23", "sample_type": "same_speaker"}

{"id": "cross_013330_2", "paths": ["/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp21_s1_sen22_soft.wav", "/saltpool0/data/tseng/FullSpectrumDataset/corpus/AVID/audio/SENT/sp36_s1_sen5_loud.wav"], "sampling_rates": [44100, 44100], "durations": [2.069954648526077, 1.278344671201814], "dataset": "LoudnessComparison-MultipleAudio", "SPLs": [75.9, 83.1], "vocal_intensities": ["soft", "loud"], "source_dataset": "AVID", "num_audios": 2, "speaker_ids": ["sp21_s1_sen22", "sp36_s1_sen5"], "sample_type": "cross_speaker"}
```

---

## Task Usage

### 1. Loudness Comparison Across Files
- **Target field:** `SPLs`
- **Input:** 2-4 separate audio files
- **Task:** Compare and rank loudness levels across files, or identify loudest/quietest
- **Ground truth:** Measured Sound Pressure Levels in dB

### 2. Vocal Intensity Recognition
- **Target field:** `vocal_intensities`
- **Input:** Audio file(s)
- **Task:** Classify vocal intensity level as soft, normal, loud, or veryloud
- **Ground truth:** Labeled intensity levels from AVID corpus

---

## Label Space

### Vocal Intensity Levels
<details>
<summary>Show 4 intensity levels:</summary>

- **soft**: Quiet speaking voice (~75-80 dB SPL)
- **normal**: Normal conversational level (~80-85 dB SPL)
- **loud**: Raised voice (~85-95 dB SPL)
- **veryloud**: Very loud voice (~90-100 dB SPL)

</details>

### SPL (Sound Pressure Level)
- **Range**: Approximately 70-100 dB
- **Type**: Continuous value measured in decibels
- **Measurement**: Calibrated recordings from AVID corpus
- **Interpretation**: Higher SPL = louder audio

---

## Sample Types

### Same Speaker (66.7% train, 70% test)
- **Description**: Multiple recordings of the same speaker saying the same sentence at different vocal intensities
- **Audio files**: 2-4 intensity variations (soft, normal, loud, veryloud)
- **Purpose**: Test loudness comparison ability without timbral variation
- **Group key**: Identifies the speaker and sentence (e.g., `sp6_s2_sen2`)
- **SPL variation**: Natural variation across intensity levels

### Cross Speaker (33.3% train, 30% test)
- **Description**: Recordings from different speakers at different intensity levels
- **Audio files**: 2-4 recordings from different speakers
- **Purpose**: Test loudness comparison ability with timbral variation
- **Constraint**: Quietest and loudest must be ≥5 dB apart from all others
- **Speaker IDs**: List of speaker/sentence identifiers
- **SPL constraint**: Ensures distinguishability across speakers

---

## Dataset Construction

### Source Data
All audio comes from the **AVID (Audio-Visual Instance Discrimination)** corpus:
- Multiple speakers recorded saying sentences at 4 intensity levels
- Calibrated SPL measurements for each recording
- High-quality studio recordings at 44.1 kHz
- Natural speech with controlled intensity variations

### Same-Speaker Sampling
1. Select a speaker and sentence group
2. Randomly choose 2-4 intensity levels
3. Include corresponding audio files
4. Record SPL values and intensity labels

### Cross-Speaker Sampling
1. Randomly select 2-4 different speaker/sentence combinations
2. Ensure SPL constraint: quietest and loudest must be ≥5 dB from others
3. If constraint not met, resample
4. Include audio files from different speakers
5. Record SPL values and intensity labels

---

## AVID Corpus Background

The **AVID (Audio-Visual Instance Discrimination)** dataset was designed for audio-visual learning research. Key features:
- **Multiple speakers**: Diverse speaker pool
- **Controlled intensities**: 4 calibrated levels (soft, normal, loud, veryloud)
- **Measured SPL**: Actual Sound Pressure Level measurements in dB
- **Natural speech**: Real sentences, not synthesized
- **High quality**: Studio recordings with minimal background noise

This provides an ecologically valid test of loudness perception because:
- SPL values are **real measurements**, not synthetic gain adjustments
- Intensity variations are **naturally produced** by speakers
- **Timbral consistency** (same speaker) and **timbral variation** (cross speaker) are both tested

---

## SPL Constraint (Cross-Speaker)

For cross-speaker samples, the following constraint ensures distinguishability:
- **Quietest audio**: Must be ≥5 dB quieter than all others
- **Loudest audio**: Must be ≥5 dB louder than all others

This guarantees that the extreme values are perceptually distinguishable even across different speakers with different vocal characteristics.

---

## Notes
- All audio files are sampled at **44.1 kHz** (original AVID sampling rate).
- Audio files are **separate** — not concatenated into a single file (unlike SingleAudio).
- The dataset uses **real SPL measurements** from the AVID corpus, not synthetic gain adjustments.
- **SPL (Sound Pressure Level)** is measured in decibels and represents actual acoustic intensity.
- **Vocal intensity labels** are from the original AVID annotations.
- The dataset evaluates:
  - **Cross-file loudness comparison**: Can models compare loudness across separate audio files?
  - **Timbral invariance**: Can models compare loudness despite speaker differences?
  - **Vocal intensity recognition**: Can models classify intensity levels?
  - **Calibrated loudness perception**: Performance on real SPL measurements vs. synthetic gains
- **Same-speaker samples** provide an easier baseline with consistent timbre.
- **Cross-speaker samples** are more challenging due to speaker variability.
- The **5 dB SPL constraint** for cross-speaker samples ensures statistical distinguishability.
- Duration varies naturally across intensity levels (louder speech may have different timing).
- This dataset is **metadata-only** — it references audio files from the AVID corpus rather than generating new audio.
- The dataset is split with different random seeds:
  - **Train**: seed=42, 60,000 samples
  - **Test**: seed=999, 1,000 samples
- The `group_key` field (same-speaker) identifies recordings from the same speaker/sentence combination.
- The `speaker_ids` field (cross-speaker) lists which speakers contributed to each sample.
- This dataset complements **SingleAudio** by:
  - Using real SPL measurements instead of synthetic gains
  - Testing cross-file comparison (separate files vs. concatenated)
  - Focusing on speech-only domain with controlled vocal intensity
  - Providing both within-speaker and across-speaker comparison scenarios
