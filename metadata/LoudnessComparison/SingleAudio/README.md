# LoudnessComparison - SingleAudio

## Overview
**LoudnessComparison-SingleAudio** is a synthetic dataset designed to evaluate audio models' ability to perceive and compare loudness levels across audio clips. The dataset contains **99,959 training samples** and **1,000 test samples**, each featuring **2-7 audio segments** presented sequentially with varying loudness levels. Models must identify which segment is loudest, quietest, or different from the others, or determine if all segments have equal loudness.

The dataset includes three loudness comparison paradigms:
- **Single-source spot-the-difference (20%)**: All clips from the same source, with at most one having altered loudness
- **Single-source pick extreme (30%)**: All clips from the same source, each with randomly varied loudness
- **Multiple-source pick extreme (50%)**: Each clip from a different source, with ensured distinguishability (≥10dB difference)

Sounds are sourced from four domains:
- **Speech**: LibriSpeech and SpeechCommands
- **Audio**: TUT2017, VocalSound, and FSD50K
- **Music**: NSynth and MTG-Jamendo
- **Synthetic**: Clicks and noise (white/pink/brown)

All audio is sampled at **16 kHz** with durations ranging from **~3-60 seconds** (70% ≤30s, 30% ≤60s). Loudness is measured using **ITU-R BS.1770 (LUFS)** for accurate perceptual loudness quantification.

## Supported Tasks
1. **Loudness Comparison** (Identify loudest/quietest segment)
2. **Loudness Equality Detection** (Determine if all segments have equal loudness)
3. **Loudness Difference Spotting** (Identify which segment differs in loudness)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 99,959 |
| test | 1,000 |

**Sample Characteristics:**
- Segments per sample: **2-7 audio clips**
- Duration range: **~3s to 60s** (70% ≤30s, 30% ≤60s)
- Average duration: **~20-25s**
- Silence between segments: **0.4-2.0 seconds** (Gaussian-sampled)
- Gain variations: **-20dB to +20dB** (in 5dB steps)
- Sampling rate: **16 kHz** for all audio files

### Sample Type Distribution (Training Set)

| Sample Type | # Samples | Percentage | Description |
|-------------|----------:|-----------:|-------------|
| multi-source-pick-loudest | 25,198 | 25.2% | Pick loudest from different sources |
| multi-source-pick-quietest | 24,862 | 24.9% | Pick quietest from different sources |
| single-source-spot-difference | 19,958 | 20.0% | Find the different one or answer "none" |
| single-source-pick-loudest | 15,015 | 15.0% | Pick loudest from same source |
| single-source-pick-quietest | 14,926 | 14.9% | Pick quietest from same source |

### Domain Distribution (Training Set)

| Domain | # Samples |
|--------|----------:|
| Audio | 25,341 |
| Speech | 25,174 |
| Music | 24,760 |
| Synthetic | 24,684 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (UUID format) |
| `path` | Path to audio file containing all segments |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Total audio duration in seconds |
| `dataset` | Source dataset for the audio content |
| `LUFS` | Integrated loudness of entire audio in LUFS (ITU-R BS.1770) |
| `sample_type` | Type of comparison task (see Sample Types below) |
| `instruction` | Natural language instruction describing the task |
| `answer` | Target answer: `"sound 1"`, `"sound 2"`, ..., or `"none"` |
| `task_type` | Task category: `"loudest"`, `"quietest"`, or `"difference"` |
| `domain` | Acoustic domain: `Speech`, `Audio`, `Music`, or `Synthetic` |
| `gains_db` | List of gain adjustments (in dB) applied to each segment |
| `num_segments` | Number of audio segments (2-7) |
| `target_index` | Index of the target segment (0-indexed), or `null` for "none" |
| `segment_lufs` | List of LUFS values for each segment |

---

## Example Entries

```json
{"id": "92b89b12-ca82-471c-9b03-33361f548223", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/loudness_train_000000.wav", "sampling_rate": 16000, "duration": 9.1725, "dataset": "VocalSound", "LUFS": -25.156181003072465, "sample_type": "single-source-pick-quietest", "instruction": "There are 4 sound clips played in order. Identify the quietest one, or answer 'none' if all sound clips have the same loudness.", "answer": "sound 1", "task_type": "quietest", "domain": "Audio", "gains_db": [-20, -10, -20, -5], "num_segments": 4, "target_index": 0, "segment_lufs": [-35.5312343174481, -25.531234686200346, -35.5312343174481, -20.53123446650196]}

{"id": "c8ca9039-1d66-4100-bb9e-5b8010e84034", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/loudness_train_000003.wav", "sampling_rate": 16000, "duration": 20.1796875, "dataset": "Noise", "LUFS": -14.117828748451773, "sample_type": "single-source-pick-loudest", "instruction": "There are 2 sound clips played in order. Identify the loudest one, or answer 'none' if all sound clips have the same loudness.", "answer": "sound 1", "task_type": "loudest", "domain": "Synthetic", "gains_db": [15, -15], "num_segments": 2, "target_index": 0, "segment_lufs": [-14.008640670385267, -30.94684067842284]}

{"id": "82a4a8cd-c1be-496d-99f2-2908d9f747f2", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/LoudnessComparison/wavs/loudness_train_000004.wav", "sampling_rate": 16000, "duration": 52.1496875, "dataset": "Noise", "LUFS": -15.632948797342536, "sample_type": "single-source-pick-loudest", "instruction": "There are 6 sound clips played in order. Identify the loudest one, or answer 'none' if all sound clips have the same loudness.", "answer": "none", "task_type": "loudest", "domain": "Synthetic", "gains_db": [0, 0, 0, 0, 0, 0], "num_segments": 6, "target_index": null, "segment_lufs": [-15.439803109962252, -15.439803109962252, -15.439803109962252, -15.439803109962252, -15.439803109962252, -15.439803109962252]}
```

