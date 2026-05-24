# GiantStepKeys

## Overview
**GiantStepKeys** is a music key detection dataset derived from the GiantSteps collection of electronic dance music (EDM) tracks. The dataset contains **7,417 training samples** and **3,010 test samples**, featuring **1,486 full tracks (train)** and **604 full tracks (test)** from 16 EDM genres, augmented with **30-second segments** to provide more training examples. Each track is annotated with its musical key (major/minor) and genre.

The dataset includes:
- **Full tracks**: Complete music tracks (43-120 seconds, mean ~120s)
- **30-second segments**: Non-overlapping 30-second crops from full tracks
- **24 musical keys**: 12 major and 12 minor keys, plus "Unknown" label
- **16 EDM genres**: tech house, trance, progressive house, techno, dubstep, etc.

All audio is in **MP3 format** at **44.1 kHz** sampling rate. This benchmark is particularly useful for evaluating music information retrieval (MIR) models' understanding of tonality, harmonic structure, and key detection in electronic dance music.

## Supported Tasks
1. **Musical Key Detection**
2. **Genre Classification** (secondary task)

---

## Dataset Statistics

| Split | # Samples | # Full Tracks | # Segments |
|-------|----------:|--------------:|-----------:|
| train | 7,417 | 1,486 | 5,931 |
| test | 3,010 | 604 | 2,406 |

**Sample Characteristics:**
- Full track duration: **43-120 seconds** (mean ~120s)
- Segment duration: **30 seconds** (fixed)
- Sampling rate: **44.1 kHz**
- Format: **MP3** (LOFI quality)
- Musical keys: **24 keys** (12 major + 12 minor) + Unknown

### Key Distribution (Training Set, Simple Keys Only)

**Major Keys (14 unique):**

| Key | # Samples |
|-----|----------:|
| D major | 235 |
| C# major | 220 |
| G# major | 215 |
| G major | 195 |
| A# major | 195 |
| F# major | 170 |
| F major | 160 |
| E major | 160 |
| D# major | 155 |
| C major | 150 |
| B major | 140 |
| C# major (with space) | 120 |
| A major | 105 |
| B major (with space) | 75 |

**Minor Keys (13 unique):**

| Key | # Samples |
|-----|----------:|
| C minor | 633 |
| F minor | 610 |
| E minor | 470 |
| D minor | 430 |
| C# minor | 423 |
| G minor | 370 |
| A minor | 367 |
| B minor | 315 |
| D# minor | 262 |
| F# minor | 250 |
| G# minor | 245 |
| A# minor | 220 |
| E minor (variant) | 50 |

**Other:**
- **Unknown**: 360 samples
- **Compound keys** (e.g., "C major,C minor"): 313 samples

**Note**: The dataset includes some compound/ambiguous key labels (e.g., "A minor,D major") which represent tracks with key changes or ambiguous tonality. Simple single-key labels account for ~96% of the training data.

### Genre Distribution (Training Set)

| Genre | # Samples |
|-------|----------:|
| breaks | 470 |
| chill out | 455 |
| deep house | 415 |
| drum & bass | 465 |
| dubstep | 469 |
| electro house | 469 |
| electronica | 463 |
| hard dance | 470 |
| hip-hop | 459 |
| house | 465 |
| minimal | 467 |
| progressive house | 470 |
| psy-trance | 470 |
| tech house | 470 |
| techno | 470 |
| trance | 470 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (e.g., `2707024_full` for full track, `2707024_0_30` for segment) |
| `path` | Path to audio file (MP3) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`GS` for GiantSteps) |
| `sampling_rate` | Audio sampling rate (44100 Hz) |
| `key` | Musical key label (e.g., `D# minor`, `C major`, `Unknown`) |
| `genre` | EDM genre label |
| `start` | Start time in seconds (for segments and full tracks) |
| `end` | End time in seconds (for segments and full tracks) |

---

## Example Entries

### Full Track
```json
{"id": "2707024_full", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GiantStepKeys/2707024.LOFI.mp3", "duration": 120.058776, "dataset": "GS", "sampling_rate": 44100, "key": "D# minor", "genre": "drum & bass", "start": 0, "end": 120.058776}
```

### 30-Second Segment (0-30s)
```json
{"id": "2707024_0_30", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GiantStepKeys/segments/2707024_0_30.mp3", "duration": 30.014694, "dataset": "GS", "sampling_rate": 44100, "key": "D# minor", "genre": "drum & bass", "start": 0, "end": 30}
```

