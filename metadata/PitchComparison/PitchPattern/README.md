# PitchPattern

## Overview
**PitchPattern** is a synthetic dataset designed to evaluate audio models' ability to perceive and describe **temporal pitch patterns** in audio. The dataset contains **60,000 training samples** and **1,000 test samples**, each featuring one of **9 canonical pitch patterns** applied to audio sources. Each sample is annotated with a natural language description of the pitch pattern, enabling evaluation of both pattern recognition and natural language understanding of dynamic pitch changes.

The dataset includes 9 canonical pitch patterns:
- **Constant**: constant
- **Monotonic changes**: monotonic_increase, monotonic_decrease
- **Sudden changes**: sudden_increase, sudden_decrease
- **Composite patterns**: increase_then_decrease, decrease_then_increase
- **Periodic patterns**: regular_repetition, irregular_fluctuation

Audio sources span two types:
- **Synthetic Continuous**: Pure tones with swept/time-varying frequency
- **Synthetic Discrete**: Beep sequences at different pitches

All audio is sampled at **16 kHz** with durations ranging from **3-30 seconds**. Patterns are implemented through various methods: PureTone uses chirps and frequency modulation, and Beep uses sequences at different pitches.

## Supported Tasks
1. **Pitch Pattern Description** (Generate natural language description of the pattern)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 60,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **3-30 seconds**
- Average duration: **~12-18 seconds** (varies by pattern and source)
- Sampling rate: **16 kHz** for all audio files
- Pattern types: **9 canonical patterns**
- Pitch range: **A1 (55 Hz) to C7 (2093 Hz)** - musical range

### Pattern Type Distribution (Training Set)

Pattern distribution follows LoudnessPattern weighting (constant weighted higher):

| Pattern Type | Approximate % | Description |
|--------------|-------------:|-------------|
| constant | ~27% | Stable pitch level |
| monotonic_increase | ~9% | Gradual pitch rise (glissando up) |
| monotonic_decrease | ~9% | Gradual pitch fall (glissando down) |
| sudden_increase | ~9% | Abrupt pitch jump up |
| sudden_decrease | ~9% | Abrupt pitch drop down |
| increase_then_decrease | ~9% | Bell curve (pitch peak) |
| decrease_then_increase | ~9% | Valley curve (pitch dip) |
| regular_repetition | ~9% | Periodic pitch oscillation (vibrato/trill) |
| irregular_fluctuation | ~10% | Multiple irregular pitch changes |

### Source Type Distribution (Training Set)

| Source Type | # Samples | Percentage |
|-------------|----------:|-----------:|
| PureTone | 30,000 | 50.0% |
| Beep | 30,000 | 50.0% |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (format: `pattern_{split}_{id:06d}`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`PitchPattern`) |
| `type` | Pattern type (one of 9 canonical patterns) |
| `description` | Natural language description of the pitch pattern |
| `source_type` | Audio source type: `nsynth`, `puretone`, or `beep` |

---

## Example Entries

```json
{"id": "pattern_train_000000", "path": "/path/to/pattern_train_000000.wav", "sampling_rate": 16000, "duration": 21.21, "dataset": "PitchPattern", "type": "monotonic_decrease", "description": "The pitch generally becomes lower from the beginning toward the end, without a dominant abrupt drop.", "source_type": "nsynth"}

{"id": "pattern_train_000002", "path": "/path/to/pattern_train_000002.wav", "sampling_rate": 16000, "duration": 14.50, "dataset": "PitchPattern", "type": "constant", "description": "The pitch stays approximately stable across the clip, with only minor natural variation.", "source_type": "puretone"}

{"id": "pattern_train_000004", "path": "/path/to/pattern_train_000004.wav", "sampling_rate": 16000, "duration": 18.62, "dataset": "PitchPattern", "type": "monotonic_increase", "description": "The sound steadily rises in pitch as the clip progresses.", "source_type": "beep"}
```

---

## Task Usage

### 1. Pitch Pattern Description
- **Target field:** `description`
- **Task:** Generate natural language description of the pitch pattern
- **Evaluation**: Text similarity, semantic matching, or human evaluation

---

## Canonical Pitch Patterns

### 1. constant
- **Description**: Stable pitch with minor natural variation
- **PureTone**: Constant frequency sine/square/sawtooth/triangle wave
- **Beep**: Repeated beeps at the same pitch
- **Example descriptions**:
  - "The pitch stays approximately stable across the clip, with only minor natural variation."
  - "The clip maintains a nearly even pitch level from start to finish."

