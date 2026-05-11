# LoudnessComparison - LoudnessPattern

## Overview
**LoudnessComparison-LoudnessPattern** is a synthetic dataset designed to evaluate audio models' ability to perceive and describe **temporal loudness patterns** in audio. The dataset contains **60,000 training samples** and **1,000 test samples**, each featuring one of **9 active canonical loudness patterns** applied to clean audio sources. Each sample is annotated with a natural language description of the loudness pattern, enabling evaluation of both pattern recognition and natural language understanding of dynamic loudness changes.

The dataset includes 9 active canonical loudness patterns:
- **Constant**: constant
- **Monotonic changes**: monotonic_increase, monotonic_decrease
- **Sudden changes**: sudden_increase, sudden_decrease
- **Composite patterns**: increase_then_decrease, decrease_then_increase
- **Periodic patterns**: regular_repetition, irregular_fluctuation

Audio sources span three domains:
- **Speech**: LibriSpeech audiobook recordings
- **Music**: Slakh2100 instrument stems (8 instrument types)
- **Synthetic**: Pure tones and noise (white/pink/brown)

All audio is sampled at **16 kHz** with durations ranging from **3-30 seconds**. Patterns are implemented as time-varying amplitude envelopes (window functions) applied to the source audio, providing clean and reproducible loudness dynamics.

## Supported Tasks
1. **Loudness Pattern Description** (Generate natural language description of the pattern)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 60,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **3-30 seconds**
- Average duration: **~12-15 seconds**
- Sampling rate: **16 kHz** for all audio files
- Pattern types: **9 active canonical patterns**

### Pattern Type Distribution (Training Set)

| Pattern Type | # Samples | Description |
|--------------|----------:|-------------|
| constant | 16,399 | Stable loudness level |
| monotonic_decrease | 5,521 | Gradual decrease from loud to quiet |
| decrease_then_increase | 5,503 | Valley curve (dip in middle) |
| sudden_decrease | 5,485 | Abrupt step from loud to quiet |
| irregular_fluctuation | 5,471 | Multiple frequency components |
| sudden_increase | 5,455 | Abrupt step from quiet to loud |
| regular_repetition | 5,400 | Periodic oscillation |
| increase_then_decrease | 5,385 | Bell curve (peak in middle) |
| monotonic_increase | 5,381 | Gradual increase from quiet to loud |

### Source Type Distribution (Training Set)

| Source Type | # Samples |
|-------------|----------:|
| speech | 23,398 |
| noise | 12,298 |
| pure_tone | 12,197 |
| music | 12,107 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (format: `pattern_{split}_{id:06d}`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`LoudnessPattern`) |
| `type` | Pattern type (one of 9 active canonical patterns) |
| `description` | Natural language description of the loudness pattern |
| `source_type` | Audio source type: `speech`, `music`, `pure_tone`, or `noise` |

---

## Example Entries

```json
{"id": "pattern_train_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/pattern_train_000000.wav", "sampling_rate": 16000, "duration": 3.6, "dataset": "LoudnessPattern", "type": "sudden_decrease", "description": "A clear step-like decrease in loudness occurs once during the clip.", "source_type": "music"}

{"id": "pattern_train_000001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/pattern_train_000001.wav", "sampling_rate": 16000, "duration": 14.44, "dataset": "LoudnessPattern", "type": "constant", "description": "The audio has a stable level, with no meaningful dynamic contour.", "source_type": "noise"}

{"id": "pattern_train_000002", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/pattern_train_000002.wav", "sampling_rate": 16000, "duration": 12.35, "dataset": "LoudnessPattern", "type": "constant", "description": "The signal stays close to the same loudness level for the entire clip.", "source_type": "speech"}

{"id": "pattern_train_000003", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/pattern_train_000003.wav", "sampling_rate": 16000, "duration": 15.45, "dataset": "LoudnessPattern", "type": "regular_repetition", "description": "The loudness changes form a pattern that repeats instead of occurring randomly.", "source_type": "music"}

{"id": "pattern_train_000004", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/pattern_train_000004.wav", "sampling_rate": 16000, "duration": 3.15, "dataset": "LoudnessPattern", "type": "monotonic_increase", "description": "The sound becomes louder over time rather than remaining flat or reversing direction.", "source_type": "music"}
```

