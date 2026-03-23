# TUT2017

## Overview
**TUT2017** (TUT Acoustic Scenes 2017) is a benchmark dataset from the DCASE 2017 Challenge for acoustic scene classification. It contains **10-second audio segments** recorded in **15 everyday environments** such as buses, cafés, offices, parks, and metro stations. The dataset is widely used to study environmental sound understanding and scene recognition in real-world contexts.

## Supported Tasks
1. **Acoustic Scene Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 4,680 |
| test | 1,620 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `acoustic_scene` | Ground-truth acoustic scene label |

---

## Example Entries

```json
{"id": "a098_40_50", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/TUT2017/TUT-acoustic-scenes-2017-development/audio/a098_40_50.wav", "duration": "10.000", "sampling_rate": 44100, "dataset": "TUT2017", "acoustic_scene": "forest_path"}

{"id": "a110_260_270", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/TUT2017/TUT-acoustic-scenes-2017-development/audio/a110_260_270.wav", "duration": "10.000", "sampling_rate": 44100, "dataset": "TUT2017", "acoustic_scene": "grocery_store"}

{"id": "b065_204_214", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/TUT2017/TUT-acoustic-scenes-2017-development/audio/b065_204_214.wav", "duration": "10.000", "sampling_rate": 44100, "dataset": "TUT2017", "acoustic_scene": "train"}
```

---

## Task Usage

### 1. Acoustic Scene Classification
- **Target field:** `acoustic_scene` (acoustic scene label)

---

## Label Space

### Acoustic Scene Labels
<details>
<summary>Show 15 available labels:</summary>

`beach`, `bus`, `cafe/restaurant`, `car`, `city_center`, `forest_path`, `grocery_store`, `home`, `library`, `metro_station`, `office`, `park`, `residential_area`, `train`, `tram`

</details>

### Label Definitions
<details>
<summary>Show detailed descriptions for each acoustic scene:</summary>

- **beach**: Lakeside beach (outdoor)
- **bus**: Traveling by bus in the city (vehicle)
- **cafe/restaurant**: Small cafe/restaurant (indoor)
- **car**: Driving or traveling as a passenger, in the city (vehicle)
- **city_center**: City center (outdoor)
- **forest_path**: Forest path (outdoor)
- **grocery_store**: Medium size grocery store (indoor)
- **home**: Home (indoor)
- **library**: Library (indoor)
- **metro_station**: Metro station (indoor)
- **office**: Multiple persons, typical work day (indoor)
- **park**: Urban park (outdoor)
- **residential_area**: Residential area (outdoor)
- **train**: Train (traveling, vehicle)
- **tram**: Tram (traveling, vehicle)

</details>

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Each clip is exactly **10 seconds** long.
- This is a **single-label** classification task where each recording corresponds to one acoustic scene.
- The 15 scenes can be categorized into:
  - **Indoor scenes** (5): cafe/restaurant, grocery_store, home, library, office
  - **Outdoor scenes** (5): beach, city_center, forest_path, park, residential_area
  - **Vehicle scenes** (5): bus, car, metro_station, train, tram
- The dataset is part of the DCASE (Detection and Classification of Acoustic Scenes and Events) 2017 Challenge.
- There is no `dev` split in the provided manifest.