---

## Task Usage

### 1. Loudness Comparison
- **Target field:** `answer`
- **Input:** Audio file containing 2-7 segments + instruction
- **Task:** Identify which segment is loudest or quietest, or answer "none" if all equal
- **Answer format:** `"sound 1"`, `"sound 2"`, ..., `"sound N"`, or `"none"`

---

## Sample Types

### Type 1: Single-Source Spot-the-Difference (20%)
- **Description**: All segments from the same source audio, with at most one having altered loudness
- **Segments**: 3-7 repetitions
- **Equal loudness probability**: 10%
- **Task**: Identify which segment is different, or answer "none" if all equal
- **Gain modification**: ±5/10/15/20 dB on one randomly selected segment (if not equal)

### Type 2: Single-Source Pick Extreme (30%)
- **Description**: All segments from the same source audio, each with randomly varied loudness
- **Segments**: 2-7 repetitions
- **Equal loudness probability**: 5%
- **Task**: Identify the loudest or quietest segment, or answer "none" if all equal
- **Gain range**: -20dB to +20dB in 5dB steps, randomly assigned to each segment

### Type 3: Multiple-Source Pick Extreme (50%)
- **Description**: Each segment from a different source file within the same dataset
- **Segments**: 2-7 different audio files
- **Equal loudness probability**: 0% (never equal)
- **Task**: Identify the loudest or quietest segment
- **Gain range**: -20dB to +20dB in 5dB steps, with loudest/quietest ensured ≥10dB different
- **VAD**: Voice Activity Detection applied to crop silence from each source

---

## Audio Generation Methodology

### Segment Construction
1. **Load source audio** from dataset (or generate synthetic)
2. **Apply VAD** (for multiple-source only) to extract active audio
3. **Apply gain** (volume adjustment in dB)
4. **Add silence padding**: 0.2-0.4 seconds at start and end of each segment
5. **Concatenate segments** with Gaussian-sampled silence (0.4-2.0s between segments)
6. **Measure LUFS** for each segment and overall audio

### Duration Constraints
- **Target duration preference**: 70% of samples ≤30s, 30% of samples ≤60s
- If concatenated audio exceeds target duration, the sample is skipped and regenerated
- Segment padding and inter-segment silence contribute to total duration

### Loudness Measurement
- **LUFS (Loudness Units relative to Full Scale)**: ITU-R BS.1770-4 standard
- Measured using **pyloudnorm** library for accurate perceptual loudness
- Fallback to RMS-based approximation if pyloudnorm unavailable
- Separate LUFS calculated for each segment and entire audio

### Distinguishability Guarantee (Multi-Source)
- For multi-source tasks, the loudest/quietest segment is guaranteed to be ≥10dB different from others
- This ensures the target is perceptually distinguishable
- If constraint cannot be met, the sample is regenerated

---

## Source Datasets

### Speech (25% of samples)
- **LibriSpeech**: Audiobook recordings (train-clean-100 for train, test-clean for test)
- **SpeechCommands**: Spoken command words

### Audio (25% of samples)
- **TUT2017**: Acoustic scene recordings
- **VocalSound**: Vocal sound events
- **FSD50K**: Freesound environmental sounds

### Music (25% of samples)
- **NSynth**: Musical note dataset (4-second monophonic notes)
- **MTG-Jamendo**: Music tracks with genre/instrument annotations

### Synthetic (25% of samples)
- **Click**: Procedurally generated click sounds
- **Noise**: White, pink, and brown noise (generated on-the-fly)

---

## Answer Format

The `answer` field uses a 1-indexed format:
- **"sound 1"**: First segment is the target
- **"sound 2"**: Second segment is the target
- ...
- **"sound N"**: Nth segment is the target
- **"none"**: All segments have equal loudness

The `target_index` field is 0-indexed (0 for "sound 1", 1 for "sound 2", etc.) or `null` for "none".

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** depending on number of segments and silence durations.
- The dataset is **synthetic** — all samples are procedurally generated from existing audio corpora.
- **Loudness normalization**: LUFS is the perceptually-weighted loudness standard used in broadcast (ITU-R BS.1770)
- **Inter-segment silence**: Sampled from Gaussian distribution centered at 1.2s with std 0.4s, clipped to 0.4-2.0s
- The dataset evaluates:
  - **Loudness perception**: Can models distinguish loudness differences?
  - **Relative comparison**: Can models identify the loudest/quietest among multiple options?
  - **Equality detection**: Can models recognize when all segments have equal loudness?
  - **Cross-domain robustness**: Performance across speech, music, audio, and synthetic sounds
- **Gain modifications** are applied in the linear amplitude domain (not log)
- The `instruction` field provides natural language task description for instruction-following models
- **Single-source** tasks test within-source loudness comparison
- **Multiple-source** tasks test cross-source loudness comparison (more challenging due to timbral differences)
- The dataset is split with different random seeds:
  - **Train**: seed=42, 100,000 target samples (99,959 successful)
  - **Test**: seed=610, 1,000 samples
- Some samples fail generation due to duration constraints and are skipped
- The `LUFS` field represents integrated loudness of the entire concatenated audio
- **VAD (Voice Activity Detection)** uses librosa's onset detection to crop silence from audio sources in multi-source tasks
- This dataset complements traditional loudness normalization research by testing discrimination and comparison abilities
