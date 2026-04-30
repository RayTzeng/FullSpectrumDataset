# JamendoQA Music Captioning

## Overview
**JamendoQA Music Captioning** is a component of the Jamendo-QA benchmark, a large-scale dataset for music understanding built on freely licensed music from the Jamendo platform. This captioning task provides **7,335 full-length music tracks** paired with detailed, human-authored captions that describe comprehensive musical characteristics. Unlike shorter auto-generated captions, these descriptions provide in-depth analysis covering genre, tempo, key signature, instrumentation, production details, vocal characteristics, lyrical themes, song structure, and harmonic progressions. The dataset supports research in music captioning, multimodal audio-text learning, and music information retrieval.

## Supported Tasks
1. **Music Captioning**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 7,335 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique track identifier |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `caption` | Detailed natural language description of the music |

---

## Example Entries

```json
{"id": "accordion_AGeordieFarewell", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_AGeordieFarewell.wav", "sampling_rate": 16000, "duration": 205.69, "dataset": "JamendoQA", "caption": "This track is a Folk‑Rock/Acoustic‑Rock piece that blends earnest singer‑songwriter storytelling with a modest rock backbone.\nThe duration of the piece is 205.67 seconds. It moves at a steady 100 BPM in a 4/4 meter and is rooted in B minor, giving the song a wistful, minor‑toned foundation while the chord choices often lift into the relative major (D major) for moments of hopeful release.\n\n Instrumentation & production:  The arrangement is built around a warm, strummed acoustic guitar that carries the harmonic rhythm, a solid electric bass that anchors the low end, and a simple drum kit (kick, snare, hi‑hat) that provides a steady, unobtrusive pulse. The production is clean and natural, with a balanced stereo field that places the guitar slightly wide, the bass centered, and the drums panned modestly to create an intimate, "live‑room" feel. No heavy processing or synth layers are present; the mix emphasizes clarity and the organic timbres of the acoustic instruments.\n\n Vocals:  A male lead sings in a clear, slightly weathered baritone. His delivery is narrative and earnest, conveying a sense of longing and determination. The vocal track is treated with light reverb and gentle compression, preserving intimacy while adding a subtle sense of space.\n\n Lyrical themes:  The lyrics tell a story of departure and hope, focusing on leaving a restrictive homeland for a new life in America. The recurring chorus—"Sail away, sail away, sail away, sail away / Under a sky black with morning / In search of a New York morning"—encapsulates the central motif of escape and optimism. Verses reference "a new land is calling," "a ship bound for New York," and "goodbye to the old folks, the depression and dull," reinforcing the themes of exile, yearning, and the promise of a brighter future."}

{"id": "accordion_AGoodManPassing", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_AGoodManPassing.wav", "sampling_rate": 16000, "duration": 276.19, "dataset": "JamendoQA", "caption": "This track is a heartfelt Folk‑Rock ballad that blends acoustic folk storytelling with a gentle rock sensibility.\nThe duration of the piece is 266.17 seconds. It moves at a measured ≈ 90.9 BPM in a steady 4/4 meter and is rooted in B♭ major.\n\n Instrumentation & production:  The arrangement is built around a warm, finger‑picked acoustic guitar that carries the harmonic foundation, complemented by a melodic piano that adds lyrical counter‑lines. A subtle electric bass provides a supportive low end, while light, brushed drum patterns keep a soft pulse without overpowering the intimacy. The mix is clean and high‑fidelity, with a balanced stereo field that places the vocals front‑center and lets the acoustic instruments breathe. Minimal processing—just a touch of reverb—preserves the natural timbre of each element.\n\n Vocal characteristics:  A male baritone delivers the lyrics with a warm, clear, and expressive timbre. His delivery is gentle, narrative, and heartfelt, emphasizing the song's reflective tone. The vocal track is treated only with subtle reverb, keeping the performance intimate and direct.\n\n Lyrical themes:  The lyrics are a tribute to a departed friend, celebrating his kindness, wisdom, and enduring love. The recurring chorus reinforces the central message:\n\n*"For don't you know that love can never die?  \nIt goes on forever like the sky."*\n\nVerses recount memories ("I got the call… My oldest friend had passed and gone") and affirm the lasting impact of his spirit ("The soul is everlasting," "Smile for him and don't you cry").\n\n Song structure & dynamics:  The piece opens with a brief instrumental intro that establishes the chordal palette, then moves into a series of narrative verses. Each verse leads into the uplifting chorus, which repeats the central mantra. A bridge section appears midway, offering a slight lyrical and melodic variation before returning to the final choruses and a gentle outro that fades on the acoustic guitar. Dynamics remain consistently soft, with subtle swells in the choruses that add emotional lift without breaking the overall intimacy."}

{"id": "accordion_ALandCalledHome", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/JamendoQA/train/accordion_ALandCalledHome.wav", "sampling_rate": 16000, "duration": 186.6, "dataset": "JamendoQA", "caption": "This track is a melancholic Folk‑Rock piece that blends acoustic folk storytelling with a subtle rock backbone.\nThe duration of the piece is 206.57 seconds. It moves at a brisk 166.67 BPM and is rooted in F major, giving the song a bright tonal center that is constantly shaded by minor‑mode chords for emotional contrast.  \n\n Instrumentation & production:  The arrangement is built around a warm, finger‑picked acoustic guitar that carries the harmonic rhythm, a melodic electric bass that underpins the progression, and a light drum kit that provides a steady, understated pulse. The production is clean and natural, with a balanced stereo field that lets each instrument breathe; the mix emphasizes the acoustic guitar's resonance while keeping the bass and drums tight and unobtrusive.  \n\n Vocals:  A male lead sings in a clear, slightly melancholic timbre, delivering the lyrics in a narrative, storytelling style. The vocal delivery is clean, with modest reverb that adds depth without obscuring articulation.  \n\n Lyrical themes:  The lyrics explore a yearning for belonging and the pain of feeling "without a heart." The recurring chorus—"Home is where the heart is, but I'm a man without a heart. If I had a heart, girl, we'd have never come to part"—encapsulates the central motif of searching for a place to call home. Verses such as "I wandered streets of silent dread… Looking for a land called home" reinforce the theme of wandering and longing.  \n\n Song structure:  The composition follows a clear verse‑chorus format with instrumental breaks that allow the acoustic guitar to shine. Verses introduce the narrative, leading into the emotionally charged chorus; a brief instrumental interlude provides a reflective pause before the final choruses, which repeat the central hook to reinforce the song's melancholic resolve.  \n\n Theoretical grounding:  Harmonic movement frequently shifts from the tonic F to the subdominant Bb and the relative minor Gm, creating a wistful pull away from the home key. The progression often passes through C and Eb major chords, adding color and a sense of yearning before returning to F, which mirrors the lyrical search for resolution."}
```

