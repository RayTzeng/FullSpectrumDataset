# JamendoMaxCaps Music Captioning

## Overview
**JamendoMaxCaps** is a large-scale music captioning resource built from freely licensed instrumental tracks on the Jamendo platform, designed to support music-language understanding tasks such as retrieval, captioning, and multimodal representation learning. The dataset contains over **362,000 tracks** paired with generated natural-language captions and imputed metadata such as genre, tempo, mood, and instrumentation. Audio includes both **30-second segments** (opening clips and random segments) and **full-length songs** with variable durations. Captions provide rich, contextual descriptions covering musical characteristics including genre classification, key signature, tempo (BPM), time signature, chord progressions, instrumentation, mood, and suggested use cases.

## Supported Tasks
1. **Music Captioning**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 714,951 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment identifier (format: `{track_id}_{start_time}`, `{track_id}_opening_30s`, or `{track_id}_fullsong`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `caption` | Natural language description of the music |
| `source` | Audio source type (`raw`, `opening_30s`, or `full_song`) |

---

## Example Entries

```json
{"id": "1748883_90", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/raw/shard_2/wavs/1748883_90.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "caption": "The music in question is a slow-paced instrumental track with elements of jazz, soul, and R&B, set in A minor key with a tempo of around 80 BPM. The chord progression includes a rich blend of A minor, E major, D minor, and F major chords, creating a complex yet soothing soundscape. The genre is characterized as jazz, soul, and R&B, reflecting a smooth, melodic style that invites listeners to relax and unwind. The mood of the track is introspective, offering a sense of contemplation and depth. It's the type of music you might hear playing in the background at a coffee shop or during a quiet evening at home.", "source": "raw"}

{"id": "695133_opening_30s", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/opening_30s/695133.wav", "sampling_rate": 16000, "duration": 30.0, "dataset": "JamendoMaxCaps", "caption": "This music is characterized by an instrumental rock genre with elements of noise rock and psychedelic rock. It has a Spanish touch, played in E minor key at a tempo of around 130 BPM, featuring a complex chord progression and a 4/4 time signature. The mood evoked is one of suspense and intrigue, suitable for scenes involving mysterious landscapes or psychological thrillers.", "source": "opening_30s"}

{"id": "1009717_fullsong", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/JamendoMaxCaps/full_song/1009717.wav", "sampling_rate": 16000, "duration": 221.231063, "dataset": "JamendoMaxCaps", "caption": "The music is a fast-paced dub and reggae track in G major with a tempo of 143.55 BPM, featuring a 4/4 time signature. It includes a chord progression with G major, E minor, A minor, and D major chords and has a prominent reggae influence.", "source": "full_song"}
```

---

## Task Usage

### 1. Music Captioning
- **Target field:** `caption` (natural language music description)

---

## Label Space

*This is an open-vocabulary generation task without a predefined label space.*

### Caption Content Structure

The captions typically describe the following musical attributes:

1. **Genre**: Hip-hop, electronic, jazz, rock, pop, indie, experimental, soul, R&B, noise rock, psychedelic, etc.
2. **Key Signature**: E minor, A minor, F# minor, Bb major, etc.
3. **Tempo**: Specified in BPM (e.g., "around 80 BPM", "130 BPM")
4. **Time Signature**: Primarily 4/4, with occasional variations
5. **Chord Progressions**: Specific chord sequences (e.g., "A minor, E major, D minor, F major")
6. **Instrumentation**: Guitar, piano, synth, bass, drums, flute, strings, etc. (typically instrumental tracks)
7. **Mood/Atmosphere**: Introspective, suspenseful, energetic, chill, dark, dreamy, melancholic, upbeat, etc.
8. **Musical Characteristics**: Tempo descriptors (slow-paced, fast-paced), complexity (simple, complex chord progressions), style (melodic, rhythmic)
9. **Use Cases/Scenarios**: Coffee shop background music, festival music, movie soundtracks, video games, relaxing, working out, psychological thrillers, etc.

---

## Notes
- All audio files are sampled at **16 kHz** in **WAV format**.
- The dataset contains three types of audio sources:
  - **raw**: Random 30-second segments from various positions in tracks (`train_0` to `train_7`)
  - **opening_30s**: First 30 seconds of tracks (`train_0` to `train_7`)
  - **full_song**: Complete tracks with variable durations (66-221+ seconds) (`train_8`)
- The `id` format reflects the source type:
  - Random segments: `{track_id}_{start_time}` (e.g., "1748883_90")
  - Opening segments: `{track_id}_opening_30s` (e.g., "695133_opening_30s")
  - Full songs: `{track_id}_fullsong` (e.g., "1009717_fullsong")
- Captions are generated using automated methods combining metadata imputation and natural language generation.
- The dataset focuses on **instrumental music** from the Jamendo platform (freely licensed Creative Commons).
- Training set is distributed across **9 sharded files** (`train_0.jsonl.gz` through `train_8.jsonl.gz`).
- **No dev/test splits** are provided; users should create their own evaluation splits.
- Total: **714,951 samples** from over **362,000 unique tracks** (681,804 30-second segments + 33,147 full songs).

---

## Citation

If you use this dataset, please cite the JamendoMaxCaps paper:

```bibtex
@article{jamendo_maxcaps,
  title={JamendoMaxCaps: A Large-Scale Music Captioning Dataset},
  author={[Authors]},
  journal={[Journal/Conference]},
  year={[Year]}
}
```

---

## Related Tasks

For other tasks using the JamendoMaxCaps dataset, see:
- [Tempo Estimation](../TempoEstimation/README.md): BPM prediction from audio
- [Text-to-Audio Retrieval](../T2A/README.md): Retrieve music from text descriptions
- [Audio-to-Text Retrieval](../A2T/README.md): Retrieve text descriptions from music
