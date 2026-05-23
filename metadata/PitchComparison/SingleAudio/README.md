# PitchComparison - SingleAudio

## Overview
**PitchComparison-SingleAudio** is a synthetic dataset designed to evaluate audio models' ability to perceive and compare pitch levels across audio clips. The dataset contains **99,981 training samples** and **1,000 test samples**, each featuring **2-7 audio segments** presented sequentially with varying pitch levels. Models must identify which segment has the highest or lowest pitch, or which segment differs in pitch from the others, or determine if all segments have equal pitch.

The dataset includes three pitch comparison paradigms:
- **Single-source spot-the-difference (30%)**: All clips from the same source, with at most one having altered pitch
- **Single-source pick extreme (40%)**: All clips from the same source, each with randomly varied pitch
- **Multiple-source pick extreme (30%)**: Each clip from a different source with natural pitch variation

Sounds are sourced from four domains:
- **Speech**: LibriSpeech, SpeechCommands, and ParaSpeechCaps
- **Audio**: ESC-50 and VocalSound
- **Music**: NSynth and Slakh2100
- **Synthetic**: PureTone and Beep

All audio is sampled at **16 kHz** with durations ranging from **~1-31 seconds** (mean ~16s). Pitch shifting is implemented using **PyWorld vocoder** for speech/audio, natural pitch variation for NSynth/ParaSpeechCaps, and on-the-fly synthesis for PureTone/Beep.

## Supported Tasks
1. **Pitch Comparison** (Identify highest/lowest pitch segment)
2. **Pitch Equality Detection** (Determine if all segments have equal pitch)
3. **Pitch Difference Spotting** (Identify which segment differs in pitch)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 99,981 |
| test | 1,000 |

**Sample Characteristics:**
- Segments per sample: **2-7 audio clips**
- Duration range: **~1s to 31s** (mean ~16s)
- Pitch shifts: **-6 to +9 semitones** for single-source tasks
- Natural pitch variation for multi-source tasks
- Silence between segments: **0.4-2.0 seconds** (Gaussian-sampled)
- Sampling rate: **16 kHz** for all audio files

### Sample Type Distribution (Training Set)

| Sample Type | # Samples | Percentage | Description |
|-------------|----------:|-----------:|-------------|
| single-source-spot-difference | 29,969 | 30.0% | Find the different one or answer "none" |
| single-source-pick-highest | 19,996 | 20.0% | Pick highest pitch from same source |
| single-source-pick-lowest | 19,926 | 19.9% | Pick lowest pitch from same source |
| multi-source-pick-highest | 15,060 | 15.1% | Pick highest pitch from different sources |
| multi-source-pick-lowest | 15,030 | 15.0% | Pick lowest pitch from different sources |

### Domain Distribution (Training Set)

| Domain | # Samples |
|--------|----------:|
| Speech | 32,688 |
| Music | 32,427 |
| Audio | 17,579 |
| Synthetic | 17,287 |

### Source Dataset Distribution (Training Set)

| Dataset | # Samples | Type |
|---------|----------:|------|
| NSynth | 23,862 | Music (natural pitch variation) |
| ParaSpeechCaps | 14,950 | Speech (natural F0 variation) |
| LibriSpeech | 8,904 | Speech (pitch-shifted) |
| SpeechCommands | 8,834 | Speech (pitch-shifted) |
| VocalSound | 8,795 | Audio (pitch-shifted) |
| ESC-50 | 8,784 | Audio (pitch-shifted) |
| Beep | 8,712 | Synthetic (synthesized) |
| PureTone | 8,575 | Synthetic (synthesized) |
| Slakh2100 | 8,565 | Music (pitch-shifted) |

### Segments per Sample (Training Set)