### 30-Second Segment (30-60s)
```json
{"id": "2707024_30_60", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/GiantStepKeys/segments/2707024_30_60.mp3", "duration": 30.014694, "dataset": "GS", "sampling_rate": 44100, "key": "D# minor", "genre": "drum & bass", "start": 30, "end": 60}
```

---

## Task Usage

### 1. Musical Key Detection
- **Target field:** `key`
- **Task:** Predict the musical key of the audio (24-class classification + Unknown)
- **Label space:** 12 major keys, 12 minor keys, Unknown, plus compound keys
- **Evaluation**: Classification accuracy, precision, recall, F1 score

### 2. Genre Classification
- **Target field:** `genre`
- **Task:** Predict the EDM genre of the audio (16-class classification)
- **Label space:** 16 EDM genres
- **Evaluation**: Classification accuracy, precision, recall, F1 score

---

## Label Space

### Musical Keys
<details>
<summary>Show 24 primary musical keys:</summary>

**Major Keys (12):**
- C major, C# major, D major, D# major
- E major, F major, F# major, G major
- G# major, A major, A# major, B major

**Minor Keys (12):**
- C minor, C# minor, D minor, D# minor
- E minor, F minor, F# minor, G minor
- G# minor, A minor, A# minor, B minor

**Special Labels:**
- Unknown

**Note:** Some tracks have compound key labels indicating key changes or ambiguity (e.g., "C major,C minor", "A minor,D major").

</details>

### Genres
<details>
<summary>Show 16 EDM genres:</summary>

- **breaks**: Breakbeat music
- **chill out**: Downtempo/ambient electronic
- **deep house**: Deep house music
- **drum & bass**: Drum and bass / jungle
- **dubstep**: Dubstep music
- **electro house**: Electro house music
- **electronica**: General electronic music
- **hard dance**: Hard dance / hardcore
- **hip-hop**: Electronic hip-hop
- **house**: House music
- **minimal**: Minimal techno/house
- **progressive house**: Progressive house music
- **psy-trance**: Psychedelic trance
- **tech house**: Tech house music
- **techno**: Techno music
- **trance**: Trance music

</details>

---

## Dataset Augmentation

The dataset is augmented from the original GiantSteps corpus through the following process:

### Original Dataset
- **Train**: 1,486 full tracks
- **Test**: 604 full tracks

### Augmentation Process
1. **Full track entry**: Create an entry for the complete track with ID suffix `_full`
2. **30-second segments**: Crop each track into non-overlapping 30-second segments
   - Segment naming: `{track_id}_{start}_{end}.mp3`
   - Example: `2707024_0_30.mp3`, `2707024_30_60.mp3`, etc.
   - Each 120-second track yields ~4 segments
3. **Audio cropping**: Use FFmpeg to extract segments with codec copy (no re-encoding)
4. **Metadata**: Each segment inherits the key and genre labels from the parent track

### Augmented Dataset
- **Train**: 7,417 samples (1,486 full + 5,931 segments)
- **Test**: 3,010 samples (604 full + 2,406 segments)

### File Organization
```
corpus/GiantStepKeys/
├── {track_id}.LOFI.mp3         # Full tracks
└── segments/
    ├── {track_id}_0_30.mp3     # 30-second segments
    ├── {track_id}_30_60.mp3
    ├── {track_id}_60_90.mp3
    └── {track_id}_90_120.mp3
```

---

## Musical Key Annotation

The musical key annotations in GiantSteps follow standard Western music theory:

### Key Notation
- **Format**: `{Root Note} {Mode}`
- **Root Notes**: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
- **Modes**: major, minor
- **Examples**: `C major`, `A minor`, `F# major`, `D# minor`

### Compound Keys
Some tracks have compound key labels indicating:
- **Key changes**: Track modulates between multiple keys (e.g., "C major,G major")
- **Ambiguous tonality**: Track has ambiguous or multiple tonal centers (e.g., "A minor,C major")
- **Relative keys**: Track alternates between relative major/minor (e.g., "C major,A minor")

These compound labels account for ~4% of the dataset.

---

## Musical Context

### Key Detection in EDM
Key detection is a fundamental MIR task with applications in:
- **Harmonic mixing**: DJs use key information for seamless transitions
- **Music recommendation**: Similar keys suggest harmonic compatibility
- **Music analysis**: Understanding tonal structure and composition
- **Automated DJ systems**: Key-aware playlist generation