### 2. monotonic_increase
- **Description**: Gradual pitch rise (glissando upward)
- **PureTone**: Linear or exponential chirp upward
- **Beep**: 5-8 beeps with increasing pitch
- **Example descriptions**:
  - "The sound steadily rises in pitch as the clip progresses."
  - "A continuous upward pitch glide can be heard from start to finish."

### 3. monotonic_decrease
- **Description**: Gradual pitch fall (glissando downward)
- **PureTone**: Linear or exponential chirp downward
- **Beep**: 5-8 beeps with decreasing pitch
- **Example descriptions**:
  - "The pitch generally becomes lower from the beginning toward the end."
  - "A continuous downward pitch glide can be heard from start to finish."

### 4. sudden_increase
- **Description**: Abrupt pitch jump upward
- **PureTone**: Step function (low → high) with 50ms smooth transition
- **Beep**: Low pitch beeps → sudden jump → high pitch beeps
- **Example descriptions**:
  - "There is a sudden jump to a higher pitch partway through the audio."
  - "The pitch jumps sharply upward at a specific moment and then stays higher."

### 5. sudden_decrease
- **Description**: Abrupt pitch drop downward
- **PureTone**: Step function (high → low) with 50ms smooth transition
- **Beep**: High pitch beeps → sudden drop → low pitch beeps
- **Example descriptions**:
  - "The audio drops sharply from high to low pitch at a distinct point."
  - "A clear step-like decrease in pitch occurs once during the clip."

### 6. increase_then_decrease
- **Description**: Bell curve (pitch peak in middle)
- **PureTone**: Chirp up then down (piecewise linear frequency curve)
- **Beep**: Beeps rising to peak pitch, then falling
- **Example descriptions**:
  - "The pitch rises to a peak and then descends toward the end."
  - "The clip sounds like it glides up and then glides down in pitch."

### 7. decrease_then_increase
- **Description**: Valley curve (pitch dip in middle)
- **PureTone**: Chirp down then up (piecewise linear frequency curve)
- **Beep**: Beeps falling to valley pitch, then rising
- **Example descriptions**:
  - "The pitch broadly moves lower before returning to a higher level."
  - "The clip sounds like it glides down in pitch and then glides back up."

### 8. regular_repetition
- **Description**: Periodic pitch oscillation (vibrato/trill)
- **PureTone**: Frequency modulation (0.5-2 Hz vibrato)
- **Beep**: Regular alternation between 2-3 pitches
- **Example descriptions**:
  - "A rhythmic periodic variation in frequency can be heard throughout."
  - "The pitch repeatedly increases and decreases in a way that feels organized and periodic."

### 9. irregular_fluctuation
- **Description**: Irregular pitch changes (multiple components)
- **PureTone**: Multi-frequency FM (3-6 random frequency components)
- **Beep**: 8-15 beeps at random pitches
- **Example descriptions**:
  - "The pitch varies multiple times without following a simple up/down or repeating pattern."
  - "The pitch moves up and down multiple times without a stable rhythm or simple global shape."

---

## Audio Processing Pipeline

### PureTone Processing (Chirps and FM)

1. **Select waveform**: sine, square, sawtooth, or triangle
2. **Generate time-varying frequency**:
   - **Linear chirp**: Constant Hz/second rate
   - **Exponential chirp**: Constant musical interval rate
   - **Step functions**: Abrupt frequency changes with 50ms smoothing
   - **FM synthesis**: Frequency modulation for repetition/fluctuation
3. **Generate waveform** at 16 kHz
4. **Normalize** to -1 to 1 range

**Example (monotonic_increase with exponential chirp)**:
- f(t) = f₀ × k^t, where k = (f₁/f₀)^(1/duration)
- E.g., f₀ = 100 Hz, f₁ = 800 Hz over 10 seconds
- Sounds like constant musical interval rise

### Beep Processing (Discrete Sequences)

1. **Generate individual beeps**:
   - Duration: 200-400ms per beep
   - 10ms fade in/out to avoid clicks
   - Waveform: sine, square, sawtooth, or triangle
2. **Concatenate with silence**:
   - Silence between beeps: 100-200ms
3. **Sequence pitches** based on pattern
4. **Crop/pad** to target duration

**Example (regular_repetition)**:
- Alternate between 2 pitches (e.g., A3=220Hz and D4=293Hz)
- 6-12 cycles total
- Creates trill-like effect

---

## Implementation Details

### Pitch Range
- **Musical range**: A1 (55 Hz) to C7 (2093 Hz)
- Covers typical musical pitch perception range
- Avoids sub-bass (<55 Hz) and extreme high frequencies (>2093 Hz)

