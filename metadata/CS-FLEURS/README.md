# CS-FLEURS

## Overview
**CS-FLEURS** is a code-switching speech dataset derived from the FLEURS sentence collection and distributed through the Hugging Face dataset `byan/cs-fleurs`. It is designed for **code-switching automatic speech recognition (CS-ASR)** and utterance-level **language-pair identification**.

The dataset contains speech where one non-English language is mixed with English. Each sample provides an audio path, transcription, and a `language` label indicating the code-switching language pair, such as `ara-eng` for Arabic-English or `cmn-eng` for Mandarin Chinese-English. Audio in this manifest is stored at **16 kHz**.

## Supported Tasks
1. **Code-Switching Automatic Speech Recognition (CS-ASR)**
2. **Language-Pair Identification**

---

## Dataset Statistics

| Split | # Samples | Duration |
|------|----------:|---------:|
| train | 41,445 | 127.9 hours |
| test | 11,321 | 35.8 hours |
| total | 52,766 | 163.7 hours |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID from the source dataset |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset name: `CS-FLEURS` |
| `language` | Code-switching language-pair label |
| `text` | Ground-truth code-switched transcription |

---

## Example Entries

```json
{"id": "30_ara-spk0_sample0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/train/30_ara-spk0_sample0.wav", "sampling_rate": 16000, "duration": 4.960688, "dataset": "CS-FLEURS", "language": "ara-eng", "text": "اشتعلت النيران في **prison** **Abu** غريب بالعراق أثناء أحداث **riot.**"}

{"id": "638_ara-spk0_sample0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/train/638_ara-spk0_sample0.wav", "sampling_rate": 16000, "duration": 16.992688, "dataset": "CS-FLEURS", "language": "ara-eng", "text": "بعد أريع سنوات، تم منح براءة **granted,** **which** كانت أول براءة اختراع في العالم يتم منحها في مجال التصوير بالرنين **MRI.**"}

{"id": "540_ara-spk0_sample0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/train/540_ara-spk0_sample0.wav", "sampling_rate": 16000, "duration": 5.707375, "dataset": "CS-FLEURS", "language": "ara-eng", "text": "**also called** المستعمرون، الذين شاهدوا **this** النشاط، بتعزيزات."}

{"id": "1961_ara-spk1_sample0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/test/1961_ara-spk1_sample0.resamp.wav", "sampling_rate": 16000, "duration": 21.035375, "dataset": "CS-FLEURS", "language": "ara-eng", "text": "ومن بين أكثر الطرق شيوعاً التي used لتوضيح importance of socialization الاجتماعية، الاعتماد على cases the few unfortunate للأطفال الذين عانوا، من خلال الإهمال أو سوء misfortune, أو wilful abuse, المتعمد، غير مرتبطين اجتماعياً من جانب البالغين أثناء نشأتهم."}

{"id": "1934_ara-spk0_sample0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/CS-FLEURS/audio/test/1934_ara-spk0_sample0.resamp.wav", "sampling_rate": 16000, "duration": 9.132, "dataset": "CS-FLEURS", "language": "ara-eng", "text": "you أن تسمع صوت السيّاح والبائعين هنا دائماً عادةً. story الصوت والضوء is like قصة book."}
```

---

## Task Usage

### 1. Code-Switching Automatic Speech Recognition (CS-ASR)
- **Target field:** `text` (code-switched transcription)
- **Input:** `path` audio file
- **Metric:** ASR metrics such as word error rate (WER), character error rate (CER), or mixed-unit error rate depending on the language pair and evaluation protocol

### 2. Language-Pair Identification
- **Target field:** `language` (code-switching language pair)
- **Input:** `path` audio file, or optionally the transcript for text-based language-pair classification

---

## Label Space

### Language-Pair Labels
<details>
<summary>Show 16 language-pair labels:</summary>

`ara-eng` - Arabic-English

`ces-eng` - Czech-English

`cmn-eng` - Mandarin Chinese-English

`deu-eng` - German-English

`fra-eng` - French-English

`hin-eng` - Hindi-English

`hun-eng` - Hungarian-English

`ita-eng` - Italian-English

`jpn-eng` - Japanese-English

`kor-eng` - Korean-English

`nld-eng` - Dutch-English

`pol-eng` - Polish-English

`por-eng` - Portuguese-English

`rus-eng` - Russian-English

`spa-eng` - Spanish-English

`tur-eng` - Turkish-English

</details>

### Language Distribution

| Language Pair | Train | Test |
|--------------|------:|-----:|
| `ara-eng` | 1,491 | 428 |
| `ces-eng` | 2,742 | 723 |
| `cmn-eng` | 3,048 | 945 |
| `deu-eng` | 2,922 | 862 |
| `fra-eng` | 3,071 | 676 |
| `hin-eng` | 1,926 | 418 |
| `hun-eng` | 3,009 | 905 |
| `ita-eng` | 2,967 | 865 |
| `jpn-eng` | 2,097 | 650 |
| `kor-eng` | 2,211 | 382 |
| `nld-eng` | 2,853 | 364 |
| `pol-eng` | 2,756 | 758 |
| `por-eng` | 2,693 | 919 |
| `rus-eng` | 2,488 | 775 |
| `spa-eng` | 2,709 | 908 |
| `tur-eng` | 2,462 | 743 |

---

## Notes
- All audio files in these manifests are sampled at **16 kHz**.
- The manifest contains two splits: `train` and `test`; no `dev` split is provided in this metadata directory.
- The `train` manifest was generated from source samples whose audio path matches `xtts/train`.
- The `test` manifest was generated from source samples whose audio path matches `xtts/test1`.
- The `language` field identifies the language pair for the whole utterance. It does not provide word-level or segment-level language boundaries.
- English spans in many training transcripts are marked with Markdown-style `**...**` emphasis. The test transcripts in this manifest do not use those markers.
- Transcriptions may contain mixed scripts, punctuation, and embedded English words or phrases.
- The task is challenging because recognition requires handling multilingual phonetics, script changes, lexical borrowing, and intra-utterance language switching.
- For CS-ASR, use `text` as the recognition target and preserve the source transcription convention unless a separate normalization protocol is defined.
