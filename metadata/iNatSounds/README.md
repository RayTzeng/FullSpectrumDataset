# iNatSounds

## Overview
**iNatSounds** (iNaturalist Sounds Dataset) is a large-scale collection of **230,000 audio files** capturing sounds from over **5,500 species**, contributed by more than **27,000 recordists** worldwide. The dataset encompasses sounds from birds, mammals, insects, reptiles, and amphibians, with audio and species labels derived from observations submitted to **iNaturalist**, a global citizen science platform. This diverse dataset enables research in biodiversity monitoring, species classification, and bioacoustic analysis.

## Supported Tasks
1. **Species Supercategory Classification**
2. **Species Name Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 135,975 |
| test | 49,338 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique observation ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `supercategory` | Taxonomic supercategory label |
| `common_name` | Common name of the species |
| `scientific_name` | Scientific name of the species |
| `short_name` | Shortened common name |

---

## Example Entries

```json
{"id": 80371, "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/iNatSounds/train/02461_Animalia_Chordata_Aves_Passeriformes_Cardinalidae_Piranga_ludoviciana/fbb39356-089a-4b86-9fc3-bec6591cab5d.wav", "sampling_rate": 22050, "duration": 14.931, "dataset": "iNatSounds", "supercategory": "Aves(birds)", "common_name": "Western Tanager", "scientific_name": "Piranga ludoviciana", "short_name": "tanager"}

{"id": 121770, "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/iNatSounds/train/03289_Animalia_Chordata_Aves_Passeriformes_Muscicapidae_Copsychus_saularis/f13ef314-9939-4480-8966-e1274295d4fa.wav", "sampling_rate": 22050, "duration": 29.28, "dataset": "iNatSounds", "supercategory": "Aves(birds)", "common_name": "Oriental Magpie-Robin", "scientific_name": "Copsychus saularis", "short_name": "magpie-robin"}

{"id": 58000, "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/iNatSounds/train/01986_Animalia_Chordata_Aves_Coraciiformes_Alcedinidae_Todiramphus_sanctus/7ec08729-73b0-4fbf-9c77-10dd198cb505.wav", "sampling_rate": 22050, "duration": 19.18, "dataset": "iNatSounds", "supercategory": "Aves(birds)", "common_name": "Sacred Kingfisher", "scientific_name": "Todiramphus sanctus", "short_name": "kingfisher"}
```

---

## Task Usage

### 1. Species Supercategory Classification
- **Target field:** `supercategory` (taxonomic supercategory)

### 2. Species Name Classification
- **Target field:** `common_name` (species common name)
- **Additional metadata:** `scientific_name` and `short_name` are also provided and can be used for alternative taxonomic identification

---

## Label Space

### Supercategories
<details>
<summary>Show 5 available supercategories:</summary>

`Amphibia`, `Aves(birds)`, `Insect`, `Mammal`, `Reptile`

</details>

### Common Names
<details>
<summary>Show species diversity:</summary>

The dataset contains **5,272 unique species** identified by their common names. The full list of species is available in the file:
- [common_name_stats.csv](common_name_stats.csv)

The species span diverse taxonomic groups including:
- **Birds** (Aves): Various songbirds, raptors, waterfowl, and other avian species
- **Mammals**: Primates, rodents, ungulates, carnivores, and more
- **Insects**: Crickets, cicadas, grasshoppers, beetles, and other invertebrates
- **Amphibians**: Frogs, toads, salamanders
- **Reptiles**: Lizards, snakes, crocodilians

</details>

---

## Notes
- All audio files are sampled at **22.05 kHz**.
- Audio clips have **variable duration**, reflecting natural observation conditions.
- This is a **single-label** classification task where each recording corresponds to one species.
- The dataset includes both **common names** and **scientific names** for species identification, supporting multiple taxonomic classification approaches.
- Audio quality and recording conditions vary as the dataset is crowdsourced from citizen scientists worldwide.
- The `short_name` field is derived from the last word of the `common_name` (e.g., "White-throated Sparrow" → "sparrow"), useful for grouping related species.
- The dataset is particularly valuable for:
  - **Biodiversity monitoring**: Tracking species presence and distribution
  - **Bioacoustic research**: Studying animal vocalizations and communication
  - **Conservation**: Monitoring endangered or threatened species
  - **Citizen science**: Engaging public participation in ecological research
- **Distribution by supercategory**:
  - Birds (Aves): ~80-85% of samples
  - Amphibians: ~8-12% of samples
  - Insects: ~5-10% of samples
  - Mammals: ~1-2% of samples
  - Reptiles: <1% of samples
- There is no `dev` split in the provided manifest.
