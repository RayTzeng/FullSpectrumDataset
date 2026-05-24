# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Word-Level Duration Analysis**, providing word-level timing information extracted from Montreal Forced Aligner (MFA) alignments for prosody and speech timing research.

## Supported Tasks
1. **Word-Level Duration Analysis**

---

## Dataset Statistics

| Split | # Samples | Duration Range | Avg Duration | Avg Words/Utterance | Word Count Range | Avg Word Duration |
|-------|-----------|----------------|--------------|---------------------|------------------|-------------------|
| train | 102,750 | 2.0s - 30.0s | 9.5s | 29.8 | 1 - 136 | 0.260s |
| test | 1,605 | 2.0s - 30.0s | 7.4s | 18.9 | 1 - 115 | 0.300s |

**Total**: 104,355 utterances with word-level alignments (filtered to ≤30s duration)

**Filtering applied**:
- Original total: 104,805 utterances
- Removed: 450 utterances (>30s duration, ranging 30.1s - 145.2s)
- Kept: 104,355 utterances (99.6% retention rate)

**Breakdown by source corpus (train)**:
- **Emilia**: ~79,000 samples (77%)
- **EARS**: ~12,600 samples (12%)
- **expresso**: ~11,000 samples (11%)

*Note: Test split has no samples because it contains only voxceleb audio, which currently has no MFA alignments available.*

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique audio identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (44100 or 48000 Hz) |
| `duration` | Audio duration (seconds) |
| `dataset` | Dataset name |
| `words` | List of words in sequential order |
| `word_durations` | List of word durations (seconds) corresponding to each word |

---

## Example Entries

```json
{"id": "EARS_audio_p002_emo_sadness_sentences", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p002/emo_sadness_sentences.wav", "sampling_rate": 48000, "duration": 10.8, "dataset": "ParaSpeechCaps", "words": ["i", "am", "so", "upset", "by", "the", "state", "of", "the", "world", "i", "hope", "it", "gets", "better", "soon", "i", "really", "miss", "her", "life", "isn't", "the", "same", "without", "her", "i'm", "sorry", "for", "your", "loss"], "word_durations": [0.12, 0.15, 0.29, 0.31, 0.14, 0.09, 0.25, 0.09, 0.08, 0.43, 0.08, 0.22, 0.05, 0.18, 0.28, 0.46, 0.08, 0.25, 0.26, 0.3, 0.25, 0.21, 0.13, 0.27, 0.37, 0.29, 0.14, 0.38, 0.16, 0.13, 0.54]}

{"id": "EARS_audio_p037_sentences_05_loud", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p037/sentences_05_loud.wav", "sampling_rate": 48000, "duration": 13.1, "dataset": "ParaSpeechCaps", "words": ["in", "fact", "the", "count's", "face", "brightened", "for", "god's", "sake", "talk", "to", "her", "in", "what", "an", "amiable", "light", "does", "this", "place", "him", "take", "me", "out", "of", "my", "way", "i", "heard", "many", "things", "in", "hell"], "word_durations": [0.22, 0.57, 0.16, 0.44, 0.34, 0.72, 0.13, 0.38, 0.55, 0.42, 0.13, 0.35, 0.19, 0.19, 0.1, 0.57, 0.28, 0.29, 0.18, 0.32, 0.34, 0.33, 0.12, 0.15, 0.1, 0.16, 0.46, 0.13, 0.21, 0.26, 0.37, 0.13, 0.47]}

{"id": "EN_B00008_S00783_W000290", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/Emilia/data/ea5a63b30fe727692c098f56079e8e3ab36c7d7142341750d411471a22efcc23/EN_B00008_S00783_W000290.mp3", "sampling_rate": 24000, "duration": 18.319, "dataset": "ParaSpeechCaps", "words": ["and", "she's", "like", "okay", "she's", "trying", "to", "play", "this", "game", "with", "him", "actually", "so", "it", "was", "an", "equal", "back", "and", "forth", "game", "with", "previous", "relationship", "and", "i", "know", "inside", "information", "that", "she", "was", "playing", "it", "was", "a", "game", "a", "child's", "game", "and", "uhm", "she", "got", "ready", "and", "about", "to", "leave", "and", "i", "said", "hey", "listen", "uhm", "you", "know", "i", "like", "you", "i", "like", "spending", "time", "with", "you", "but", "uhm"], "word_durations": [0.1, 0.08, 0.09, 0.25, 0.3, 0.23, 0.05, 0.09, 0.11, 0.18, 0.11, 0.08, 0.26, 0.24, 0.05, 0.25, 0.23, 0.21, 0.17, 0.09, 0.17, 0.17, 0.2, 0.59, 0.84, 0.13, 0.03, 0.15, 0.29, 0.5, 0.14, 0.15, 0.12, 0.25, 0.17, 0.11, 0.07, 0.19, 0.04, 0.17, 0.13, 0.09, 0.6, 0.1, 0.33, 0.35, 0.18, 0.18, 0.07, 0.19, 0.2, 0.09, 0.24, 0.11, 0.3, 0.25, 0.09, 0.07, 0.08, 0.26, 0.1, 0.03, 0.14, 0.32, 0.09, 0.1, 0.08, 0.36, 0.5]}
```

