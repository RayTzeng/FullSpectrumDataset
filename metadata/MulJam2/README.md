# MulJam2

## Overview
**MulJam2** is a large-scale multilingual audio-to-lyrics transcription dataset based on the MTG-Jamendo corpus. The dataset contains over **153,000 vocal music segments** spanning **6 languages** (English, French, Spanish, Italian, German, and Russian), with each segment annotated with time-aligned lyrics transcriptions. Audio is pre-segmented from full-length music tracks, with segments ranging from a few seconds to 30 seconds in duration. This dataset is designed for automatic lyrics transcription (ALT) research, supporting both monolingual and cross-lingual music understanding tasks.

## Supported Tasks
1. **Automatic Lyrics Transcription (ALT)**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 147,708 |
| dev | 3,492 |
| test | 2,170 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment identifier (format: `{track_id}_{segment_num}`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `language` | Language of the lyrics |
| `lyrics` | Ground-truth lyrics transcription |

---

## Example Entries

```json
{"id": "1001890_0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MulJam2/audio/train/1001890_0.wav", "sampling_rate": 16000, "duration": 4.0, "dataset": "MulJam2", "language": "English", "lyrics": "THE GENIUS OF THE CROWD"}

{"id": "1001890_1", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MulJam2/audio/train/1001890_1.wav", "sampling_rate": 16000, "duration": 17.0, "dataset": "MulJam2", "language": "English", "lyrics": "THERE IS ENOUGH TREACHERY HATRED VIOLENCE ABSURDITY AND THE AVERAGE HUMAN BEING TO SUPPLY ANY GIVEN ARMY ON ANY GIVEN DAY"}

{"id": "1001890_2", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/MulJam2/audio/train/1001890_2.wav", "sampling_rate": 16000, "duration": 6.0, "dataset": "MulJam2", "language": "English", "lyrics": "AND THE BEST AT MURDER ARE THOSE WHO PREACH AGAINST IT"}
```

---

## Task Usage

### 1. Automatic Lyrics Transcription (ALT)
- **Target field:** `lyrics` (lyrics transcription)
- **Optional input:** `language`

---

## Label Space

*This is an open-vocabulary generation task without a predefined label space.*

### Language Distribution

The dataset covers 6 languages with the following distribution in the training set:

| Language | Code | # Samples | Percentage |
|----------|------|----------:|------------|
| English | en | 86,549 | 58.6% |
| French | fr | 33,220 | 22.5% |
| Spanish | es | 15,119 | 10.2% |
| Italian | it | 7,807 | 5.3% |
| German | de | 3,208 | 2.2% |
| Russian | ru | 1,805 | 1.2% |

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio files are stored in **WAV format**.
- Audio segments have **variable duration**, ranging from 0.1 to 30 seconds (average ~5.4 seconds).
- **Lyrics are in uppercase** format.
- The dataset is derived from the **MTG-Jamendo** music corpus with multilingual lyrics annotations.
- Segments are **pre-segmented** from full-length music tracks, with each segment corresponding to a lyrical phrase or line.
- The dataset exhibits **language imbalance**, with English dominating (58.6%) followed by French (22.5%).
- **Challenges for ALT**:
  - **Musical accompaniment**: Lyrics must be transcribed from singing voice mixed with instrumental background
  - **Vocal effects**: Reverb, harmony, vibrato, and other vocal processing
  - **Multilingual support**: Models must handle 6 different languages with varying orthographic conventions
  - **Variable singing styles**: From soft whispers to powerful belting across different music genres
  - **Overlapping vocals**: Backup vocals, harmonies, and choir sections
- **Evaluation metrics**: Word Error Rate (WER), Character Error Rate (CER), BLEU score
- This dataset is part of the **MARBLE benchmark** (Music Audio Representation Benchmark for Universal Evaluation)
- Unlike automatic speech recognition (ASR), lyrics transcription must handle:
  - **Melodic variations**: Words sung at different pitches and rhythms
  - **Repetition and structure**: Choruses, verses, and repeated phrases
  - **Non-speech vocalizations**: Vocal runs, ad-libs, and melismatic passages
  - **Background music**: Strong instrumental accompaniment that may mask vocals

---

## Citation

If you use this dataset, please cite the MARBLE paper:

```bibtex
@article{yuan2023marble,
  title={MARBLE: Music Audio Representation Benchmark for Universal Evaluation},
  author={Yuan, Ruibin and Ma, Yinghao and Li, Yizhi and Zhang, Ge and Chen, Xingran and Yin, Hanzhi and Zhuo, Le and Liu, Yiqi and Huang, Jiawen and Tian, Zeyue and others},
  journal={arXiv preprint arXiv:2306.10548},
  year={2023}
}
```
