# NSynth

## Overview
**NSynth** is a large-scale collection of annotated musical notes created to support research on neural audio synthesis and music understanding. The dataset contains **305,979 four-second monophonic notes** sampled from **1,006 instruments**, with each note characterized by its **pitch**, **timbre**, and **envelope**. It includes comprehensive annotations such as instrument source, family, and sound qualities, making it suitable for musical instrument classification, pitch recognition, and sound production method analysis.

## Supported Tasks
1. **Musical Instrument Classification**
2. **Musical Note Classification**
3. **Sound Production Method Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 289,205 |
| dev | 12,678 |
| test | 4,096 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique note ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `pitch` | Musical pitch label (note name) |
| `instrument` | Instrument family label |
| `sound_production_method` | Sound production method |

---

## Example Entries

```json
{"id": "organ_electronic_100-048-025", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/NSynth/nsynth-train/audio/organ_electronic_100-048-025.wav", "duration": 4.0, "dataset": "NSynth", "pitch": "C3", "instrument": "organ", "sampling_rate": 16000, "sound_production_method": "electronic"}

{"id": "guitar_synthetic_006-081-050", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/NSynth/nsynth-train/audio/guitar_synthetic_006-081-050.wav", "duration": 4.0, "dataset": "NSynth", "pitch": "A5", "instrument": "guitar", "sampling_rate": 16000, "sound_production_method": "synthetic"}

{"id": "mallet_acoustic_001-077-127", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/NSynth/nsynth-train/audio/mallet_acoustic_001-077-127.wav", "duration": 4.0, "dataset": "NSynth", "pitch": "F5", "instrument": "mallet", "sampling_rate": 16000, "sound_production_method": "acoustic"}
```

---

## Task Usage

### 1. Musical Instrument Classification
- **Target field:** `instrument` (instrument family)

### 2. Musical Note Classification
- **Target field:** `pitch` (musical note)

### 3. Sound Production Method Classification
- **Target field:** `sound_production_method` (recording/synthesis method)

---

## Label Space

### Instruments
<details>
<summary>Show 11 available instrument families:</summary>

`bass`, `brass`, `flute`, `guitar`, `keyboard`, `mallet`, `organ`, `reed`, `string`, `synth_lead`, `vocal`

</details>

### Sound Production Methods
<details>
<summary>Show 3 available methods:</summary>

`acoustic`, `electronic`, `synthetic`

**Definitions:**
- **acoustic**: Traditional acoustic instruments recorded naturally
- **electronic**: Electronic instruments and synthesizers
- **synthetic**: Digitally synthesized sounds

</details>

### Musical Pitches
<details>
<summary>Show 88 available pitches (MIDI 21-108):</summary>

The dataset covers **88 musical pitches** spanning from **A0 to C8** (MIDI notes 21-108), corresponding to the full range of a standard piano keyboard.

**Octave 0:** `A0`, `A#0`, `B0`

**Octave 1:** `C1`, `C#1`, `D1`, `D#1`, `E1`, `F1`, `F#1`, `G1`, `G#1`, `A1`, `A#1`, `B1`

**Octave 2:** `C2`, `C#2`, `D2`, `D#2`, `E2`, `F2`, `F#2`, `G2`, `G#2`, `A2`, `A#2`, `B2`

**Octave 3:** `C3`, `C#3`, `D3`, `D#3`, `E3`, `F3`, `F#3`, `G3`, `G#3`, `A3`, `A#3`, `B3`

**Octave 4:** `C4`, `C#4`, `D4`, `D#4`, `E4`, `F4`, `F#4`, `G4`, `G#4`, `A4`, `A#4`, `B4`

**Octave 5:** `C5`, `C#5`, `D5`, `D#5`, `E5`, `F5`, `F#5`, `G5`, `G#5`, `A5`, `A#5`, `B5`

**Octave 6:** `C6`, `C#6`, `D6`, `D#6`, `E6`, `F6`, `F#6`, `G6`, `G#6`, `A6`, `A#6`, `B6`

**Octave 7:** `C7`, `C#7`, `D7`, `D#7`, `E7`, `F7`, `F#7`, `G7`, `G#7`, `A7`, `A#7`, `B7`

**Octave 8:** `C8`

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Each note is exactly **4 seconds** long.
- All notes are **monophonic** (single note, not chords).
- This is a **single-label** classification task for each target field.
- The dataset contains notes from **1,006 different instruments** across 11 instrument families.
- Sound production methods indicate the recording or synthesis technique:
  - **Acoustic**: Natural recordings of physical instruments
  - **Electronic**: Electronically generated sounds
  - **Synthetic**: Computationally synthesized audio
- The dataset is particularly valuable for:
  - **Neural audio synthesis**: Training generative models for music creation
  - **Instrument recognition**: Identifying instrument types from audio
  - **Pitch detection**: Recognizing musical notes and frequencies
- NSynth was created by Google's Magenta team for music and audio research.