| # Segments | # Samples |
|-----------:|----------:|
| 2 | 11,630 |
| 3 | 22,470 |
| 4 | 24,089 |
| 5 | 19,538 |
| 6 | 12,525 |
| 7 | 9,729 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (UUID format) |
| `path` | Path to audio file containing all segments |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Total audio duration in seconds |
| `dataset` | Dataset name (`PitchComparison`) |
| `source_dataset` | Source dataset for the audio content |
| `sample_type` | Type of comparison task (see Sample Types below) |
| `instruction` | Natural language instruction describing the task |
| `answer` | Target answer: `"sound 1"`, `"sound 2"`, ..., `"sound N, higher/lower"`, or `"none"` |
| `task_type` | Task category: `"highest"`, `"lowest"`, or difference spotting |
| `domain` | Acoustic domain: `Speech`, `Audio`, `Music`, or `Synthetic` |
| `num_segments` | Number of audio segments (2-7) |
| `target_index` | Index of the target segment (0-indexed), or `null` for "none" |
| `pitches` | List of pitch values for each segment (semitones or Hz) |
| `pitch_shifts` | List of pitch shift amounts (semitones) for single-source tasks |

---

## Example Entries

### Single-Source Pick Highest
```json
{"id": "1dd9e46c-e9a6-46a4-8a32-a2fe938ff24d", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PitchComparison/SingleAudio/wavs/pitch_train_000000.wav", "sampling_rate": 16000, "duration": 9.1171875, "instruction": "There are 4 sound clips played in order. Identify the one with the highest pitch, or answer 'none' if all sound clips have the same pitch.", "answer": "sound 1", "sample_type": "single-source-pick-highest", "task_type": "highest", "domain": "Audio", "source_dataset": "VocalSound", "pitch_shifts": [9, 4, 2, 6], "num_segments": 4, "target_index": 0, "pitches": [9, 4, 2, 6], "dataset": "PitchComparison"}
```

### Multi-Source Pick Highest
```json
{"id": "c448a0cd-38f3-42c3-82aa-07b5b6a652e8", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PitchComparison/SingleAudio/wavs/pitch_train_000001.wav", "sampling_rate": 16000, "duration": 10.849875, "instruction": "There are 3 different sound clips played in order. Identify the one with the highest pitch.", "answer": "sound 1", "sample_type": "multi-source-pick-highest", "task_type": "highest", "domain": "Music", "source_dataset": "NSynth", "num_segments": 3, "target_index": 0, "pitches": [50, 9, 43], "dataset": "PitchComparison"}
```

### Single-Source Spot Difference (Equal)
```json
{"id": "9001b52d-dcd0-411b-9ccf-ff59786721a8", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PitchComparison/SingleAudio/wavs/pitch_train_000006.wav", "sampling_rate": 16000, "duration": 25.1103125, "instruction": "There are 4 sound clips played in order. Identify the one that differs in pitch, or answer 'none' if all sound clips have the same pitch.", "answer": "none", "sample_type": "single-source-spot-difference", "variation": "equal", "domain": "Audio", "source_dataset": "ESC50", "pitch_shift": 0, "num_segments": 4, "target_index": null, "pitches": [0, 0, 0, 0], "dataset": "PitchComparison"}
```

### Single-Source Spot Difference (Higher)
```json
{"id": "fbcdd33a-9b34-4c4c-b00a-68c3a140bbd1", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PitchComparison/SingleAudio/wavs/pitch_train_000007.wav", "sampling_rate": 16000, "duration": 27.0554375, "instruction": "There are 5 sound clips played in order. Identify the one that differs in pitch, or answer 'none' if all sound clips have the same pitch.", "answer": "sound 4, higher", "sample_type": "single-source-spot-difference", "variation": "higher", "domain": "Speech", "source_dataset": "LibriSpeech", "pitch_shift": 3, "num_segments": 5, "target_index": 3, "pitches": [0, 0, 0, 3, 0], "dataset": "PitchComparison"}
```

### Multi-Source Pick Highest (ParaSpeechCaps)
```json
{"id": "ba45bf76-b63e-4fcd-9e37-00b1f47204a5", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/PitchComparison/SingleAudio/wavs/pitch_train_000009.wav", "sampling_rate": 16000, "duration": 29.463375, "instruction": "There are 4 different sound clips played in order. Identify the one with the highest pitch.", "answer": "sound 3", "sample_type": "multi-source-pick-highest", "task_type": "highest", "domain": "Speech", "source_dataset": "ParaSpeechCaps", "num_segments": 4, "target_index": 2, "pitches": [125, 165, 205, 180], "dataset": "PitchComparison"}
```

