# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Phoneme Recognition using IPA (International Phonetic Alphabet)**, providing phoneme-level transcriptions for speech recognition research.

## Supported Tasks
1. **Phoneme Recognition (IPA)**

---

## Dataset Statistics

| Split | # Samples |
|-------|-----------|
| train | 116,516 |
| dev | 11,967 |
| test | 14,756 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio/speaker identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (44100 or 48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `text` | Text transcription |
| `IPA` | Phoneme sequence in IPA format |

---

## Example Entries

```json
{"id": "voxceleb2_dev_aac_id08348_f1LF5d7FT2w_00312_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/dev/aac/id08348/f1LF5d7FT2w/00312_voicefixer.wav", "sampling_rate": 44100, "duration": 3.9, "dataset": "ParaSpeechCaps", "text": " feel about humanity. A book is one thing, I mean a writer can", "IPA": "f i l | ʌ b aʊ t | h j u m æ n ɪ t i | ʌ | b ʊ k | ɪ z | w ʌ n | θ ɪ ŋ | aɪ | m i n | ʌ | ɹ aɪ t ɜ˞ | k æ n"}

{"id": "voxceleb2_test_aac_id04656_2BkaBbeSoGI_00012_voicefixer", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/voxceleb2/test/aac/id04656/2BkaBbeSoGI/00012_voicefixer.wav", "sampling_rate": 44100, "duration": 4.4, "dataset": "ParaSpeechCaps", "text": " this what I call patchwork, you know, little things that need to be fixed or", "IPA": "ð ɪ s | w ʌ t | aɪ | k ɔ l | p æ tʃ w ɜ˞ k | j u | n oʊ | l ɪ t ʌ l | θ ɪ ŋ z | ð æ t | n i d | t u | b i | f ɪ k s t | ɔ ɹ"}

{"id": "expresso_audio_48khz_read_ex02_confused_base_ex02_confused_00377", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/expresso/audio_48khz/read/ex02/confused/base/ex02_confused_00377.wav", "sampling_rate": 48000, "duration": 2.666, "dataset": "ParaSpeechCaps", "text": "We didn't get the weather right, guys.", "IPA": "w i | t i | ɡ ɛ t | ð ʌ | w ɛ ð ɜ˞ | ɹ aɪ t | ɡ aɪ z"}
```

---

## Task Usage

### 1. Phoneme Recognition (IPA)
- **Input field:** Audio
- **Target field:** `IPA` (phoneme sequence)

---

## Label Space

### IPA Phoneme Set

IPA uses single Unicode characters for phonemes with diacritics for stress and tone:

<details>
<summary>Show common IPA symbols:</summary>

**Vowels**:
- **Monophthongs**: i, ɪ, e, ɛ, æ, ɑ, ɔ, o, ʊ, u, ʌ, ə, ɜ
- **R-colored**: ɜ˞ (r-colored vowel)

**Diphthongs**:
- aɪ (bite), aʊ (bout), ɔɪ (boy), eɪ (bait), oʊ (boat)

**Consonants**:
- **Stops**: p, b, t, d, k, g
- **Fricatives**: f, v, θ (thin), ð (this), s, z, ʃ (sh), ʒ (measure), h
- **Affricates**: tʃ (ch), dʒ (j)
- **Nasals**: m, n, ŋ (ng)
- **Liquids**: l, ɹ (r)
- **Glides**: w, j (y)

**Stress markers**:
- **ˈ** - Primary stress
- **ˌ** - Secondary stress

**Example**: "because" → /bɪˈkɔz/ (primary stress on second syllable)

</details>

---

## IPA Format

### Normalized Format (Matching ARPABET Structure)

The IPA sequences have been **normalized** to match the ARPABET format structure:

- **Space-separated phonemes**: Each phoneme is separated by a space
- **Word boundaries**: Marked with `|` (pipe character)
- **Example**: `w i | t i | ɡ ɛ t | ð ʌ` (word boundaries clearly marked)

This makes the IPA format structurally consistent with ARPABET while maintaining IPA phonetic symbols.

### Format Comparison

| Aspect | ARPABET (LibriSpeech) | IPA (ParaSpeechCaps - Normalized) |
|--------|----------------------|-----------------------------------|
| **Phoneme symbols** | Two-letter codes (DH, TH, SH) | Unicode symbols (ð, θ, ʃ) |
| **Word boundaries** | Pipe `\|` | Pipe `\|` |
| **Phoneme separation** | Spaces | Spaces |
| **Stress markers** | Digits 0-2 (AH0, AE1) | Diacritics (ˈ, ˌ) |
| **Example** | `DH AH0 T \| HH AE1 D` | `ð ʌ t \| h æ d` |

### IPA Characteristics

- **Unicode symbols**: θ, ð, ʃ, ʒ instead of multi-letter codes
- **Phonetically precise**: Diacritics for stress, tone, length
- **International standard**: Used across languages
- **Space-separated with word boundaries**: Consistent with standard phoneme recognition formats

### Comparison with ARPABET

Unlike ARPABET (used in LibriSpeech), IPA:
- Uses **Unicode symbols** (ð, θ, ʃ, ʒ) instead of two-letter codes (DH, TH, SH, ZH)
- More **phonetically precise** with diacritics
- **International standard** used across languages
- **Same structural format**: Both use space-separated phonemes with `|` word boundaries
- Example: "the cat" = `DH AH0 | K AE1 T` (ARPABET) vs `ð ʌ | k æ t` (IPA)

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled)
- **Dev**: From `dev` split
- **Test**: From `test` split

All splits contain phoneme sequences extracted from the ParaSpeechCaps dataset.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **VoxCeleb1/2**: Celebrity interviews (44.1 kHz)
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
- **Phonemes already in IPA format** - no conversion needed from source data.
- **Normalized format**: Phoneme sequences are space-separated Unicode IPA symbols with `|` marking word boundaries (matching ARPABET structure).
- The `text` field provides the original word-level transcription for reference.
- **Backup files**: Original files are backed up as `*.jsonl.gz.backup` before normalization.
- This is an **open-vocabulary** phoneme recognition task where target sequences vary by utterance.
- **Stress markers** (ˈ, ˌ) enable research on prosody and pronunciation variation.
- This is particularly valuable for:
  - **Phoneme recognition**: Training acoustic models for speech recognition
  - **Pronunciation modeling**: Analyzing phonetic patterns
  - **Low-level acoustic-phonetic analysis**: Understanding speech production
  - **Cross-linguistic research**: IPA is an international standard
  - **Speech synthesis**: Training TTS models with phonetic targets
- The dataset includes both human-annotated (PSC-Base) and automatically annotated (PSC-Scaled) samples in training.
- All audio files are verified for existence before inclusion.
- Phoneme counts typically range from ~10-30 phonemes per utterance depending on speech duration and rate.

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{paraspeechcaps2024,
  title={ParaSpeechCaps: A Large-Scale Corpus for Paralinguistic Speech Understanding},
  author={[Authors TBD]},
  booktitle={Proceedings of [Conference]},
  year={2024}
}
```

## References
- HuggingFace dataset: https://huggingface.co/datasets/ajd12342/paraspeechcaps
- International Phonetic Alphabet (IPA): https://www.internationalphoneticalphabet.org/
- 59 paralinguistic style tags covering diverse speaking characteristics
- Human-annotated (PSC-Base: 342 hours) and automatically annotated (PSC-Scaled: 2,427 hours) subsets
