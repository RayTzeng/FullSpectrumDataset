# UASpeech

## Overview
**UASpeech** is a benchmark corpus for dysarthric speech research, created to support the development of speech technologies for people with neuromotor speech disorders. The dataset consists of isolated-word recordings from **16 speakers with cerebral-palsy-related dysarthria** and **8 matched control speakers** (neurologically healthy). Each speaker recorded approximately 3,000 isolated words across three recording sessions (blocks B1, B2, B3) using multiple microphones. The corpus contains common words, uncommon words, and digit sequences, totaling over 68,000 recordings. Audio is recorded at **16 kHz** and paired with word-level transcriptions. This dataset enables research on dysarthric speech recognition, severity classification, and assistive technology development.

## Supported Tasks
1. **Dysarthria Severity Classification**
2. **Dysarthria Type Classification**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 45,319 |
| test | 22,797 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique recording ID (format: SPEAKER_BLOCK_WORD_MIC) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `dysarthria_type` | Type of dysarthria (or "None" for controls) |
| `severity` | Severity level label |
| `severity_numeric` | Numeric severity rating (0-5) |
| `sentence` | Ground-truth word transcription (lowercase) |

---

## Example Entries

```json
{"id": "CF02_B1_CW100_M3", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/UASpeech/CF02/CF02_B1_CW100_M3.wav", "sampling_rate": 16000, "duration": 1.453813, "dataset": "UASpeech", "dysarthria_type": "None", "severity": "none", "severity_numeric": 0, "sentence": "yes"}

{"id": "M10_B1_UW45_M5", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/UASpeech/M10/M10_B1_UW45_M5.wav", "sampling_rate": 16000, "duration": 2.145125, "dataset": "UASpeech", "dysarthria_type": "Mixed", "severity": "high", "severity_numeric": 4, "sentence": "moisten"}

{"id": "F03_B3_CW200_M7", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/UASpeech/F03/F03_B3_CW200_M7.wav", "sampling_rate": 16000, "duration": 1.876500, "dataset": "UASpeech", "dysarthria_type": "Spastic", "severity": "low", "severity_numeric": 2, "sentence": "time"}
```

---

## Task Usage

### 1. Dysarthria Severity Classification
- **Target field:** `severity` (severity level label)
- **Alternative target:** `severity_numeric` (numeric rating for regression)

### 2. Dysarthria Type Classification
- **Target field:** `dysarthria_type` (dysarthria type)

---

## Label Space

### Dysarthria Types
<details>
<summary>Show 4 available types:</summary>

`Spastic`, `Athetoid`, `Mixed`, `None`

**Definitions:**
- **Spastic** - Characterized by stiff, slow movements and harsh voice quality due to increased muscle tone (11 speakers)
- **Athetoid** - Characterized by involuntary movements and variable speech patterns due to fluctuating muscle tone (2 speakers)
- **Mixed** - Combination of multiple dysarthria types with features from different categories (2 speakers)
- **None** - Control speakers with no dysarthria (8 speakers)

</details>

### Severity Levels
<details>
<summary>Show 6 available severity levels:</summary>

`none`, `very low`, `low`, `mid`, `high`, `very high`

**Numeric mapping:**
- **none (0)** - Control speakers with no speech impairment
- **very low (1)** - Minimal speech impairment with near-normal intelligibility
- **low (2)** - Mild speech impairment with good intelligibility
- **mid (3)** - Moderate speech impairment with reduced intelligibility
- **high (4)** - Severe speech impairment with significantly reduced intelligibility
- **very high (5)** - Very severe speech impairment with minimal intelligibility

</details>

### Word Transcriptions
<details>
<summary>Details about word vocabulary:</summary>

The dataset contains approximately **755 unique isolated words** spanning three categories:
- **Common Words (CW)**: 300 most frequently used English words (e.g., "yes", "the", "have", "with")
- **Uncommon Words (UW)**: 455 less common English words (e.g., "moisten", "boulevard", "chronicle")
- **Digits (D)**: Numbers and digit sequences (e.g., "zero", "one", "ten")

This is an **open-vocabulary** isolated word recognition task where the target field contains the transcription of a single spoken word.

</details>

---

## Train/Test Split

This manifest uses the **HuggingFace split** (matching `ngdiana/uaspeech` dataset), which is a **speaker-dependent** split:

- **Train**: All recordings from blocks **B1 + B3** (~66% of data)
- **Test**: All recordings from block **B2** (~34% of data)

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from 0.5 to 3 seconds per isolated word.
- Each recording ID follows the format: `{SPEAKER}_{BLOCK}_{WORD}_{MIC}`
  - Example: `F02_B1_CW100_M3` = Speaker F02, Block 1, Common word #100, Microphone 3
- The dataset includes recordings from **multiple microphones** (M1-M8) per session, providing multi-condition training data.
- **Control speakers** (prefixed with `C`, e.g., CM04, CF02) have no dysarthria and serve as neurologically healthy baseline comparisons.
- **Dysarthric speakers** are prefixed with speaker ID only (e.g., M01, F02, M10).
- The dataset contains **24 speakers total**:
  - **16 dysarthric speakers**: 11 male (M01, M04, M07, M08, M09, M10, M11, M12, M14, M16) + 5 female (F02, F03, F04)
  - **8 control speakers**: 8 male (CM04-CM13) + 3 female (CF02-CF04)
- Severity distribution in training set:
  - Control (none): 20,000 samples (44.1%)
  - Spastic dysarthria: 17,375 samples (38.3%)
  - Mixed dysarthria: 4,000 samples (8.8%)
  - Athetoid dysarthria: 3,944 samples (8.7%)
- This is a highly valuable dataset for:
  - **Dysarthric speech recognition**: Training robust ASR for impaired speech
  - **Severity assessment**: Automatic clinical evaluation tools
  - **Assistive technology**: Communication aids for people with cerebral palsy
  - **Speaker adaptation**: Personalized models for individual speakers
- The **speaker-dependent** split makes this task easier than speaker-independent evaluation, as the model can learn speaker-specific characteristics during training.
- Each word transcription is stored in lowercase in the `sentence` field.
- The corpus includes three recording blocks (B1, B2, B3) per speaker, enabling within-speaker temporal variation analysis.

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{kim2008dysarthric,
  title={Dysarthric speech database for universal access research},
  author={Kim, Hoirin and Hasegawa-Johnson, Mark and Perlman, Adrienne and
          Gunderson, Jon and Huang, Thomas S and Watkin, Kenneth and Frame, Simone},
  booktitle={Proc. INTERSPEECH},
  pages={1741--1744},
  year={2008}
}
```

## References
- Official website: http://www.isle.illinois.edu/sst/data/UASpeech/
- HuggingFace dataset: https://huggingface.co/datasets/ngdiana/uaspeech
- Documentation: http://www.isle.illinois.edu/sst/data/UASpeech/UAspDocumentation.pdf