### EDM Key Characteristics
Electronic dance music presents unique challenges for key detection:
- **Heavy use of synthesizers**: Non-traditional harmonic content
- **Percussive elements**: Drums and rhythm may dominate the mix
- **Effects and processing**: Distortion, filtering, and modulation
- **Minimal harmonic content**: Some tracks focus on rhythm over melody
- **Key changes**: Progressive tracks may modulate through multiple keys

---

## Source Dataset

### GiantSteps
- **Source**: GiantSteps Key Dataset
- **Type**: Electronic dance music key annotations
- **Content**: DJ-friendly EDM tracks with expert key annotations
- **Sampling rate**: 44.1 kHz
- **Format**: MP3 (LOFI quality for distribution)
- **Annotation method**: Expert manual annotation with key detection algorithms

---

## Generation Scripts

### Prepare Original Manifests
```bash
cd /home/tseng/FullSpectrumDataset/metadata/GiantStepKeys
python3 prepare_gs_manifests.py
```

This creates:
- `train.original.jsonl.gz` (1,486 full tracks)
- `test.original.jsonl.gz` (604 full tracks)

### Augment with Segments
```bash
python3 augment_gs_segments.py train.original.jsonl.gz test.original.jsonl.gz
```

This creates:
- `train.jsonl.gz` (7,417 samples: 1,486 full + 5,931 segments)
- `test.jsonl.gz` (3,010 samples: 604 full + 2,406 segments)
- Audio segments in `corpus/GiantStepKeys/segments/`

### Script Features
- **FFmpeg-based cropping**: Fast segment extraction with codec copy (no re-encoding)
- **Duration probing**: Accurate duration calculation with ffprobe
- **Incremental processing**: Skip existing segments (use `--overwrite-audio` to force)
- **Smoke testing**: Use `--limit N` to process only first N tracks

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Audio format is **MP3** (LOFI quality for efficient distribution).
- Full tracks have **variable duration** (43-120 seconds, mean ~120s).
- Segments are **exactly 30 seconds** (±40ms due to MP3 frame boundaries).
- The dataset is **augmented** from the original GiantSteps corpus.
- **Musical key labels** follow standard Western music theory notation.
- Some tracks have **compound key labels** indicating key changes or ambiguity (~4%).
- The "**Unknown**" label is used for tracks with unclear or no discernible key (360 samples).
- The dataset focuses on **electronic dance music** (EDM) genres.
- **Genre distribution** is approximately balanced across 16 EDM categories.
- The dataset evaluates:
  - **Key detection accuracy**: Can models identify the musical key?
  - **Cross-genre robustness**: Performance across different EDM genres
  - **Segment vs. full track**: Performance on 30s segments vs. full tracks
  - **Harmonic understanding**: Recognition of tonal centers in electronic music
- **Train/test split**:
  - Train: 1,486 original tracks → 7,417 samples (augmented)
  - Test: 604 original tracks → 3,010 samples (augmented)
  - No track overlap between train and test
- **Segment labeling**: All segments from a track inherit the track's key label (assumes key stability within track).
- **Applications** include:
  - DJ software for harmonic mixing
  - Music recommendation systems
  - Automatic playlist generation
  - Music theory analysis
  - Tonal analysis of electronic music
- The dataset complements other key detection datasets by:
  - Focusing on EDM rather than classical or pop music
  - Providing both full tracks and segments
  - Including genre information for multi-task learning
  - Covering modern electronic music production techniques

---

## Dependencies

Dataset preparation requires:
- **Python 3.6+**
- **ffmpeg**: For audio cropping
- **ffprobe**: For duration measurement
- **tqdm**: Progress bars (optional)

Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

Install Python dependencies:
```bash
pip install tqdm
```

---

## Citation

If using this dataset, please cite the original GiantSteps work:

```bibtex
@inproceedings{knees2015giantsteps,
  title={Two data sets for tempo estimation and key detection in electronic dance music annotated from user corrections},
  author={Knees, Peter and Faraldo, {\'A}ngel and Herrera, Perfecto and Vogl, Richard and B{\"o}ck, Sebastian and H{\"o}rschl{\"a}ger, Florian and Le Goff, Mickael},
  booktitle={Proceedings of the 16th International Society for Music Information Retrieval Conference (ISMIR)},
  pages={364--370},
  year={2015}
}
```

---

## References

- **GiantSteps Project**: https://github.com/GiantSteps/giantsteps-key-dataset
- **Dataset Paper**: Knees et al., ISMIR 2015
- **Musical Key Theory**: https://en.wikipedia.org/wiki/Key_(music)
- **Harmonic Mixing**: https://en.wikipedia.org/wiki/Harmonic_mixing
