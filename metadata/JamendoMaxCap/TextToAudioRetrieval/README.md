# JamendoMaxCaps - Text-to-Audio Retrieval

## Overview
**JamendoMaxCaps Text-to-Audio Retrieval** is a benchmark dataset for evaluating text-to-audio retrieval models in the music domain. Built from the JamendoMaxCaps corpus, this dataset contains **85,226 carefully selected retrieval instances**, each pairing a textual music description with two audio candidates (one positive match and one negative distractor). This format supports contrastive learning and retrieval evaluation in music-language understanding systems.

The dataset is formulated as a **binary classification problem** where models must determine whether the first or second audio clip matches the given textual description. Audio clips are **30-second excerpts** sampled at **16 kHz** in **WAV format**.

## Supported Tasks
1. **Text-to-Audio Retrieval** — Given a music caption, select which of two audio clips matches the description

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 84,000 |
| test | 1,226 |

**Audio Characteristics:**
- Duration per clip: 30.0 seconds
- Sampling rate: 16 kHz (all clips)
- Clips per sample: 2 (one match + one distractor)

**Label Distribution:**
- Label 0 (first audio is correct): 42,521 samples (49.9%)
- Label 1 (second audio is correct): 42,705 samples (50.1%)
- **Balanced distribution** between both positions

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample identifier |
| `paths` | List of 2 audio file paths [audio1, audio2] |
| `sampling_rates` | List of 2 sampling rates (both 16000 Hz) |
| `durations` | List of 2 audio durations in seconds (both 30.0s) |
| `caption` | Text description of the music |
| `label` | Binary label: `0` if first audio matches, `1` if second audio matches |

---

## Example Entries

### Sample with label 0 (first audio is correct):
```json
{"id": "1748883_90", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_2/wavs/1748883_90.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_1/wavs/1499011_60.wav"], "sampling_rates": [16000, 16000], "durations": [30.0, 30.0], "caption": "The music in question is a slow-paced instrumental track with elements of jazz, soul, and R&B, set in A minor key with a tempo of around 80 BPM. The chord progression includes a rich blend of A minor, E major, D minor, and F major chords, creating a complex yet soothing soundscape. The genre is characterized as jazz, soul, and R&B, reflecting a smooth, melodic style that invites listeners to relax and unwind. The mood of the track is introspective, offering a sense of contemplation and depth. It's the type of music you might hear playing in the background at a coffee shop or during a quiet evening at home.", "label": 0}
```

### Sample with label 1 (second audio is correct):
```json
{"id": "1322526_opening_30s", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/909972.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/1322526.wav"], "sampling_rates": [16000, 16000], "durations": [30.0, 30.0], "caption": "The music is an instrumental track featuring a piano with a harp accompaniment, characterized by the genres easy listening, electronic, jazz, lounge, and soundtrack, presenting a mood akin to that of a musical movie set in London, with a time signature of 4/4 and a tempo of 136.0 bpm.", "label": 1}
```

---

## Task Usage

### 1. Text-to-Audio Retrieval
- **Input:** Text caption + 2 audio clips
- **Candidates:** `paths[0]` (first audio) and `paths[1]` (second audio)
- **Target field:** `label` (binary classification)
- **Task:** Predict which audio (0 or 1) matches the caption

**Task format:**
- **Query:** Music caption (text)
- **Candidates:** 2 audio clips (30 seconds each)
- **Goal:** Classify whether first (0) or second (1) audio matches the caption

**Evaluation:** Measured using **binary classification accuracy** or **audio retrieval metrics** (R@1, R@2).

---

## Label Space

### Binary Labels

<details>
<summary>Show 2 available labels:</summary>

`0` - First audio (paths[0]) matches the caption
`1` - Second audio (paths[1]) matches the caption

</details>

**Balanced distribution:** Both labels appear in approximately equal proportions (~50% each).

### Caption Characteristics

Captions provide rich descriptions covering multiple musical dimensions:

<details>
<summary>Show caption content categories:</summary>

