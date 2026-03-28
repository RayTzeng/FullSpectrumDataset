# VocalSet

## Overview
**VocalSet** is a large-scale singing voice corpus containing approximately **10.1 hours** of monophonic recordings from **20 professional singers** (11 male, 9 female). The dataset captures a wide range of **standard and extended vocal techniques** performed across vowels, scales, arpeggios, and musical excerpts. Each recording showcases specific vocal production methods used in various singing styles, making it valuable for research on singing technique analysis, singer identification, vocal pedagogy, and singing voice synthesis.

## Supported Tasks
1. **Vocal Technique Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 1,301 |
| test | 441 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique recording ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `vocal_technique` | Ground-truth vocal technique label |

---

## Example Entries

```json
{"id": "f1_long_trill_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/female1/long_tones/trill/f1_long_trill_u.wav", "sampling_rate": 44100, "duration": 17.225, "dataset": "VocalSet", "vocal_technique": "Trill (upper semitone)"}

{"id": "m9_long_trill_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/male9/long_tones/trill/m9_long_trill_u.wav", "sampling_rate": 44100, "duration": 7.045, "dataset": "VocalSet", "vocal_technique": "Trill (upper semitone)"}

{"id": "f1_row_spoken", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/female1/excerpts/spoken/f1_row_spoken.wav", "sampling_rate": 44100, "duration": 15.087, "dataset": "VocalSet", "vocal_technique": "Spoken excerpt"}
```

---

## Task Usage

### 1. Vocal Technique Classification
- **Target field:** `vocal_technique` (singing technique label)

---

## Label Space

### Vocal Techniques
<details>
<summary>Show 10 available vocal techniques:</summary>

**Standard Techniques:**
- `Vibrato` - Regular oscillation in pitch/intensity for expressive effect
- `Straight tone` - Sustained note without vibrato
- `Breathy` - Airflow-rich production with audible breath noise

**Extended Techniques:**
- `Belt` - Powerful chest-voice dominant production
- `Vocal fry` - Low-frequency creaky voice register
- `Inhaled Singing` - Sound production during inhalation
- `Trill (upper semitone)` - Rapid alternation between adjacent pitches
- `Trillo (goat tone)` - Rapid repeated articulation on single pitch
- `Lip Trill` - Lip vibration technique (vocal warm-up/embellishment)

**Spoken:**
- `Spoken excerpt` - Spoken delivery without singing

</details>

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Audio clips have **variable duration**, reflecting natural performance lengths.
- This is a **single-label** classification task where each recording demonstrates one vocal technique.
- The dataset includes **20 professional singers** with diverse training backgrounds (classical, jazz, contemporary).
- Recordings cover multiple vocal exercise types:
  - **Long tones**: Sustained notes demonstrating technique control
  - **Scales and arpeggios**: Melodic patterns across pitch ranges
  - **Musical excerpts**: Performance of standard vocal literature
- All recordings are **monophonic** (solo voice without accompaniment).
- The dataset is particularly valuable for:
  - **Vocal pedagogy research**: Analyzing and teaching singing techniques
  - **Singer identification**: Recognizing individual vocal characteristics
  - **Singing voice synthesis**: Training generative models for expressive singing
  - **Music information retrieval**: Extracting performance attributes from singing
- Technique definitions span both **classical/traditional** methods (vibrato, straight tone) and **extended/contemporary** techniques (vocal fry, inhaled singing, belt).
- There is no `dev` split in the provided manifest.
