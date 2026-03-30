# EasyCall

## Overview
**EasyCall** is an Italian dysarthric speech command corpus created to support the development of ASR-based assistive technologies for people with dysarthria. The dataset contains recordings from **30 dysarthric speakers** and **24 healthy control speakers**, totaling **55 speakers**. Each speaker recorded approximately 66-69 Italian voice commands and phrases across multiple sessions (typically 5-8 sessions per speaker). The original corpus consists of **21,386 isolated word and command recordings**. To enhance audio diversity and support longer-context training, this manifest includes **concatenated audio files** where recordings from multiple sessions are combined. Audio is recorded at **8 kHz** (telephone quality) and paired with dysarthria type and severity annotations. The dataset enables research on dysarthric speech recognition, severity classification, and voice command systems for motor-impaired users.

## Supported Tasks
1. **Dysarthric Speech Detection**
2. **Dysarthria Severity Estimation**
3. **Dysarthria Type Classification**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 21,711 |
| dev | 7,795 |
| test | 9,541 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique recording ID (format: SPEAKER_UTTERANCE_nN_sXX) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (8000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `dysarthria_type` | Type of dysarthria (or "None" for controls) |
| `severity_measure` | Severity rating (0-5) |

---

## Example Entries

```json
{"id": "f01_Aggiungi ai preferiti_n1_s01", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/EasyCall-concat/f01/f01_Aggiungi ai preferiti_n1_s01.wav", "sampling_rate": 8000, "duration": 3.56, "dataset": "EasyCall", "dysarthria_type": "paretic", "severity_measure": 1}

{"id": "m09_Apri rubrica_n3_s02_04_05", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/EasyCall-concat/m09/m09_Apri rubrica_n3_s02_04_05.wav", "sampling_rate": 8000, "duration": 7.82, "dataset": "EasyCall", "dysarthria_type": "cerebellar", "severity_measure": 4}

{"id": "fc02_Chiama_n1_s03", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/EasyCall-concat/fc02/fc02_Chiama_n1_s03.wav", "sampling_rate": 8000, "duration": 1.94, "dataset": "EasyCall", "dysarthria_type": "None", "severity_measure": 0}
```

---

## Task Usage

### 1. Dysarthric Speech Detection
- **Target field:** `dysarthria_type` (binary classification: "None" vs. any dysarthria type)

### 2. Dysarthria Severity Estimation
- **Target field:** `severity_measure` (numeric severity rating)

### 3. Dysarthria Type Classification
- **Target field:** `dysarthria_type` (dysarthria type)

---

## Label Space

### Dysarthria Types
<details>
<summary>Show 5 available types:</summary>

`paretic`, `cerebellar`, `extrapyramidal`, `pyramidal`, `None`

**Definitions:**
- **paretic** - Weakness or paralysis of speech muscles due to peripheral nervous system damage. Characteristics: Reduced muscle strength, imprecise articulation, hypernasality (24 speakers)
- **cerebellar** - Coordination and timing issues due to cerebellar dysfunction. Characteristics: Irregular rhythm, scanning speech, excess and equal stress (4 speakers)
- **extrapyramidal** - Movement disorder related to basal ganglia dysfunction (e.g., Parkinson's disease). Characteristics: Reduced loudness, monotone pitch, rushed speech, imprecise articulation (1 speaker)
- **pyramidal** - Upper motor neuron damage affecting corticospinal tract. Characteristics: Spastic speech, slow rate, strained-strangled voice quality (1 speaker)
- **None** - Control speakers with no dysarthria (24 speakers)

</details>

### Severity Levels
<details>
<summary>Show 6 available severity levels:</summary>

`0`, `1`, `2`, `3`, `4`, `5`

**Numeric ratings:**
- **0** - Healthy control speakers with no speech impairment
- **1** - Mild dysarthria with minimal impact on intelligibility
- **2** - Mild-moderate dysarthria with slight reduction in intelligibility
- **3** - Moderate dysarthria with noticeable impact on intelligibility
- **4** - Moderate-severe dysarthria with significantly reduced intelligibility
- **5** - Severe dysarthria with minimal intelligibility

**Note:** This is a **regression task** where the target is a continuous numeric value from 0 to 5, or a **6-class classification task** treating each severity level as a discrete category.

</details>

---

## Audio Concatenation Strategy

This manifest includes both single-session recordings and **concatenated audio files** to enhance diversity and support longer-context training:

### Concatenation Levels

For each speaker and utterance, multiple versions are created:
- **n=1** (54.8%): Single session recording (matches original EasyCall dataset)
- **n=2** (9.5%): 2 recordings from 2 different sessions concatenated
- **n=3** (9.1%): 3 recordings from 3 different sessions concatenated
- **n=4** (8.8%): 4 recordings concatenated
- **n=5** (8.7%): 5 recordings concatenated
- **n=6** (8.3%): 6 recordings concatenated
- **n=7** (0.7%): 7 recordings concatenated
- **n=8** (0.2%): 8 recordings concatenated

### ID Format

The `id` field encodes the concatenation information:
- Format: `{speaker}_{utterance}_n{N}_s{sessions}`
- Example: `f01_Aggiungi_n3_s02_04_05` means:
  - Speaker: f01
  - Utterance: "Aggiungi"
  - n=3: 3 sessions concatenated
  - Sessions: s02, s04, s05 (in random order)

### Why Concatenation?

1. **Data augmentation**: Increases training data diversity
2. **Longer contexts**: Enables models to learn from multi-utterance sequences
3. **Robustness**: Exposes models to temporal variations across sessions
4. **Flexibility**: Use n=1 only for baseline comparison, or all n levels for enhanced training

---

## Train/Dev/Test Split

This manifest uses a **speaker-independent split** matching the `changelinglab/easycall-dysarthria` HuggingFace dataset:

- **Train**: 31 speakers (55.6% of data)
- **Dev**: 11 speakers (20.0% of data)
- **Test**: 13 speakers (24.4% of data)

No speaker appears in multiple splits, ensuring evaluation on truly unseen speakers. This split is suitable for:
- Speaker-independent ASR evaluation
- Generalization to new dysarthric speakers
- Reproducible comparison with published benchmarks

**Note:** The n=1 entries (21,385 total) exactly match the original EasyCall dataset size (21,386 recordings), with minimal discrepancy due to data versioning.

---

## Notes
- All audio files are sampled at **8 kHz** (telephone quality), reflecting the corpus's focus on phone-based assistive applications.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**:
  - Single session (n=1): typically 1-3 seconds per utterance
  - Concatenated (n≥2): proportionally longer based on number of sessions
- The dataset contains approximately **66-69 unique Italian voice commands and phrases** per speaker, including:
  - **Numbers**: Zero, Uno, Due, Tre, Quattro, Cinque, Sei, Sette, Otto, Nove
  - **Phone commands**: Chiama (call), Termina chiamata (end call), Vivavoce (speakerphone), Rubrica (contacts)
  - **Navigation**: Apri (open), Chiudi (close), Indietro (back), Scorri (scroll)
  - **Actions**: Aggiungi (add), Cancella (delete), Salva (save), Seleziona (select)
- The dataset includes **55 speakers total**:
  - **30 dysarthric speakers**: 19 male, 11 female
  - **24 control speakers**: 14 male (mc01-mc14), 10 female (fc01-fc10)
- **Language**: All utterances are in Italian
- Dysarthria type distribution:
  - Paretic: 24 speakers (most common)
  - Cerebellar: 4 speakers
  - Extrapyramidal: 1 speaker (m01)
  - Pyramidal: 1 speaker (m14)
- Severity distribution in training set:
  - Level 0 (healthy): 9,945 samples (45.8%)
  - Level 1 (mild): 6,567 samples (30.2%)
  - Level 3 (moderate): 3,247 samples (15.0%)
  - Level 4 (moderate-severe): 1,452 samples (6.7%)
  - Level 5 (severe): 500 samples (2.3%)
  - **Note**: Level 2 appears only in dev split (8.0%)
- Each speaker recorded multiple sessions (typically 5-8 sessions), with each session containing the same set of utterances.
- Concatenation order is randomized with a fixed seed (default: 42) for reproducibility.
- The **speaker-independent** split ensures no speaker overlap between train/dev/test, making this a challenging generalization task.
- This is particularly valuable for:
  - **Italian ASR for pathological speech**: Training models on dysarthric Italian
  - **Voice command systems**: Building assistive technologies for motor-impaired users
  - **Severity assessment**: Automatic clinical evaluation tools for Italian speakers
  - **Cross-linguistic dysarthria research**: Comparing dysarthric speech patterns across languages
- Recommended usage:
  - Use **n=1 only** to match the original EasyCall benchmark
  - Use **all n levels** for enhanced training with data augmentation and longer contexts
  - Filter by `severity_measure > 0` to focus on dysarthric speakers only

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{gadaleta2019easycall,
  title={EasyCall: A dysarthric speech corpus for Italian},
  author={Gadaleta, Matteo and Menegotto, Alice and Boni, Andrea and Carioli, Laura and
          Quaglini, Silvana and Romano, Lucia and Sinforiani, Elena and Cavallini, Alessio},
  booktitle={Proceedings of INTERSPEECH},
  pages={3719--3720},
  year={2019}
}
```

## References
- HuggingFace dataset: https://huggingface.co/datasets/changelinglab/easycall-dysarthria
- Original paper: [INTERSPEECH 2019](https://www.isca-speech.org/archive/interspeech_2019/gadaleta19_interspeech.html)