**Musical Attributes:**
- **Genre:** jazz, rock, electronic, classical, ambient, hip-hop, etc.
- **Subgenre:** noise rock, glitch hop, orchestral, lounge, etc.
- **Key:** A minor, E minor, G major, Bb major, etc.
- **Tempo:** BPM (beats per minute), e.g., "80 BPM", "136.0 bpm"
- **Time signature:** 4/4, 3/4, 6/8, etc.
- **Chord progression:** Specific chord sequences

**Instrumentation:**
- Piano, guitar, drums, strings, brass, synthesizer
- Harp, marimba, glockenspiel, theremin
- Specific instrument combinations

**Mood & Atmosphere:**
- Introspective, uplifting, melancholic, aggressive
- Romantic, suspenseful, hopeful, dark
- Moody, energetic, calm, atmospheric

**Use Cases & Scenarios:**
- "suitable for a coffee shop"
- "perfect for wedding videos"
- "ideal for film or video game soundtrack"
- "background music for a rainy day"

**Style & Character:**
- Experimental, inspirational, cinematic
- Smooth, melodic, complex, sparse
- Fast-paced, slow-paced

</details>

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips are **30-second excerpts** from full Jamendo music tracks.
- Each sample contains **exactly 2 audio clips**: one correct match and one distractor.
- The dataset contains **~85,000 samples selected** from the larger JamendoMaxCaps corpus.
- The dataset is **perfectly balanced**: ~50% label 0, ~50% label 1.
- **Label randomization** ensures models cannot learn position bias (correct audio appears equally in both positions).
- **No dev/test splits** are provided; users should create their own evaluation splits.
- **Captions** are detailed, multi-attribute descriptions covering genre, mood, instrumentation, musical theory, and contextual use cases.
- **Distractor audio** is carefully selected to be a plausible alternative:
  - Often from similar genre or style
  - Provides challenging negative samples
  - Tests fine-grained music understanding
- The task evaluates **cross-modal understanding** between text and audio modalities.
- **Binary classification formulation**:
  - Simplifies retrieval as a pairwise comparison task
  - Models predict which of two audios matches the caption
  - Can be extended to ranking multiple candidates
- **Modeling challenges**:
  - **Fine-grained music understanding**: Distinguishing subtle differences in genre, mood, and style
  - **Musical knowledge**: Understanding tempo, key, chord progressions, and time signatures
  - **Cross-modal alignment**: Mapping textual descriptions to audio features
  - **Distractor discrimination**: Identifying correct match among similar-sounding music
  - **Multi-attribute matching**: Captions describe multiple dimensions simultaneously
- **Applications**:
  - Music search engines ("find music that sounds romantic and uplifting")
  - Query-by-description music retrieval
  - Music recommendation based on textual preferences
  - Music production and library management
  - Cross-modal music understanding
  - Audio-language model training
- **Training strategy**:
  - Binary classification objective (cross-entropy loss)
  - Can use contrastive learning approaches
  - Models learn to align text and audio embeddings
- **Model architectures** commonly used:
  - Dual-encoder models (separate text and audio encoders)
  - Cross-attention transformers
  - CLIP-style contrastive models
  - Audio-language pre-trained models
- **Evaluation approach**: Models compute similarity scores between the caption and both audio clips, then select the one with higher similarity. Performance is measured by accuracy of selecting the correct audio.
- **Evaluation metrics**: Accuracy, Mean Reciprocal Rank (MRR), Recall@K.

---

## Related Tasks

For other tasks using the JamendoMaxCaps dataset, see:
- [Music Captioning](../MusicCaptioning/README.md): Generate text descriptions from music audio
- [Audio-to-Text Retrieval](../AudioToTextRetrieval/README.md): Retrieve text descriptions from music audio

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{wu2023music,
  title={Music Understanding LLaMA: Advancing Text-to-Music Generation with Question Answering and Captioning},
  author={Wu, Shulei and others},
  booktitle={Proceedings of ISMIR},
  year={2023}
}
```

## References
- Jamendo music library: https://www.jamendo.com/
- JamendoMaxCaps: Large-scale music captioning corpus
- Audio clips licensed under Creative Commons
- Related to music information retrieval (MIR) and audio-language tasks
