# ParaSpeechCaps

## Overview
**ParaSpeechCaps** is a large-scale speech corpus annotated with rich paralinguistic style captions that describe *how* something is spoken rather than just *what* is said. The dataset covers **59 style tags** spanning both intrinsic speaker traits (gender, pitch, accent, voice quality) and utterance-level situational styles (speed, articulation, emotion, environment). It includes a **342-hour human-annotated subset (PSC-Base)** and a **2,427-hour automatically annotated subset (PSC-Scaled)**. Audio is sourced from multiple corpora including VoxCeleb1/2, EARS, and Expresso, with sampling rates of **44.1 kHz or 48 kHz** depending on the source. This manifest focuses on **Word-Level Loudness Analysis**, providing word-level RMS loudness measurements (in dBFS) extracted from audio for prosody and speech dynamics research.

## Supported Tasks
1. **Word-Level Loudness Analysis**
2. **Speech Dynamics and Prosody Research**
3. **Loudness Modeling for TTS**

---

## Dataset Statistics

| Split | # Samples | Duration Range | Avg Duration | Avg Words/Utterance | Word Count Range | Avg Word Loudness | Silent Words |
|-------|-----------|----------------|--------------|---------------------|------------------|-------------------|--------------|
| train | 102,750 | 2.0s - 30.0s | 9.5s | 29.8 | 1 - 136 | -22.2 dBFS | 0.00% |
| test | 1,605 | 2.0s - 30.0s | 7.4s | 18.9 | 1 - 115 | -20.0 dBFS | 0.00% |

**Total**: 104,355 utterances with word-level loudness (filtered to ≤30s duration)

**Filtering applied**:
- Original total: 1,041,167 entries loaded
- Successfully processed: 104,355 entries (10.0%)
- Filtered by duration (>30s): 341 entries
- No alignment found: 936,471 entries (mostly voxceleb without MFA alignments)

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
| `word_loudness` | List of word loudness values (RMS dBFS) corresponding to each word |

---

## Example Entries

```json
{"id": "EARS_audio_p030_rainbow_08_slow", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p030/rainbow_08_slow.wav", "sampling_rate": 48000, "duration": 24.0, "dataset": "ParaSpeechCaps", "words": ["if", "the", "red", "of", "the", "second", "bow", "falls", "upon", "the", "green", "of", "the", "first", "the", "result", "is", "to", "give", "a", "bow", "with", "an", "abnormally", "wide", "yellow", "band", "since", "red", "and", "green", "light", "when", "mixed", "form", "yellow", "this", "is", "a", "very", "common", "type", "of", "bow", "one", "showing", "mainly", "red", "and", "yellow", "with", "little", "or", "no", "green", "or", "blue"], "word_loudness": [-20.85, -16.38, -15.13, -19.13, -16.71, -20.39, -16.46, -15.41, -18.41, -17.8, -18.21, -21.07, -18.62, -23.25, -16.28, -18.44, -21.33, -19.74, -19.65, -17.96, -18.7, -23.01, -16.96, -18.16, -17.62, -19.61, -25.26, -21.5, -19.07, -20.28, -17.49, -19.79, -17.97, -22.29, -17.45, -21.77, -22.43, -16.9, -24.04, -17.43, -18.79, -21.08, -19.15, -22.86, -18.55, -18.32, -18.58, -19.87, -18.92, -21.21, -24.4, -18.03, -20.59, -15.29, -17.34, -17.62, -25.52]}

{"id": "EARS_audio_p015_sentences_02_fast", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p015/sentences_02_fast.wav", "sampling_rate": 48000, "duration": 12.9, "dataset": "ParaSpeechCaps", "words": ["it", "might", "happen", "he", "added", "with", "an", "involuntary", "smile", "it", "is", "sold", "sir", "was", "again", "his", "laconic", "reply", "and", "you", "must", "have", "some", "water", "my", "dear", "fellow", "what", "is", "that", "flying", "about", "who", "wants", "a", "dead", "cert", "for", "the", "gold", "cup"], "word_loudness": [-20.34, -12.88, -17.58, -20.49, -18.5, -23.36, -20.76, -19.34, -22.18, -24.01, -20.25, -21.05, -19.63, -22.69, -19.66, -23.17, -19.93, -18.77, -23.02, -16.86, -15.92, -17.7, -17.98, -15.63, -18.19, -19.39, -18.57, -23.69, -22.2, -18.16, -20.75, -17.95, -22.18, -20.5, -18.8, -19.53, -23.01, -21.74, -22.51, -20.02, -23.01]}

{"id": "EARS_audio_p036_emo_pain_freeform", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/ParaSpeechCaps/EARS/audio/p036/emo_pain_freeform.wav", "sampling_rate": 48000, "duration": 5.2, "dataset": "ParaSpeechCaps", "words": ["ouch", "gosh", "my", "toe", "it", "really", "hurt"], "word_loudness": [-19.41, -21.89, -22.86, -21.38, -23.51, -18.7, -22.71]}
```

---

## Task Usage

### 1. Word-Level Loudness Analysis
- **Input field:** Audio
- **Target fields:** `words` (word sequence), `word_loudness` (RMS dBFS loudness for each word)
- **Use cases:**
  - Speech dynamics and prosody analysis
  - Loudness variation modeling
  - Emphasis detection
  - Energy distribution patterns
  - Loudness-aware TTS systems
  - Speech modification and enhancement
  - Emotional expression analysis (loudness-emotion correlation)

---

## Label Space

*This is an open-vocabulary task where both the word sequence and loudness values vary by utterance.*

### Word Loudness Characteristics

