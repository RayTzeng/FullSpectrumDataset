# FLEURS

## Overview
**FLEURS** is the speech version of the **FLoRes** machine translation benchmark. It contains **2,009 n-way parallel sentences** from the publicly available **FLoRes dev** and **devtest** sets, covering **102 languages**.

This dataset can be used for:
1. **Multilingual Speech Recognition**
2. **Language Identification**
3. **Language Group Classification**
4. **Speaker Gender Classification**

Training sets contain around **10 hours of supervision per language**. Speakers in the **train** split are different from speakers in the **dev/test** splits.

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 271,798 |
| dev | 34,452 |
| test | 77,810 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Sample ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `text` | Ground-truth transcription |
| `lang` | Language label |
| `gender` | Speaker gender label |
| `lang_group` | Geographical language group |

---

## Example Entries

```json
{"id": 1378, "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/FLEURS/7f500292c3add67dd9713da3256bfa483d25d203192a63493b6606b36d7bed6b/train/6962621185044216129.wav", "duration": "26.700", "dataset": "FLEURS", "text": "Ozi ihe-omumundu-banyere-uburu ewetala akaebe ana ahu anya maka usoro kowaputa nye nyocha nke nkota. Nihi ya obelatala ogbe nchoputa ma mee ya kpom-kwem nke ukwu karia.", "lang": "Igbo", "gender": "female", "lang_group": "sub-saharan africa", "sampling_rate": 16000}

{"id": 1029, "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/FLEURS/a47a0641ed7e7174e90532d20b295d87fe7d8319f0beae87ef9fd42f473dac5b/train/4200864968094606042.wav", "duration": "16.080", "dataset": "FLEURS", "text": "Ein anderer Unterschied war, dass die armen Leute und die Frauen ihr Essen auf Stühlen sitzend aßen. Die reichen Männer hielten dagegen lieber gemeinsame Bankette ab, bei denen sie auf der Seite lagen, während sie ihre Mahlzeiten verspeisten.", "lang": "German", "gender": "female", "lang_group": "western europe", "sampling_rate": 16000}

{"id": 1271, "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/FLEURS/b731254681c0160d53c954a9b8963f59c46313c0e33644cc3e29235768802976/train/1169897688282629909.wav", "duration": "29.040", "dataset": "FLEURS", "text": "Туризам заснован на природи привлачи људе који су заинтересовани за посете природним подручјима, а у сврху уживања у пејзажу, укључујући биљни и животињски свет дивљине.", "lang": "Serbian", "gender": "male", "lang_group": "eastern europe", "sampling_rate": 16000}
```

---

## Task Usage

### 1. Multilingual Speech Recognition
- **Target field:** `text` (transcription)

### 2. Language Identification
- **Target field:** `lang` (language label)

### 3. Language Group Classification
- **Target field:** `lang_group` (geographical language group)

### 4. Speaker Gender Classification
- **Target field:** `gender` (speaker gender label)

---

## Evaluation Notes

For **multilingual ASR**, multilingual fine-tuning is used and performance is reported using **average unit error rate (UER)** across languages, where units are defined at the **character/sign** level.

For classification tasks, the target label depends on the selected field (`lang`, `lang_group`, or `gender`).

---

## Language Groups

FLEURS languages are grouped into **seven geographical areas**.

<details>
<summary>Show language groups</summary>

### Western Europe
Asturian, Bosnian, Catalan, Croatian, Danish, Dutch, English, Finnish, French, Galician, German, Greek, Hungarian, Icelandic, Irish, Italian, Kabuverdianu, Luxembourgish, Maltese, Norwegian, Occitan, Portuguese, Spanish, Swedish, Welsh

### Eastern Europe
Armenian, Belarusian, Bulgarian, Czech, Estonian, Georgian, Latvian, Lithuanian, Macedonian, Polish, Romanian, Russian, Serbian, Slovak, Slovenian, Ukrainian

### Central-Asia / Middle-East / North-Africa
Arabic, Azerbaijani, Hebrew, Kazakh, Kyrgyz, Mongolian, Pashto, Persian, Sorani-Kurdish, Tajik, Turkish, Uzbek

### Sub-Saharan Africa
Afrikaans, Amharic, Fula, Ganda, Hausa, Igbo, Kamba, Lingala, Luo, Northern-Sotho, Nyanja, Oromo, Shona, Somali, Swahili, Umbundu, Wolof, Xhosa, Yoruba, Zulu

### South Asia
Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Nepali, Oriya, Punjabi, Sindhi, Tamil, Telugu, Urdu

### South-East Asia
Burmese, Cebuano, Filipino, Indonesian, Javanese, Khmer, Lao, Malay, Maori, Thai, Vietnamese

### East Asia (CJK Languages)
Cantonese, Mandarin Chinese, Japanese, Korean

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- The dataset contains **102 languages** with parallel sentence content across languages.
- Because the same corpus supports multiple tasks, the task definition depends on the selected target field.