---

## Task Usage

### 1. Pitch Comparison
- **Target field:** `answer`
- **Input:** Audio file containing 2-7 segments + instruction
- **Task:** Identify which segment has highest or lowest pitch, or answer "none" if all equal
- **Answer format:** `"sound 1"`, `"sound 2"`, ..., `"sound N"`, or `"none"`

### 2. Pitch Difference Spotting
- **Target field:** `answer`
- **Input:** Audio file containing 2-7 segments + instruction
- **Task:** Identify which segment differs in pitch, specifying if it's higher or lower
- **Answer format:** `"sound N, higher"`, `"sound N, lower"`, or `"none"`

---

## Sample Types

### Type 1: Single-Source Spot-the-Difference (30%)
- **Description**: All segments from the same source audio, with at most one having altered pitch
- **Segments**: 3-7 repetitions of the same audio clip
- **Equal pitch probability**: 10%
- **Task**: Identify which segment is different (higher or lower), or answer "none" if all equal
- **Pitch modification**: ±2 to ±6 semitones on one randomly selected segment (if not equal)
- **Pitch shifting method**: PyWorld vocoder for speech/audio, original recordings for NSynth

### Type 2: Single-Source Pick Extreme (40%)
- **Description**: All segments from the same source audio, each with randomly varied pitch
- **Segments**: 2-7 repetitions of the same audio clip
- **Equal pitch probability**: 5%
- **Task**: Identify the highest or lowest pitch segment, or answer "none" if all equal
- **Pitch range**: -6 to +9 semitones, randomly assigned to each segment
- **Constraint**: Extreme pitch must be ≥2 semitones from all others
- **Pitch shifting method**: PyWorld vocoder for speech/audio, original recordings for NSynth

### Type 3: Multiple-Source Pick Extreme (30%)
- **Description**: Each segment from a different audio file within the same dataset
- **Segments**: 2-7 different audio files
- **Equal pitch probability**: 0% (never equal)
- **Task**: Identify the highest or lowest pitch segment
- **Pitch variation**: Natural pitch differences across sources
- **Sources**:
  - **ParaSpeechCaps**: Different speakers with natural F0 variation (Hz)
  - **NSynth**: Different instruments at different MIDI pitches
- **VAD**: Voice Activity Detection applied to crop silence from each source

---

## Audio Generation Methodology

### Segment Construction

1. **Load source audio** from dataset (or generate synthetic)
2. **Apply VAD** (for Slakh2100) to extract active audio segments
3. **Apply pitch shifting** (for single-source tasks):
   - **PyWorld vocoder** for speech/audio sources
   - **Native pitch selection** for NSynth (select different MIDI notes)
   - **On-the-fly synthesis** for PureTone/Beep at target frequencies
4. **Trim silence** from edges (top_db=20 for most, top_db=25 for Slakh2100)
5. **Normalize volume** to -30 dBFS RMS
6. **Add silence padding**: 0.2-0.4 seconds at start and end of each segment
7. **Concatenate segments** with Gaussian-sampled silence (0.4-2.0s between segments)

### Pitch Shifting Methods

#### PyWorld Vocoder (Speech, Audio, Music)
- **Target datasets**: LibriSpeech, SpeechCommands, VocalSound, ESC-50, Slakh2100
- **Method**: WORLD vocoder pitch manipulation
- **Pitch shift range**: -6 to +9 semitones
- **Process**:
  1. Extract F0 (fundamental frequency), spectral envelope, and aperiodicity
  2. Multiply F0 by pitch shift factor: `2^(semitones/12)`
  3. Reconstruct audio with modified F0
- **Advantage**: Preserves timbre while changing pitch

#### Natural Pitch Selection (NSynth)
- **Target dataset**: NSynth musical instrument notes
- **Method**: Select recordings at different MIDI pitches
- **Pitch range**: 112 unique pitches from A#-1 to G8
- **Process**:
  1. For same-source: Select same instrument at different pitches
  2. For multi-source: Select different instruments at different pitches
- **Advantage**: Uses natural recordings instead of synthesis

