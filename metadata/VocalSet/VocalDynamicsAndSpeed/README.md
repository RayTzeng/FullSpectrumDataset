# VocalSet

## Overview
**VocalSet** is a large-scale singing voice corpus containing approximately **10.1 hours** of monophonic recordings from **20 professional singers** (11 male, 9 female). This task focuses on **vocal dynamics classification**, where the goal is to identify the volume level and intensity of vocal production. The dataset includes recordings performed at various dynamic levels from very soft (pianissimo) to very loud (forte), along with articulation speed information.

## Supported Tasks
1. **Vocal Dynamics Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 1,668 |
| test | 564 |

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
| `vocal_dynamic_type` | Ground-truth vocal dynamic label |
| `articulation_speed` | Articulation speed annotation (slow/medium/fast) |

---

## Example Entries

```json
{"id": "m11_scales_c_slow_piano_e", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/male11/scales/slow_piano/m11_scales_c_slow_piano_e.wav", "sampling_rate": 44100, "duration": 9.66, "dataset": "VocalSet", "vocal_dynamic_type": "piano (soft)", "articulation_speed": "slow (legato)"}

{"id": "f3_arpeggios_f_fast_forte_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/female3/arpeggios/fast_forte/f3_arpeggios_f_fast_forte_u.wav", "sampling_rate": 44100, "duration": 2.605, "dataset": "VocalSet", "vocal_dynamic_type": "forte (loud)", "articulation_speed": "fast (articulated)"}

{"id": "m1_long_pp_u", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/VocalSet/FULL/male1/long_tones/pp/m1_long_pp_u.wav", "sampling_rate": 44100, "duration": 9.617, "dataset": "VocalSet", "vocal_dynamic_type": "pianissimo (very soft)", "articulation_speed": "medium (tenuto)"}
```

---

## Task Usage

### 1. Vocal Dynamics Classification
- **Target field:** `vocal_dynamic_type` (vocal volume/intensity level)

---

## Label Space

### Vocal Dynamics
<details>
<summary>Show 5 available vocal dynamic levels:</summary>

**Intensity Levels (softest to loudest):**
- `pianissimo (very soft)` - Very quiet singing with minimal vocal intensity
- `piano (soft)` - Soft singing with gentle vocal production
- `mezzo forte (medium)` - Medium volume with moderate intensity
- `forte (loud)` - Loud singing with strong vocal projection
- `messa di voce` - Dynamic control exercise (crescendo-decrescendo on single note)

</details>

### Articulation Speed
<details>
<summary>Additional annotation dimension:</summary>

The dataset also includes `articulation_speed` annotations:
- `slow (legato)` - Smooth, connected notes with gradual transitions
- `medium (tenuto)` - Sustained notes with full duration
- `fast (articulated)` - Quick, clearly separated notes with distinct attacks

</details>

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Audio clips have **variable duration**, reflecting natural performance lengths.
- This is a **single-label** classification task where each recording represents one dynamic level.
- The dataset includes **20 professional singers** (15 in training, 5 in test split).
- Recordings cover multiple vocal exercise types:
  - **Scales**: Ascending/descending melodic patterns
  - **Arpeggios**: Broken chord patterns
  - **Long tones**: Sustained single-note exercises
- **Messa di voce** is a classical vocal technique involving a smooth crescendo followed by diminuendo on a single sustained note, demonstrating dynamic control.
- The `articulation_speed` field provides additional context about tempo and articulation style, which can influence dynamic perception.
- Dynamic markings follow standard musical notation conventions:
  - **pp** (pianissimo) = very soft
  - **p** (piano) = soft
  - **mf** (mezzo forte) = medium loud
  - **f** (forte) = loud
- All recordings are **monophonic** (solo voice without accompaniment).
- There is no `dev` split in the provided manifest.
