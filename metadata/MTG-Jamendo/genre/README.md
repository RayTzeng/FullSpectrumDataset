# MTG-Jamendo

## Overview
**MTG-Jamendo** is a large-scale open benchmark for automatic music tagging, built from Jamendo tracks released under Creative Commons licenses and annotated with uploader-provided tags. The dataset contains over **55,000 full-length audio tracks** labeled with **195 tags** spanning genre, instrument, and mood/theme. It is widely used for multi-label music information retrieval research, particularly for music genre classification.

## Supported Tasks
1. **Music Genre Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 117,986 |
| dev | 39,962 |
| test | 41,534 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique track ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `genre` | List of genre labels |

---

## Example Entries

```json
{"id": "track_0429948_30s_seg1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio-30s/48/429948.low_seg1.mp3", "sampling_rate": 16000, "duration": 30.067, "dataset": "MTG-Jamendo", "genre": ["pop", "rock"]}

{"id": "track_1400989", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio/89/1400989.low.mp3", "sampling_rate": 16000, "duration": 404.193, "dataset": "MTG-Jamendo", "genre": ["drumnbass", "electronic"]}

{"id": "track_1148304_60s_seg1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio-60s/04/1148304.low_seg1.mp3", "sampling_rate": 16000, "duration": 60.048, "dataset": "MTG-Jamendo", "genre": ["classical", "newage", "soundtrack"]}
```

---

## Task Usage

### 1. Music Genre Classification
- **Target field:** `genre` (list of genre labels)

---

## Label Space

### Genre Labels
<details>
<summary>Show 87 available genre labels:</summary>

`60s`, `70s`, `80s`, `90s`, `acidjazz`, `alternative`, `alternativerock`, `ambient`, `atmospheric`, `blues`, `bluesrock`, `bossanova`, `breakbeat`, `celtic`, `chanson`, `chillout`, `choir`, `classical`, `classicrock`, `club`, `contemporary`, `country`, `dance`, `darkambient`, `darkwave`, `deephouse`, `disco`, `downtempo`, `drumnbass`, `dub`, `dubstep`, `easylistening`, `edm`, `electronic`, `electronica`, `electropop`, `ethno`, `eurodance`, `experimental`, `folk`, `funk`, `fusion`, `groove`, `grunge`, `hard`, `hardrock`, `hiphop`, `house`, `idm`, `improvisation`, `indie`, `industrial`, `instrumentalpop`, `instrumentalrock`, `jazz`, `jazzfusion`, `latin`, `lounge`, `medieval`, `metal`, `minimal`, `newage`, `newwave`, `orchestral`, `pop`, `popfolk`, `poprock`, `postrock`, `progressive`, `psychedelic`, `punkrock`, `rap`, `reggae`, `rnb`, `rock`, `rocknroll`, `singersongwriter`, `soul`, `soundtrack`, `swing`, `symphonic`, `synthpop`, `techno`, `trance`, `triphop`, `world`, `worldfusion`

</details>

---

## Notes
- All audio files are resampled to **16 kHz**.
- Audio clips have **variable duration**, including:
  - **Full-length tracks**: Original recordings (typically >2 minutes). The tracks longer than 5 minutes are excluded.
  - **30-second segments**: Randomly trimmed segments (1-2 per track)
  - **60-second segments**: Randomly trimmed segments (for tracks > 120 seconds)
- This is a **multi-label** classification task: each track may have multiple genre labels.
- Labels are stored in the `genre` field as a **list of strings**.
- The dataset is built from **Jamendo** tracks released under **Creative Commons licenses**, making it freely available for research.
- Genre labels are provided by **uploaders** (artists and users) on the Jamendo platform.
- The dataset contains **87 genre labels** covering:
  - **Era-based genres**: 60s, 70s, 80s, 90s
  - **Main genres**: rock, pop, jazz, classical, electronic, metal, hiphop, blues, country, folk
  - **Sub-genres**: alternativerock, classicrock, poprock, postrock, drumnbass, deephouse, acidjazz, jazzfusion
  - **Descriptive styles**: ambient, atmospheric, experimental, orchestral, symphonic, minimal
- The full MTG-Jamendo dataset includes additional tags for **instruments** and **mood/theme**, but this task focuses specifically on **genre classification**.
- The dataset is particularly valuable for:
  - **Multi-label music classification**: Training models to recognize multiple genres per track
  - **Music information retrieval**: Developing systems for music search and recommendation
  - **Genre recognition**: Understanding musical styles and characteristics
  - **Transfer learning**: Pre-training models for downstream music understanding tasks
- Created by the **Music Technology Group (MTG)** at Universitat Pompeu Fabra, Barcelona.
