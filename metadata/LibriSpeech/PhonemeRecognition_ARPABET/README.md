# LibriSpeech

## Overview
**LibriSpeech** is a large-scale corpus of read English speech derived from LibriVox audiobooks. This task extends the standard ASR dataset by providing **phoneme-level transcriptions** using the ARPABET phonetic alphabet. Each audio file is paired with a sequence of phonemes representing the pronunciation of the spoken words, with word boundaries explicitly marked. The phoneme alignments are obtained from Montreal Forced Alignment (MFA) TextGrid files. This dataset enables research on phoneme recognition, pronunciation modeling, and low-level acoustic-phonetic analysis of speech.

## Supported Tasks
1. **Phoneme Recognition (ARPABET)**

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 129,573 |
| dev | 2,484 |
| test | 2,361 |

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
| `text` | Ground-truth text transcription |
| `ARPABET` | Phoneme sequence in ARPABET format with word boundaries |

---

## Example Entries

```json
{"id": "1272-128104-0000", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0000.flac", "sampling_rate": 16000, "duration": "5.855", "dataset": "LibriSpeech", "text": "mister Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.", "ARPABET": "M IH1 S T ER0 | K W IH1 L T ER0 | IH0 Z | DH IY0 | AH0 P AA1 S AH0 L | AH1 V | DH AH0 | M IH1 D AH0 L | K L AE1 S AH0 Z | AE1 N D | W IY1 | ER0 | G L AE1 D | T UW1 | W EH1 L K AH0 M | HH IH1 Z | G AO1 S P AH0 L"}

{"id": "1272-128104-0001", "path": "/saltpool0/data/tseng/LibriSpeech/dev-clean/1272/128104/1272-128104-0001.flac", "sampling_rate": 16000, "duration": "4.815", "dataset": "LibriSpeech", "text": "Nor is mister Quilter's manner less interesting than his matter.", "ARPABET": "N AO1 R | IH0 Z | M IH1 S T ER0 | K W IH1 L T ER0 | EH1 S | M AE1 N ER0 | L EH1 S | IH1 N T ER0 IH0 S T IH0 NG | DH AH0 N | HH IH0 Z | M AE1 T ER0"}

{"id": "1188-133604-0000", "path": "/saltpool0/data/tseng/LibriSpeech/test-clean/1188/133604/1188-133604-0000.flac", "sampling_rate": 16000, "duration": "10.725", "dataset": "LibriSpeech", "text": "You will find me continually speaking of four men Titian, Holbein, Turner, and Tintoret in almost the same terms.", "ARPABET": "Y UW1 | W AH0 L | F AY1 N D | M IY1 | K AH0 N T IH1 N Y UW0 L IY0 | S P IY1 K IH0 NG | AH0 V | F AO1 R | M EH1 N | T IH1 SH AH0 N | HH OW1 L B AY0 N | T ER1 N ER0 | AE1 N D | T IH1 N T OW0 R IH0 T | IH0 N | AO1 L M OW2 S T | DH AH0 | S EY1 M | T ER1 M Z"}
```

---

## Task Usage

### 1. Phoneme Recognition (ARPABET)
- **Input field:** Audio
- **Target field:** `ARPABET` (phoneme sequence with word boundaries)

---

## Label Space

The ARPABET phoneme set consists of 39 phonemes divided into vowels and consonants:

### Vowels (15 phonemes with stress markers 0, 1, 2)
- **AA** - "odd" (AA1), **AE** - "at" (AE1), **AH** - "hut" (AH0, AH1)
- **AO** - "ought" (AO1), **AW** - "cow" (AW1), **AY** - "hide" (AY1)
- **EH** - "Ed" (EH1), **ER** - "hurt" (ER0, ER1), **EY** - "ate" (EY1)
- **IH** - "it" (IH0, IH1), **IY** - "eat" (IY1), **OW** - "oat" (OW1)
- **OY** - "toy" (OY1), **UH** - "hood" (UH1), **UW** - "two" (UW1)

### Consonants (24 phonemes)
- **Stops**: B, D, G, K, P, T
- **Fricatives**: DH (thee), F, HH, S, SH, TH (theta), V, Z, ZH (seizure)
- **Affricates**: CH (cheese), JH (gee)
- **Nasals**: M, N, NG (ping)
- **Liquids**: L, R
- **Glides**: W, Y

---

## ARPABET Format

The `ARPABET` field contains phoneme sequences with word boundaries:

### Format Specification:
- **Phonemes within a word** are separated by spaces
- **Words** are separated by ` | ` (space-pipe-space)
- **Vowels** include stress markers: `0` (unstressed), `1` (primary stress), `2` (secondary stress)
- **Consonants** do not have stress markers

### Example Breakdown:
```
Text: "mister Quilter is"
ARPABET: "M IH1 S T ER0 | K W IH1 L T ER0 | IH0 Z"

Word 1 "mister": M IH1 S T ER0 (5 phonemes)
Word 2 "Quilter": K W IH1 L T ER0 (6 phonemes)
Word 3 "is": IH0 Z (2 phonemes)
```

---

## Notes
- All audio files are sampled at **16 kHz**.
- Phoneme alignments are obtained from **Montreal Forced Alignment (MFA)** TextGrid files.
- The `text` field provides the original text transcription in **lowercase** (as processed by MFA).
- **Silence markers** (`sil`, `sp`) are filtered out from the phoneme sequences.
- **Word boundaries** are explicitly marked with ` | ` to enable word-level phoneme segmentation.
- Phoneme-to-word assignment is based on **temporal overlap** (phoneme midpoint falls within word time range).
- Some samples may contain the special marker `spn` for spoken noise or non-speech sounds.
- The dataset is derived from LibriSpeech's **clean subsets** only:
  - **train** (`train-clean-100` and `train-clean-360`)
  - **dev** (`dev-clean`)
  - **test** (`test-clean`)
- ARPABET is a widely-used phonetic alphabet developed by ARPA (Advanced Research Projects Agency) for North American English.
- Stress markers on vowels enable research on prosody and pronunciation variation.