---

## Task Usage

### 1. Loudness Pattern Description
- **Target field:** `description`
- **Task:** Generate natural language description of the loudness pattern
- **Evaluation**: Text similarity, semantic matching, or human evaluation

---

## Canonical Loudness Patterns

### 1. constant
- **Description**: Stable loudness with minor natural variation
- **Window function**: Nearly flat (1.0) with small random variations (±2%)
- **Example descriptions**:
  - "The audio has a stable level, with no meaningful dynamic contour."
  - "Loudness remains mostly constant throughout, without obvious ramps or peaks."

### 2. monotonic_increase
- **Description**: Gradual increase from quiet to loud
- **Window function**: Linear ramp from 0.05 to 1.0
- **Example descriptions**:
  - "The sound becomes louder over time rather than remaining flat or reversing direction."
  - "There is a steady crescendo throughout the duration of the clip."

### 3. monotonic_decrease
- **Description**: Gradual decrease from loud to quiet
- **Window function**: Linear ramp from 1.0 to 0.05
- **Example descriptions**:
  - "The clip starts at a higher volume and gradually fades to a quieter level."
  - "A continuous decrescendo can be heard from start to finish."

### 4. sudden_increase
- **Description**: Abrupt step from quiet to loud
- **Window function**: Step function (0.05 → 1.0) with 1-second smooth transition
- **Example descriptions**:
  - "There is a sudden jump to a louder level partway through the audio."
  - "The loudness shifts abruptly upward once, from soft to loud."

### 5. sudden_decrease
- **Description**: Abrupt step from loud to quiet
- **Window function**: Step function (1.0 → 0.05) with 1-second smooth transition
- **Example descriptions**:
  - "A clear step-like decrease in loudness occurs once during the clip."
  - "The audio drops sharply from loud to soft at a distinct point."

### 6. increase_then_decrease
- **Description**: Bell curve (peak in middle)
- **Window function**: Piecewise linear (ramp up to peak at 40-60%, then ramp down)
- **Example descriptions**:
  - "The clip builds to a peak and then tapers off toward the end."
  - "Loudness rises to a maximum somewhere in the middle, then falls back."

### 7. decrease_then_increase
- **Description**: Valley curve (dip in middle)
- **Window function**: Piecewise linear (ramp down to valley at 40-60%, then ramp up)
- **Example descriptions**:
  - "The audio briefly becomes quieter before returning to a louder level."
  - "A dip in loudness appears in the middle, flanked by louder sections."

### 8. regular_repetition
- **Description**: Periodic oscillation (0.5-2 Hz)
- **Window function**: Sine wave with frequency 0.5-2 Hz
- **Example descriptions**:
  - "The loudness changes form a pattern that repeats instead of occurring randomly."
  - "A rhythmic, periodic variation in volume can be heard throughout."

### 9. irregular_fluctuation
- **Description**: Multiple frequency components with better dynamics
- **Window function**: 3-6 sine waves at different frequencies
- **Example descriptions**:
  - "The loudness varies in an irregular, non-periodic manner."
  - "Volume changes multiple times without following a simple up/down or repeating pattern."

---

## Audio Processing Pipeline

### 1. Load Source Audio
- **Speech** (LibriSpeech): Load utterance, trim silence (top_db=20), random crop if >30s
- **Music** (Slakh2100): Energy-based VAD → filter by duration/loudness → select random segment → crop if >30s
- **Synthetic** (PureTone, Noise): Generate on-the-fly, no preprocessing

### 2. Normalize Volume
- Peak normalize to random range 0.6-0.8
- Ensures consistent base loudness before pattern application

### 3. Apply Pattern Window
- Multiply audio by time-varying window function
- Window function corresponds to selected pattern type
- For regular_repetition: frequency-aware processing

### 4. Final Normalization
- Peak normalize to 0.95 to prevent clipping
- Ensures maximum dynamic range utilization

### 5. Save Audio
- Write as 16 kHz WAV file
- Duration: 3-30 seconds after processing

---

## Window Function Details

