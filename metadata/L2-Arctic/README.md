# L2-Arctic

## Overview
**L2-Arctic** is a non-native English speech corpus created to support research on accented speech and pronunciation. The dataset contains read English speech from **24 speakers** with **six different native-language backgrounds**—Arabic, Mandarin Chinese, Hindi, Korean, Spanish, and Vietnamese. Audio is recorded at **44.1 kHz** and includes phonetic annotations for pronunciation errors in a subset of the corpus. The dataset consists of two components: (1) **CMU ARCTIC sentences** (read speech from standardized prompts) and (2) **Suitcase corpus** (spontaneous speech narratives describing a picture sequence).

## Supported Tasks
1. **Automatic Speech Recognition (ASR)**
2. **Mispronunciation Detection**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 24,180 |
| test | 2,687 |

**Annotated samples with mispronunciation labels:**
- Train: 3,076 utterances (~12.7%)
- Test: 312 utterances (~11.6%)

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `text` | Ground-truth transcription |
| `mispronunciation` | List of mispronunciation annotations |

### Mispronunciation Annotation Format

Each mispronunciation is a string with the format:
```
"{error_type}, [{start}-{end}], {correct_phone}, {perceived_phone}, {word}"
```

Where:
- **error_type**: `substitution`, `deletion`, or `addition`
- **start-end**: Time interval in seconds
- **correct_phone**: Canonical phone (ARPABET format)
- **perceived_phone**: Actually produced phone
- **word**: Word containing the error

---

## Example Entries

```json
{"id": "BWC_arctic_a0008", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/L2-Arctic/BWC/BWC/wav/arctic_a0008.wav", "sampling_rate": 44100, "duration": 3.234943, "dataset": "L2-Arctic", "text": "Gad your letter came just in time", "mispronunciation": ["substitution, [0.14-0.37], AE, AA, gad", "addition, [1.42-1.47], sil, HH, letter", "substitution, [1.75-1.86], EY, EH, came", "substitution, [2.18-2.29], JH, CH, just", "deletion, [2.48-2.51], T, sil, just"]}

{"id": "ZHAA_arctic_a0359", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/L2-Arctic/ZHAA/ZHAA/wav/arctic_a0359.wav", "sampling_rate": 44100, "duration": 3.273175, "dataset": "L2-Arctic", "text": "Earth and gravel seemed to fill the pan", "mispronunciation": []}

{"id": "ASI_arctic_b0268", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/L2-Arctic/ASI/ASI/wav/arctic_b0268.wav", "sampling_rate": 44100, "duration": 2.070544, "dataset": "L2-Arctic", "text": "Saxon nodded and the boy frowned", "mispronunciation": []}
```

---

## Task Usage

### 1. Automatic Speech Recognition (ASR)
- **Target field:** `text` (transcription)

### 2. Mispronunciation Detection
- **Target field:** `mispronunciation` (list of error annotations)
- **Note:** Only a subset of utterances (~12%) have mispronunciation annotations

---

## Label Space

### Native Languages
<details>
<summary>Show 6 native language backgrounds:</summary>

**Arabic** (4 speakers):
- ABA (M), SKA (F), YBAA (M), ZHAA (F)

**Mandarin Chinese** (4 speakers):
- BWC (M), LXC (F), NCC (F), TXHC (M)

**Hindi** (4 speakers):
- ASI (M), RRBI (M), SVBI (F), TNI (F)

**Korean** (4 speakers):
- HJK (F), HKK (M), YDCK (F), YKWK (M)

**Spanish** (4 speakers):
- EBVS (M), ERMS (M), MBMPS (F), NJS (F)

**Vietnamese** (4 speakers):
- HQTV (M), PNV (F), THV (F), TLV (M)

</details>

### Mispronunciation Error Types
<details>
<summary>Show 3 error types:</summary>

**Substitution**: Incorrect phone produced in place of correct phone
- Example: `substitution, [1.75-1.86], EY, EH, came` (produced "EH" instead of "EY")

**Deletion**: Expected phone omitted
- Example: `deletion, [2.48-2.51], T, sil, just` (final "T" deleted)

**Addition**: Unexpected phone inserted
- Example: `addition, [1.42-1.47], sil, HH, letter` (spurious "HH" added)

</details>

---

## Corpus Composition

The L2-Arctic dataset consists of two sub-corpora:

### 1. CMU ARCTIC Sentences (Main Corpus)
- **Content**: Read speech from standardized CMU ARCTIC prompts
- **Speakers**: All 24 speakers
- **Files per speaker**: ~1,000-1,130 utterances
- **Duration**: Typically 2-8 seconds per utterance
- **Annotations**: Subset has detailed phonetic alignment and mispronunciation labels

### 2. Suitcase Corpus (Spontaneous Speech)
- **Content**: Spontaneous narrative descriptions of a picture sequence
- **Task**: Describe a story about two people with identical suitcases
- **Files**: One long recording per speaker (24 total)
- **Duration**: ~50-70 seconds per recording
- **Annotations**: Detailed mispronunciation annotations for all speakers

---

## Notes
- All audio files are sampled at **44.1 kHz**.
- Audio clips have **variable duration**, typically 2-8 seconds for Arctic sentences.
- This is both an **ASR task** (open-vocabulary transcription) and a **mispronunciation detection task** (phone-level error classification).
- The dataset provides **balanced language representation** with 4 speakers per native language background (2 male, 2 female).
- Phonetic annotations use **ARPABET** phone symbols (e.g., AE, EY, DH).
- **Mispronunciation annotations** are available for only a subset of utterances:
  - Approximately **12.7% of training data** has error annotations
  - Approximately **11.6% of test data** has error annotations
  - All **suitcase corpus** recordings have detailed annotations
- Common error patterns vary by native language:
  - **Mandarin speakers**: Often substitute voiceless stops for voiced (T/D confusion)
  - **Spanish speakers**: Vowel substitutions and consonant deletions
  - **Arabic speakers**: Substitutions in vowel quality
  - **Hindi speakers**: Consonant deletions and voicing errors
  - **Korean speakers**: Stop consonant substitutions
  - **Vietnamese speakers**: Tone-influenced vowel and consonant errors
- The dataset is particularly valuable for:
  - **Accent recognition**: Identifying speaker native language
  - **Pronunciation assessment**: Detecting and classifying errors
  - **Computer-assisted language learning (CALL)**: Providing feedback on pronunciation
  - **Robust ASR**: Training models on diverse accented speech
- Each speaker's directory contains:
  - `wav/`: Audio files
  - `transcript/`: Text transcriptions
  - `annotation/`: TextGrid files with phonetic alignments (subset)
- The **train/test split** is designed to ensure speaker independence and balanced language representation.

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{zhao2018l2arctic,
  title={L2-ARCTIC: A non-native English speech corpus},
  author={Zhao, Guanlong and Sonsaat, Sinem and Silpachai, Alif and Lucic, Ivana and Chukharev-Hudilainen, Evgeny and Levis, John and Gutierrez-Osuna, Ricardo},
  booktitle={Proc. Interspeech},
  pages={2783--2787},
  year={2018}
}
```

## References
- Project page: https://psi.engr.tamu.edu/l2-arctic-corpus/
- CMU ARCTIC corpus: http://www.festvox.org/cmu_arctic/
- ARPABET phoneme set: https://en.wikipedia.org/wiki/ARPABET