### PureTone Specifics
- **Chirp types**: Both linear and exponential (randomly selected)
- **Waveforms**: sine (pure), square (harmonic-rich), sawtooth (bright), triangle (mellow)
- **FM for repetition**: 0.5-2 Hz modulation frequency, 50-200 Hz depth
- **FM for irregular fluctuation**: 3-6 frequency components with random phases

### Beep Specifics
- **Duration per beep**: 200-400ms (randomly sampled)
- **Silence between beeps**: 100-200ms (randomly sampled)
- **Fade in/out**: 10ms to prevent click artifacts
- **Waveforms**: Same as PureTone (sine, square, sawtooth, triangle)

---

## Natural Language Descriptions

Each pattern has **15 different natural language descriptions** stored in `canonical_pitch_change_descriptions.csv`. For each sample, one description is randomly selected from the corresponding pattern type. Descriptions are adapted from LoudnessPattern by replacing loudness-related terms with pitch-related terms:

- "loudness"/"volume" → "pitch"/"frequency"
- "louder" → "higher (in pitch)"
- "quieter/softer" → "lower (in pitch)"
- "build/gain" → "rise"
- "fade/reduction" → "fall"

This provides linguistic diversity and tests models' ability to understand various phrasings of the same pitch concept.

---

## Source Datasets

### PureTone (50% of samples)
- **Source**: Synthesized on-the-fly
- **Format**: 16 kHz pure tones
- **Waveforms**: sine, square, sawtooth, triangle
- **Processing**: Chirps and frequency modulation

### Beep (50% of samples)
- **Source**: Synthesized on-the-fly
- **Format**: 16 kHz discrete beeps
- **Waveforms**: sine, square, sawtooth, triangle
- **Processing**: Beep sequences with varying pitch

---

## Generation Commands

### Generate Full Dataset
```bash
cd /home/tseng/FullSpectrumDataset/metadata/pitch/PitchPattern
/home/tseng/miniconda3/envs/DeSTA2/bin/python generate_manifest.py
```

This will generate:
- 60,000 training samples (30,000 per source type)
- 1,000 test samples (500 per source type)

### Test with Small Sample
```bash
/home/tseng/miniconda3/envs/DeSTA2/bin/python test_generation.py
```

This generates 6 samples (3 train, 3 test) for testing.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** (3-30 seconds) depending on pattern and source.
- The dataset is **fully synthetic** — both PureTone and Beep are synthesized on-the-fly.
- **Chirps** can be linear (constant Hz/s) or exponential (constant musical interval).
- The dataset evaluates:
  - **Temporal pitch perception**: Can models recognize dynamic pitch patterns?
  - **Pattern classification**: Can models distinguish between 9 pattern types?
  - **Natural language grounding**: Can models map pitch patterns to descriptions?
  - **Cross-source robustness**: Performance across pure tones and beeps
- **Pattern distribution** follows LoudnessPattern weighting with `constant` weighted higher (~27%).
- **Source distribution** is exactly 1:1 (equal across PureTone and Beep).
- Audio that fails processing or is too short (<3 seconds) is skipped and regenerated.
- This dataset complements **LoudnessPattern** by testing pitch perception rather than amplitude perception.
- The `description` field enables evaluation of audio-to-text generation and audio captioning models.
- Each pattern type has 15 linguistic variations to test robustness to different phrasings.
- **Pitch range** (55-2093 Hz) covers most musical applications while avoiding extreme frequencies.

---

## Comparison with LoudnessPattern

| Aspect | LoudnessPattern | PitchPattern |
|--------|----------------|--------------|
| **Acoustic dimension** | Amplitude (loudness) | Frequency (pitch) |
| **Patterns** | 9 canonical patterns | 9 canonical patterns (same structure) |
| **Sources** | Speech, Music, Synthetic | PureTone, Beep (fully synthetic) |
| **Processing** | Amplitude envelopes (windows) | Chirps, beep sequences |
| **Sample rate** | 16 kHz | 16 kHz |
| **Duration** | 3-30 seconds | 3-30 seconds |
| **Dataset size** | 60k train, 1k test | 60k train, 1k test |
| **Descriptions** | 15 variations per pattern | 15 variations per pattern (adapted) |

---

## Dependencies

Generation scripts require:
- numpy, soundfile, tqdm
- csv, json, gzip (standard library)

Install dependencies:
```bash
pip install numpy soundfile tqdm
```

---

## Authors & License

Created for the Full Spectrum Dataset project.
See main repository for license information.