---

## Task Usage

### 1. Word-Level Duration Analysis
- **Input field:** Audio
- **Target fields:** `words` (word sequence), `word_durations` (timing for each word)
- **Use cases:**
  - Prosody analysis and modeling
  - Speech rate analysis
  - Speaking style characterization
  - Duration prediction for TTS systems
  - Forensic speech analysis
  - Speech timing disorders detection

---

## Label Space

*This is an open-vocabulary task where both the word sequence and durations vary by utterance.*

### Word Duration Characteristics

Word durations are provided in **seconds** with 4 decimal places of precision:

- **Short function words**: Articles (a, the), pronouns (I, you), prepositions (to, of) typically 0.05-0.20s
- **Medium content words**: Common nouns, verbs, adjectives typically 0.20-0.50s
- **Long words**: Multi-syllabic words, emphasized words typically 0.50-2.00s
- **Speaking rate variation**: Same word can have different durations depending on:
  - Emotion (e.g., anxious = faster, sleepy = slower)
  - Emphasis and stress patterns
  - Position in utterance (final words often lengthened)
  - Speaker characteristics (accent, age, gender)

### Alignment Source

All word-level alignments are generated using **Montreal Forced Aligner (MFA)**:
- **Aligner**: MFA 2.x or 3.x
- **Acoustic model**: English pretrained model
- **Dictionary**: English pronunciation dictionary
- **Alignment granularity**: Word-level boundaries (Begin, End timestamps)
- **Quality**: High-quality forced alignments with manual verification on subset

---

## Train/Test Split

This manifest uses the standard ParaSpeechCaps splits:

- **Train**: Combined from `train_base` (PSC-Base) + `train_scaled` (PSC-Scaled)
- **Dev**: From `dev` split
- **Test**: From `test` split

**Coverage by source corpus:**
- ✓ **expresso**: Full MFA alignment coverage
- ✓ **EARS**: Full MFA alignment coverage
- ✓ **emilia**: Full MFA alignment coverage
- ✗ **voxceleb1/2**: No MFA alignments available (excluded from this task)

Only utterances with available MFA word-level alignments are included in the manifests.

---

## Notes
- All audio files are sampled at **44.1 kHz or 48 kHz** depending on the source corpus.
- Audio files are stored in **WAV or MP3 format** depending on source.
- Audio clips have **variable duration**, typically ranging from 2-15 seconds.
- The dataset combines multiple source corpora:
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional speech from audiobooks (44.1 kHz)
- **Word alignments** are extracted from MFA CSV files containing:
  - Begin/End timestamps for each word
  - Word labels in lowercase
  - Speaker information
- **Word durations** are calculated as `End - Begin` in seconds
- **Silence/pauses** between words are NOT included in word durations
- This task is particularly valuable for:
  - **Prosody modeling**: Understanding speech rhythm and timing
  - **TTS duration modeling**: Training duration predictors for speech synthesis
  - **Speech rate analysis**: Measuring speaking speed variations
  - **Emotion-timing correlation**: Analyzing how emotions affect speech timing
  - **Accent analysis**: Studying timing differences across accents
  - **Speech disorders**: Detecting abnormal timing patterns
- The large-scale nature (100K+ aligned utterances) enables robust statistical analysis of word duration patterns across different speaking styles
- All MFA alignments are stored separately in `/saltpool0/data/mfa_alignments_ray/`
- The manifest generation script automatically maps audio files to their corresponding alignment CSVs
- **Duration filtering**: All utterances longer than 30 seconds have been filtered out to focus on typical speech segments
  - Original unfiltered backups are saved as `*.jsonl.gz.backup_unfiltered`
  - Filter script available: [filter_duration.py](filter_duration.py)
  - 450 long utterances removed (0.4% of total), ranging from 30.1s to 145.2s
  - Longest kept utterance: 30.0s (136 words)
  - Total words in dataset: **3,063,326** across all utterances

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
- Montreal Forced Aligner (MFA): https://montreal-forced-aligner.readthedocs.io/
- 59 paralinguistic style tags covering diverse speaking characteristics
- Human-annotated (PSC-Base: 342 hours) and automatically annotated (PSC-Scaled: 2,427 hours) subsets
