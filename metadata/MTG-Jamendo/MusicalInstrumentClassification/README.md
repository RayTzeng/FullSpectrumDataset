# MTG-Jamendo

## Overview
**MTG-Jamendo** is a large-scale open benchmark for automatic music tagging, built from Jamendo tracks released under Creative Commons licenses and annotated with uploader-provided tags. The dataset contains over **55,000 full-length audio tracks** labeled with **195 tags** spanning genre, instrument, and mood/theme. It is widely used for multi-label music information retrieval research, particularly for musical instrument classification.

## Supported Tasks
1. **Musical Instrument Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 52,271 |
| dev | 19,794 |
| test | 18,591 |

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
| `instrument` | List of instrument labels |

---

## Example Entries

```json
{"id": "track_0019200_60s_seg1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio-60s/00/19200.low_seg1.mp3", "sampling_rate": 16000, "duration": 60.056, "dataset": "MTG-Jamendo", "instrument": ["acousticguitar", "drummachine", "electricguitar", "synthesizer"]}

{"id": "track_0944142", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio/42/944142.low.mp3", "sampling_rate": 16000, "duration": 68.65, "dataset": "MTG-Jamendo", "instrument": ["piano"]}

{"id": "track_1135854_30s_seg1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/MTG-Jamendo/audio-30s/54/1135854.low_seg1.mp3", "sampling_rate": 16000, "duration": 30.041, "dataset": "MTG-Jamendo", "instrument": ["computer", "synthesizer"]}
```

---

## Task Usage

### 1. Musical Instrument Classification
- **Target field:** `instrument` (list of instrument labels)

---

## Label Space

### Instrument Labels
<details>
<summary>Show 40 available instrument labels:</summary>

`accordion`, `acousticbassguitar`, `acousticguitar`, `bass`, `beat`, `bell`, `bongo`, `brass`, `cello`, `clarinet`, `classicalguitar`, `computer`, `doublebass`, `drummachine`, `drums`, `electricguitar`, `electricpiano`, `flute`, `guitar`, `harmonica`, `harp`, `horn`, `keyboard`, `oboe`, `orchestra`, `organ`, `pad`, `percussion`, `piano`, `pipeorgan`, `rhodes`, `sampler`, `saxophone`, `strings`, `synthesizer`, `trombone`, `trumpet`, `viola`, `violin`, `voice`

</details>

---

## Notes
- All audio files are resampled to **16 kHz**.
- Audio clips have **variable duration**, including:
  - **Full-length tracks**: Original recordings (typically >2 minutes). The tracks longer than 5 minutes are excluded.
  - **30-second segments**: Randomly trimmed segments (1-2 per track)
  - **60-second segments**: Randomly trimmed segments (for tracks > 120 seconds)
- This is a **multi-label** classification task: each track may have multiple instrument labels.
- Labels are stored in the `instrument` field as a **list of strings**.
- The dataset is built from **Jamendo** tracks released under **Creative Commons licenses**, making it freely available for research.
- Instrument labels are provided by **uploaders** (artists and users) on the Jamendo platform.
- The dataset contains **40 instrument labels** covering:
  - **String instruments**: acousticguitar, classicalguitar, electricguitar, guitar, bass, acousticbassguitar, doublebass, cello, viola, violin, harp
  - **Keyboard instruments**: piano, electricpiano, keyboard, organ, pipeorgan, accordion, rhodes, synthesizer
  - **Percussion**: drums, drummachine, percussion, bongo, beat, bell
  - **Wind instruments**: flute, saxophone, clarinet, oboe, trumpet, trombone, horn, harmonica
  - **Ensembles**: orchestra, brass, strings
  - **Electronic/synthesis**: computer, synthesizer, sampler, pad
  - **Vocal**: voice
- Some labels represent instrument families (e.g., `guitar`) while others are more specific (e.g., `acousticguitar`, `electricguitar`, `classicalguitar`).
- The full MTG-Jamendo dataset includes additional tags for **genre** and **mood/theme**, but this task focuses specifically on **instrument classification**.
- The dataset is particularly valuable for:
  - **Multi-label instrument recognition**: Training models to identify multiple instruments in a track
  - **Music information retrieval**: Developing systems for music search and recommendation
  - **Automatic music transcription**: Understanding instrument composition in music
  - **Music production tools**: Assisting in music analysis and arrangement
- Created by the **Music Technology Group (MTG)** at Universitat Pompeu Fabra, Barcelona.