#### Natural F0 Variation (ParaSpeechCaps)
- **Target dataset**: ParaSpeechCaps speech with F0 annotations
- **Method**: Select utterances with different fundamental frequencies
- **F0 range**: 35-985 Hz (natural speech variation)
- **Process**:
  1. Select different speakers or different utterances from same speaker
  2. Use annotated F0 values as ground truth pitch
- **Advantage**: Real speech with natural pitch variation

#### On-the-Fly Synthesis (PureTone, Beep)
- **Target datasets**: Synthetic pure tones and beeps
- **Method**: Generate waveforms at specific frequencies
- **Waveforms**: sine, square, sawtooth, triangle
- **Frequency range**: Musical notes from A0 (27.5 Hz) to C8 (4186 Hz)
- **Process**:
  1. Randomly select waveform type
  2. Generate tone/beep at target musical frequency
  3. Apply fade in/out to prevent clicks
- **Advantage**: Precise frequency control

### Duration Constraints
- **Target duration**: Maximum 30 seconds per sample
- If concatenated audio exceeds 30s, sample is regenerated
- Segment padding and inter-segment silence contribute to total duration
- Most samples fall between 5-25 seconds

### Pitch Constraints (Single-Source Tasks)
- **Minimum difference**: Extreme pitch must be ≥2 semitones from all others
- **Pitch shift range**: -6 to +9 semitones
- **Equal pitch probability**:
  - Spot-difference: 10%
  - Pick extreme: 5%
- If constraints cannot be met, sample is regenerated

---

## Source Datasets

### Speech (33% of samples)
- **LibriSpeech** (9%): Audiobook recordings (train-clean-100 for train, test-clean for test)
  - Pitch shifting: PyWorld vocoder
- **SpeechCommands** (9%): Spoken command words
  - Pitch shifting: PyWorld vocoder
- **ParaSpeechCaps** (15%): Speech with F0 annotations
  - Pitch variation: Natural F0 differences across speakers/utterances

### Audio (18% of samples)
- **VocalSound** (9%): Vocal sound events (laughter, cough, etc.)
  - Pitch shifting: PyWorld vocoder
- **ESC-50** (9%): Environmental sounds
  - Pitch shifting: PyWorld vocoder

### Music (32% of samples)
- **NSynth** (24%): Musical instrument notes
  - Pitch variation: Natural pitch selection (MIDI notes)
- **Slakh2100** (9%): Multi-track music stems
  - Pitch shifting: PyWorld vocoder
  - VAD: Energy-based segmentation

### Synthetic (17% of samples)
- **PureTone** (9%): Pure sine/square/sawtooth/triangle waves
  - Generation: On-the-fly synthesis at target frequency
- **Beep** (9%): Short discrete tones
  - Generation: On-the-fly synthesis at target frequency

---

## Answer Format

The `answer` field uses a 1-indexed format with additional context for spot-difference tasks:

**Pick extreme tasks:**
- **"sound 1"**: First segment is the target
- **"sound 2"**: Second segment is the target
- ...
- **"sound N"**: Nth segment is the target
- **"none"**: All segments have equal pitch

**Spot-difference tasks:**
- **"sound N, higher"**: Nth segment is higher in pitch
- **"sound N, lower"**: Nth segment is lower in pitch
- **"none"**: All segments have equal pitch

The `target_index` field is 0-indexed (0 for "sound 1", 1 for "sound 2", etc.) or `null` for "none".

---

## Pitch Representations

The `pitches` field contains different representations depending on source:

| Source | Representation | Unit | Example |
|--------|---------------|------|---------|
| PyWorld-shifted sources | Pitch shift amount | Semitones relative to original | `[0, 3, -2, 6]` |
| NSynth | MIDI note number | MIDI (0-127) | `[50, 9, 43]` |
| ParaSpeechCaps | Fundamental frequency | Hz | `[125, 165, 205, 180]` |
| PureTone/Beep | Frequency | Hz | `[440, 880, 220]` |

---

## Generation Commands

### Generate Full Dataset
```bash
cd /home/tseng/FullSpectrumDataset/metadata/PitchComparison/SingleAudio
/home/tseng/miniconda3/envs/DeSTA2/bin/python generate_dataset_fast.py
```

This will generate:
- 100,000 training samples (99,981 successful)
- 1,000 test samples