All window functions are implemented as time-varying amplitude envelopes:

| Pattern | Window Function | Parameters |
|---------|----------------|------------|
| constant | w(t) = 1.0 ± 2% (random variations) | Flat with minor perturbations |
| monotonic_increase | w(t) = 0.05 + 0.95 * (t / T) | Linear ramp up |
| monotonic_decrease | w(t) = 1.0 - 0.95 * (t / T) | Linear ramp down |
| sudden_increase | w(t) = step(0.05 → 1.0, 1s transition) | Step function with smoothing |
| sudden_decrease | w(t) = step(1.0 → 0.05, 1s transition) | Step function with smoothing |
| increase_then_decrease | w(t) = piecewise linear (↑ to 40-60%, ↓ after) | Bell curve |
| decrease_then_increase | w(t) = piecewise linear (↓ to 40-60%, ↑ after) | Valley curve |
| regular_repetition | w(t) = 0.5 + 0.5 * sin(2πft), f ∈ [0.5, 2] Hz | Sine wave |
| irregular_fluctuation | w(t) = sum of 3-6 sine waves at different frequencies | Multi-frequency |

All window values are clipped to [0.1, 1.0] range to avoid complete silence.

---

## Natural Language Descriptions

Each active pattern has **15 different natural language descriptions** stored in `canonical_loudness_change_descriptions.csv`. For each sample, one description is randomly selected from the corresponding pattern type. This provides linguistic diversity and tests models' ability to understand various phrasings of the same concept.

Example variations for **monotonic_increase**:
1. "The sound becomes louder over time rather than remaining flat or reversing direction."
2. "There is a steady crescendo throughout the duration of the clip."
3. "Volume gradually rises from beginning to end."
4. "The audio exhibits a continuous upward trend in loudness."
5. ...and 11 more variations

---

## Source Datasets

### Speech (~39% of samples)
- **LibriSpeech**: Audiobook recordings
  - Train: train-clean-100 split
  - Test: test-clean split
- Processing: Trim silence, random crop if >30s

### Music (~20% of samples)
- **Slakh2100**: Multi-track instrument stems
  - Instruments: Guitar, Piano, Strings, Bass, Brass, Reed, Organ, Pipe
- Processing: Energy-based VAD, duration/loudness filtering, random segment selection

### Synthetic (~41% of samples)
- **PureTone** (~20%): Sine waves at musical frequencies
- **Noise** (~20%): White, pink, brown noise
- Processing: Generate on-the-fly, no preprocessing

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** (3-30 seconds) depending on source length after processing.
- The dataset is **synthetic** — patterns are applied to real audio sources using amplitude modulation.
- **Window functions** are smoothed slightly to avoid audio artifacts.
- All window values are clipped to [0.1, 1.0] to prevent complete silence.
- The dataset evaluates:
  - **Temporal loudness perception**: Can models recognize dynamic loudness patterns?
  - **Pattern classification**: Can models distinguish between 9 active pattern types?
  - **Natural language grounding**: Can models map patterns to descriptions?
  - **Cross-domain robustness**: Performance across speech, music, and synthetic sources
- **Pattern distribution** reflects the corrected manifest labels; `constant` includes entries originally sampled from inactive isolated pattern labels.
- **Source distribution** favors speech (39%) and synthetic (41%) over music (20%).
- Audio that fails processing or is too short (<3 seconds) is skipped and regenerated.
- Train and test splits use different LibriSpeech splits but share the same Slakh2100 stems and synthetic generators.
- The dataset is split with different random seeds:
  - **Train**: seed=888, 60,000 samples
  - **Test**: seed=999, 1,000 samples
- **Multithreading** is used to load Slakh2100 metadata files efficiently.
- **Hybrid audio processing**:
  - Speech uses simple silence trimming to preserve utterance continuity
  - Music uses energy-based VAD to extract active segments from long stems
  - Synthetic audio skips preprocessing (already clean)
- This dataset complements traditional dynamic range compression research by testing perception and description of specific temporal loudness patterns.
- The `description` field enables evaluation of audio-to-text generation and audio captioning models.
- Each pattern type has multiple linguistic variations to test robustness to different phrasings.