---

## Task Usage

### 1. Music Captioning
- **Target field:** `caption` (detailed natural language music description)

---

## Label Space

*This is an open-vocabulary generation task without a predefined label space.*

### Caption Content Structure

The captions are comprehensive, human-authored descriptions that typically include:

1. **Genre Classification**: Folk-Rock, Acoustic-Rock, ballad, etc.
2. **Duration**: Exact track length in seconds
3. **Tempo & Meter**: BPM and time signature (e.g., "100 BPM in 4/4 meter")
4. **Key Signature**: Tonal center and modulations (e.g., "rooted in B minor, lifts to D major")
5. **Instrumentation & Production**: Detailed description of instruments, arrangement, mixing, stereo field, processing
6. **Vocal Characteristics**: Voice type, timbre, delivery style, processing (when vocals are present)
7. **Lyrical Themes**: Story, emotions, recurring motifs, quoted lyrics
8. **Song Structure**: Intro, verse, chorus, bridge, outro organization
9. **Harmonic Analysis**: Chord progressions, theoretical grounding, harmonic movement

---

## Notes
- All audio files are sampled at **16 kHz** in **WAV format**.
- Audio clips have **variable duration** ranging from **29 to 2,035 seconds** (average: ~233 seconds / ~3.9 minutes).
- Captions are **human-authored** with expert-level musical analysis, providing significantly more depth than auto-generated descriptions.
- The dataset contains **full-length music tracks** from the Jamendo platform (freely licensed Creative Commons).
- **No dev/test splits** are provided; users should create their own evaluation splits.
- Captions average **1,000-2,000 words** with structured sections covering multiple musical dimensions.
- This dataset emphasizes detailed, analytical descriptions suitable for training models to understand complex musical attributes.
- Audio is sourced from the **Jamendo music platform**, ensuring all content is freely licensed for research use.

---

## Related Tasks

For other tasks using the JamendoQA dataset, see:
- [Reasoning QA](../ReasoningQA/README.md): Question answering about music characteristics
