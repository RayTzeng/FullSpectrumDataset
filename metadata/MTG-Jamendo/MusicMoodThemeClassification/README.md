# MTG-Jamendo

## Overview
**MTG-Jamendo** is a large-scale open benchmark for automatic music tagging, built from Jamendo tracks released under Creative Commons licenses and annotated with uploader-provided tags. The dataset contains over **55,000 full-length audio tracks** labeled with **195 tags** spanning genre, instrument, and mood/theme. It is widely used for multi-label music information retrieval research, particularly for music mood and theme classification.

## Supported Tasks
1. **Music Mood/Theme Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 35,599 |
| dev | 13,563 |
| test | 15,355 |

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
| `moodtheme` | List of mood/theme labels |

---

## Example Entries

```json
{"id": "track_1294803", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio/03/1294803.low.mp3", "sampling_rate": 16000, "duration": 245.394, "dataset": "MTG-Jamendo", "moodtheme": ["melodic"]}

{"id": "track_1356133", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio/33/1356133.low.mp3", "sampling_rate": 16000, "duration": 171.233, "dataset": "MTG-Jamendo", "moodtheme": ["action", "sport"]}

{"id": "track_1359344_30s_seg2", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio-30s/44/1359344.low_seg2.mp3", "sampling_rate": 16000, "duration": 30.067, "dataset": "MTG-Jamendo", "moodtheme": ["powerful"]}
```

---

## Task Usage

### 1. Music Mood/Theme Classification
- **Target field:** `moodtheme` (list of mood/theme labels)

---

## Label Space

### Mood/Theme Labels
<details>
<summary>Show 56 available mood/theme labels:</summary>

`action`, `adventure`, `advertising`, `background`, `ballad`, `calm`, `children`, `christmas`, `commercial`, `cool`, `corporate`, `dark`, `deep`, `documentary`, `drama`, `dramatic`, `dream`, `emotional`, `energetic`, `epic`, `fast`, `film`, `fun`, `funny`, `game`, `groovy`, `happy`, `heavy`, `holiday`, `hopeful`, `inspiring`, `love`, `meditative`, `melancholic`, `melodic`, `motivational`, `movie`, `nature`, `party`, `positive`, `powerful`, `relaxing`, `retro`, `romantic`, `sad`, `sexy`, `slow`, `soft`, `soundscape`, `space`, `sport`, `summer`, `trailer`, `travel`, `upbeat`, `uplifting`

</details>

---

## Notes
- All audio files are resampled to **16 kHz**.
- Audio clips have **variable duration**, including:
  - **Full-length tracks**: Original recordings (typically >2 minutes). The tracks longer than 5 minutes are excluded.
  - **30-second segments**: Randomly trimmed segments (1-2 per track)
  - **60-second segments**: Randomly trimmed segments (for tracks > 120 seconds)
- This is a **multi-label** classification task: each track may have multiple mood/theme labels.
- Labels are stored in the `moodtheme` field as a **list of strings**.
- The dataset is built from **Jamendo** tracks released under **Creative Commons licenses**, making it freely available for research.
- Mood/theme labels are provided by **uploaders** (artists and users) on the Jamendo platform.
- The dataset contains **56 mood/theme labels** covering:
  - **Emotional moods**: happy, sad, melancholic, emotional, romantic, love, angry, calm, relaxing, meditative
  - **Energy levels**: energetic, powerful, upbeat, uplifting, motivational, inspiring, groovy, fast, slow, soft
  - **Atmosphere**: dark, deep, dramatic, epic, dream, space, nature, atmospheric
  - **Usage contexts**: advertising, commercial, corporate, background, film, movie, documentary, trailer, game, sport
  - **Occasions**: party, holiday, christmas, summer, travel, children
  - **Characteristics**: melodic, retro, cool, fun, funny, sexy, heavy, hopeful, positive, action, adventure
- Mood/theme tags describe the **emotional quality**, **atmosphere**, or **intended use case** of the music, making them valuable for:
  - **Music recommendation**: Suggesting tracks based on mood or context
  - **Content creation**: Finding suitable music for videos, games, or advertisements
  - **Emotional analysis**: Understanding the affective content of music
  - **Context-aware music retrieval**: Matching music to specific scenarios or activities
- The full MTG-Jamendo dataset includes additional tags for **genre** and **instruments**, but this task focuses specifically on **mood/theme classification**.
- The dataset is particularly valuable for:
  - **Multi-label mood classification**: Training models to identify multiple moods in a track
  - **Music information retrieval**: Developing systems for mood-based music search
  - **Affective computing**: Understanding emotional content in music
  - **Music production and licensing**: Categorizing music for commercial and creative applications
- Created by the **Music Technology Group (MTG)** at Universitat Pompeu Fabra, Barcelona.