Word loudness is provided in **RMS dB (dBFS - decibels relative to full scale)**:

- **RMS dB metric**: Root Mean Square amplitude converted to decibels
  - Formula: `20 * log10(RMS_amplitude)`
  - Reference: Full scale (1.0), so 0 dB = maximum possible amplitude
  - Simple, interpretable measure of signal energy
  - Widely used in audio processing and speech analysis

- **Loudness ranges**:
  - **Very quiet words**: -40 to -30 dBFS (whispers, unstressed syllables)
  - **Quiet words**: -30 to -25 dBFS (soft speech)
  - **Normal words**: -25 to -15 dBFS (typical conversational speech)
  - **Loud words**: -15 to -10 dBFS (emphasized words, shouting)
  - **Very loud/clipped**: -10 to 0 dBFS (very loud speech, possible clipping)
  - **Silent/near-silent**: -80 dBFS (silence floor marker)

- **Silent word handling**:
  - Words with negligible energy (RMS < 1e-6) are marked as -80 dB
  - Very short segments (<10 samples) are marked as -80 dB
  - Values below -80 dB are clamped to -80 dB floor
  - Nearly 0% silent words in this dataset (actual speech energy captured)

- **Loudness variation factors**: Same word can have different loudness depending on:
  - **Emotion**: Angry/excited = louder, sad/calm = quieter
  - **Emphasis**: Stressed words have higher loudness
  - **Position**: Final words may be quieter
  - **Speaking style**: Shouting vs. whispering
  - **Recording conditions**: Microphone distance, environment

### Alignment Source

All word-level boundaries are extracted using **Montreal Forced Aligner (MFA)**:
- **Aligner**: MFA 2.x or 3.x
- **Acoustic model**: English pretrained model
- **Dictionary**: English pronunciation dictionary
- **Alignment granularity**: Word-level boundaries (Begin, End timestamps)
- **Loudness extraction**: LUFS calculated for audio segment between Begin-End timestamps

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
- Audio clips have **variable duration**, filtered to maximum 30 seconds.
- The dataset combines multiple source corpora:
  - **EARS**: Emotional acted speech (48 kHz)
  - **Expresso**: Expressive read speech (48 kHz)
  - **Emilia**: Emotional speech from audiobooks (44.1 kHz)
- **Word alignments** are extracted from MFA CSV files containing:
  - Begin/End timestamps for each word
  - Word labels in lowercase
  - Speaker information
- **Word loudness** is calculated using:
  - **RMS dB (dBFS)**: Root Mean Square amplitude in decibels
  - **Formula**: `20 * log10(RMS)` where RMS = `sqrt(mean(audio_segment^2))`
  - **Audio segment extraction**: Using MFA Begin/End timestamps
  - **Silence floor**: -80 dB for words with negligible energy (RMS < 1e-6)
- **Silence/pauses** between words are NOT included in word loudness calculations
- **Nearly 0% silent words**:
  - All words have measurable energy (>1e-6 RMS)
  - Reflects actual speech content from MFA alignments
  - Natural variation in loudness captured across all words
- This task is particularly valuable for:
  - **Prosody modeling**: Understanding speech emphasis and dynamics
  - **Loudness-aware TTS**: Training loudness predictors for natural speech synthesis
  - **Emphasis detection**: Identifying stressed/emphasized words
  - **Emotion-loudness correlation**: Analyzing how emotions affect speech loudness
  - **Speech modification**: Loudness normalization and enhancement
  - **Speaking style analysis**: Differentiating whispering, normal, and loud speech
- The large-scale nature (100K+ aligned utterances) enables robust statistical analysis of loudness patterns
- All MFA alignments are stored separately in `/saltpool0/data/mfa_alignments_ray/`
- The manifest generation script automatically maps audio files to their corresponding alignment CSVs
- **Duration filtering**: All utterances longer than 30 seconds have been filtered out
  - 341 entries filtered for duration > 30s
  - 104,355 entries kept (10% of loaded entries)
  - Longest kept utterance: 30.0s (136 words)
  - Total words in dataset: **3,093,660** across all utterances
  - Average word loudness: **-22.2 dBFS** (train), **-20.0 dBFS** (dev)

---

## Technical Details

### RMS dB Calculation Method
```python
import numpy as np
import soundfile as sf

# Load audio
audio, sr = sf.read(audio_path, dtype='float32')

# Convert to mono if stereo
if len(audio.shape) > 1:
    audio = np.mean(audio, axis=1)

# Extract word segment using MFA timestamps
begin_sample = int(begin_time * sr)
end_sample = int(end_time * sr)
segment = audio[begin_sample:end_sample]

# Calculate RMS
rms = np.sqrt(np.mean(segment ** 2))

# Convert to dB (reference is full scale = 1.0)
if rms >= 1e-6:
    loudness_db = 20 * np.log10(rms)
    # Clamp to floor value
    loudness_db = max(loudness_db, -80.0)
else:
    loudness_db = -80.0  # Silence floor
```

### Processing Pipeline
1. Load MFA word alignments (Begin/End timestamps)
2. Load audio file
3. For each word:
   - Extract audio segment based on timestamps
   - Calculate RMS amplitude
   - Convert to dB: `20 * log10(RMS)`
   - Apply silence floor (-80 dB) if RMS < 1e-6 or dB < -80
4. Store words + word_loudness arrays

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
- RMS dB calculation: Standard audio amplitude measurement
- 59 paralinguistic style tags covering diverse speaking characteristics
- Human-annotated (PSC-Base: 342 hours) and automatically annotated (PSC-Scaled: 2,427 hours) subsets
