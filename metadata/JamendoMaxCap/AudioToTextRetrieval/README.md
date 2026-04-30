# JamendoMaxCaps - Audio-to-Text Retrieval

## Overview
**JamendoMaxCaps Audio-to-Text Retrieval** is a benchmark dataset for evaluating audio-to-text retrieval models in the music domain. Built from the JamendoMaxCaps corpus, this dataset contains **85,226 carefully selected retrieval instances**, each pairing a 30-second music segment with one ground-truth caption and 1-2 distractor captions that describe different music. This format supports evaluation of music-language understanding and cross-modal retrieval systems.

The dataset is derived from the **Jamendo music library**, a platform for independent artists and Creative Commons music, with captions providing detailed descriptions of musical attributes such as genre, mood, instrumentation, tempo, key, chord progression, and suitable use cases.

## Supported Tasks
1. **Audio-to-Text Retrieval** — Given a music audio clip, select the correct caption from multiple candidates

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 84,000 |
| test | 1,226 |

**Audio Characteristics:**
- Average duration: ~29.2 seconds
- Duration range: 10.0s - 30.0s
- Sampling rate: 16 kHz (all clips)

**Retrieval Characteristics:**
- Distractors per sample: 1-2 (average: 1.5)
- Total candidates per sample: 2-3 (1 ground truth + distractors)

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique track identifier |
| `path` | Path to audio file (WAV) |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`JamendoMaxCaps`) |
| `ground_truth` | Correct caption describing the audio |
| `distractors` | List of incorrect captions (1-2 items) |

---

## Example Entries

### Sample with 2 distractors:
```json
{"id": "1748883_90", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_2/wavs/1748883_90.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "ground_truth": "The music in question is a slow-paced instrumental track with elements of jazz, soul, and R&B, set in A minor key with a tempo of around 80 BPM. The chord progression includes a rich blend of A minor, E major, D minor, and F major chords, creating a complex yet soothing soundscape. The genre is characterized as jazz, soul, and R&B, reflecting a smooth, melodic style that invites listeners to relax and unwind. The mood of the track is introspective, offering a sense of contemplation and depth. It's the type of music you might hear playing in the background at a coffee shop or during a quiet evening at home.", "distractors": ["This instrumental track is a blend of jazz and electronic music genres, set in E minor key with a tempo of 69 BPM. The chord progression includes E major, G# major, F# major, and A major, reflecting a complex musical structure. It's characterized by a 4/4 time signature and a piano playing the melody. The mood portrayed is moody yet upbeat, making it suitable for scenes that require an emotional depth while maintaining a lively atmosphere.", "The music is instrumental with a piano playing in the key of G minor. It follows a classical genre with an emotional mood, played at a tempo of 60.0 bpm in a 4/4 time signature. The description does not specify any particular scenario, but the mention of 'sad' suggests that the melody could be fitting for reflective or somber moments."]}
```

### Sample with 1 distractor:
```json
{"id": "316929_360", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_3/wavs/316929_360.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "ground_truth": "This music is an experimental instrumental piece with a noise rock genre, set in F# minor key and a tempo of around 89 BPM. It features a 4/4 time signature and includes sparse chords such as G major, C major, and D major. The mood portrayed seems to be dark and atmospheric, ideal for a film or video game soundtrack during intense scenes.", "distractors": ["This music is an experimental electronic track with a glitch hop genre, set in G minor key at a tempo of 132 BPM. It features a 4/4 time signature and includes chords like G major, F major, and E minor. The mood evoked is one of melancholy, suitable for a rainy day or a coffee shop atmosphere."]}
```

---

## Task Usage

### 1. Audio-to-Text Retrieval
- **Input:** Audio (music track) + list of candidate captions
- **Candidates:** `ground_truth` (correct) + `distractors` (incorrect)
- **Target:** Identify which caption correctly describes the audio
- **Evaluation:** Typically measured using **Recall@K** (R@1, R@5, R@10) and **Mean Reciprocal Rank (MRR)**

**Task format:**
- **Query:** Music audio clip (~30 seconds)
- **Candidates:** 2-3 text captions
- **Goal:** Select the correct caption from the candidate set

---

## Label Space

*This is a ranking/retrieval task with no predefined label vocabulary. The model must identify the correct caption among candidates.*

### Caption Characteristics

Captions provide rich descriptions covering multiple musical dimensions:

<details>
<summary>Show caption content categories:</summary>

**Musical Attributes:**
- **Genre:** jazz, rock, electronic, classical, ambient, hip-hop, etc.
- **Subgenre:** noise rock, glitch hop, orchestral, lounge, etc.
- **Key:** A minor, E minor, G major, Bb major, etc.
- **Tempo:** BPM (beats per minute), e.g., "80 BPM", "132 BPM"
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

**Caption length:**
- Highly detailed and descriptive
- Typically 50-200 words
- Multiple sentences covering different aspects

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips are **30-second excerpts** from full Jamendo music tracks (or shorter clips from 10-30 seconds).
- The dataset contains **~85,000 samples selected** from the larger JamendoMaxCaps corpus.
- **Captions** are detailed, multi-attribute descriptions covering genre, mood, instrumentation, musical theory, and contextual use cases.
- **Distractors** are carefully selected to be plausible alternatives:
  - Often share some attributes with the ground truth (e.g., similar genre or mood)
  - Provide challenging negative samples for retrieval models
  - Typically describe different tracks from the same or related genres
- The task evaluates **cross-modal understanding** between audio and text modalities.
- **No dev/test splits** are provided; users should create their own evaluation splits.
- **Modeling challenges**:
  - **Fine-grained music understanding**: Distinguishing subtle differences in genre, mood, and style
  - **Musical knowledge**: Understanding tempo, key, chord progressions, and time signatures
  - **Cross-modal alignment**: Mapping audio features to textual descriptions
  - **Negative sample discrimination**: Distinguishing ground truth from plausible distractors
  - **Multi-attribute matching**: Captions describe multiple dimensions simultaneously
- **Applications**:
  - Music recommendation systems
  - Music search and discovery
  - Automatic music tagging and organization
  - Music information retrieval (MIR)
  - Cross-modal music understanding
  - Audio-language model training
- **Retrieval metrics** commonly used:
  - **Accuracy (top-1)**: Fraction of queries where the correct caption is ranked first
  - **Mean Reciprocal Rank (MRR)**: Average of reciprocal ranks of correct captions
  - **Recall@K**: Fraction of queries where the correct caption appears in top-K results
  - **Median Rank**: Median position of correct caption in ranked list
- **Evaluation approach**: Models compute similarity scores between the audio and all candidate captions (ground_truth + distractors), then select the one with highest similarity. Performance is measured by how often the ground_truth caption is ranked first.

---

## Related Tasks

For other tasks using the JamendoMaxCaps dataset, see:
- [Music Captioning](../MusicCaptioning/README.md): Generate text descriptions from music audio
- [Text-to-Audio Retrieval](../TextToAudioRetrieval/README.md): Retrieve music from text descriptions

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