### Test with Small Sample
```bash
/home/tseng/miniconda3/envs/DeSTA2/bin/python test_generate.py
```

This generates 10 samples for testing.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** depending on number of segments and silence durations.
- The dataset is **synthetic** — all samples are procedurally generated from existing audio corpora.
- **PyWorld vocoder** is used for pitch shifting speech, audio, and music sources while preserving timbre.
- **Inter-segment silence**: Sampled from Gaussian distribution centered at 0.4 × segment_duration, clipped to 0.4-2.0s
- The dataset evaluates:
  - **Pitch perception**: Can models distinguish pitch differences?
  - **Relative comparison**: Can models identify the highest/lowest among multiple options?
  - **Equality detection**: Can models recognize when all segments have equal pitch?
  - **Cross-domain robustness**: Performance across speech, music, audio, and synthetic sounds
- **Pitch shifting** preserves duration and timbre characteristics
- The `instruction` field provides natural language task description for instruction-following models
- **Single-source** tasks test within-source pitch comparison with controlled pitch shifts
- **Multiple-source** tasks test cross-source pitch comparison with natural pitch variation
- The dataset is split with different random seeds:
  - **Train**: seed=406
  - **Test**: seed varies by implementation
- Some samples fail generation due to duration constraints and are skipped
- **VAD (Voice Activity Detection)** uses energy-based detection to crop silence from Slakh2100 music stems
- This dataset complements **PitchComparison-MultipleAudio** by:
  - Using concatenated segments instead of separate files
  - Including spot-the-difference tasks
  - Using pitch shifting for controlled pitch variation
  - Covering broader range of source datasets
- **Slakh2100 loading** uses parallel processing (ThreadPoolExecutor) for efficiency
- All audio is normalized to **-30 dBFS RMS** for consistent loudness
- Silence is cropped from edges (top_db=20 for most datasets, top_db=25 for Slakh2100)
- Train/test splits use corresponding splits from source datasets when available

---

## Dependencies

Generation scripts require:
- **pyworld**: For pitch shifting via WORLD vocoder
- **librosa**: Audio loading and processing
- **soundfile**: Audio I/O
- **numpy**: Numerical operations
- **scipy**: Statistical distributions (truncnorm)
- **tqdm**: Progress bars

Install dependencies:
```bash
pip install pyworld librosa soundfile numpy scipy tqdm
```

---

## Technical Details

### PyWorld Vocoder Pipeline
1. **Decomposition**:
   - Extract F0 (fundamental frequency)
   - Extract spectral envelope (SP)
   - Extract aperiodicity (AP)
2. **Pitch modification**:
   - Multiply F0 by shift factor: `2^(semitones/12)`
   - Keep SP and AP unchanged
3. **Synthesis**:
   - Reconstruct audio from modified F0, SP, and AP
   - Preserves timbre and duration

### VAD for Slakh2100
- **Energy threshold**: 0.0005 (very sensitive)
- **Frame duration**: 30ms
- **Minimum segment duration**: 3 seconds
- **Purpose**: Extract active musical segments from long stems

### Volume Normalization
- **Target**: -30 dBFS RMS
- **Method**: RMS-based gain adjustment
- **Peak limiting**: Clip to ±1.0 to prevent clipping
- **Applied to**: Each segment before concatenation

---

## Comparison with LoudnessComparison-SingleAudio

| Aspect | LoudnessComparison | PitchComparison |
|--------|-------------------|-----------------|
| **Acoustic dimension** | Amplitude (loudness) | Frequency (pitch) |
| **Modification method** | Gain adjustment (dB) | PyWorld vocoder, natural selection |
| **Sources** | Speech, Audio, Music, Synthetic | Speech, Audio, Music, Synthetic |
| **Sample types** | Spot-diff, pick extreme (single/multi) | Spot-diff, pick extreme (single/multi) |
| **Sample rate** | 16 kHz | 16 kHz |
| **Duration range** | ~3-60s | ~1-31s |
| **Dataset size** | 99,959 train, 1k test | 99,981 train, 1k test |
| **Ground truth** | LUFS (loudness) | Semitones, MIDI, F0 (Hz) |
