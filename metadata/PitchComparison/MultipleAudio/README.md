# PitchComparison - MultipleAudio

## Overview
**PitchComparison-MultipleAudio** is a dataset for evaluating audio models' ability to compare pitch across multiple audio files. The dataset contains **60,000 training samples** and **1,000 test samples**, each featuring **2-4 audio files** with different pitch levels from the same or different sources. Models must compare pitch levels across these files using their actual pitch measurements (F0, MIDI notes, or frequencies).

The dataset includes two comparison paradigms:
- **Same source (56.7% train, 60% test)**: 2-4 recordings from the same speaker/instrument/waveform at different pitch levels
- **Cross source (43.3% train, 40% test)**: 2-4 recordings from different speakers/instruments/waveforms with pitch constraints to ensure distinguishability

Audio sources span three domains:
- **Speech**: ParaSpeechCaps (F0 values in Hz)
- **Music**: NSynth (MIDI note numbers)
- **Synthetic**: Pure tones and beeps (frequencies in Hz)

This dataset complements **PitchComparison-SingleAudio** by:
- Testing cross-file comparison (separate files vs. concatenated)
- Using both real pitch measurements (ParaSpeechCaps F0, NSynth MIDI) and synthetic frequencies
- Providing both within-source and across-source comparison scenarios

## Supported Tasks
1. **Pitch Comparison Across Files** (Compare pitch of multiple audio files)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 60,000 |
| test | 1,000 |

**Sample Characteristics:**
- Audio files per sample: **2-4 recordings**
- Sampling rates: **16 kHz, 44.1 kHz, or 48 kHz** (depending on source)
- Duration range: **~3-20 seconds per audio file** (variable by source)
- Pitch representations: **F0 (Hz), MIDI notes, or frequencies (Hz)**

### Sample Type Distribution

#### Training Set (60,000 samples)

| Sample Type | # Samples | Percentage | Description |
|-------------|----------:|-----------:|-------------|
| ParaSpeechCaps same-source | 10,000 | 16.7% | Same speaker at different F0 levels |
| ParaSpeechCaps cross-source | 15,000 | 25.0% | Different speakers with F0 constraints (≥20 Hz) |
| NSynth same-source | 15,000 | 25.0% | Same instrument at different pitches |
| NSynth cross-source | 15,000 | 25.0% | Different instruments with pitch constraints (≥3 semitones) |
| Synthetic same-source | 5,000 | 8.3% | Same waveform at different frequencies |

#### Test Set (1,000 samples)

| Sample Type | # Samples | Percentage |
|-------------|----------:|-----------:|
| ParaSpeechCaps same-source | 200 | 20% |
| ParaSpeechCaps cross-source | 200 | 20% |
| NSynth same-source | 200 | 20% |
| NSynth cross-source | 200 | 20% |
| Synthetic same-source | 200 | 20% |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (format varies by type) |
| `paths` | List of paths to audio files (2-4 files) |
| `sampling_rates` | List of sampling rates for each audio file |
| `durations` | List of durations in seconds for each audio file |
| `dataset` | Dataset name (`PitchComparison-MultipleAudio`) |
| `pitches` | List of pitch values for each audio file (type depends on source) |
| `pitch_type` | Type of pitch measurement: `f0_hz`, `midi_note`, or `frequency_hz` |
| `source_dataset` | Original source dataset (`ParaSpeechCaps`, `NSynth`, or `Synthetic`) |
| `num_audios` | Number of audio files in the sample (2-4) |
| `sample_type` | Type of comparison: `same_source` or `cross_source` |
| `group_key` | Speaker/instrument/waveform identifier for same-source samples |
| `source_ids` | List of source identifiers for cross-source samples |
| `metadata` | Additional dataset-specific metadata (optional) |

---

## Example Entries

### ParaSpeechCaps Same-Source
```json
{
  "id": "paraspeech_same_id01392_009437_4",
  "paths": [
    "/path/to/id01392_utt1.wav",
    "/path/to/id01392_utt2.wav",
    "/path/to/id01392_utt3.wav",
    "/path/to/id01392_utt4.wav"
  ],
  "sampling_rates": [44100, 44100, 44100, 44100],
  "durations": [4.1, 4.2, 5.5, 6.4],
  "dataset": "PitchComparison-MultipleAudio",
  "pitches": [65, 100, 110, 270],
  "pitch_type": "f0_hz",
  "source_dataset": "ParaSpeechCaps",
  "num_audios": 4,
  "sample_type": "same_source",
  "group_key": "id01392"
}
```

### NSynth Same-Source
```json
{
  "id": "nsynth_same_brass_006577_4",
  "paths": [
    "/path/to/brass_C#2.wav",
    "/path/to/brass_B5.wav",
    "/path/to/brass_A#2.wav",
    "/path/to/brass_A#1.wav"
  ],
  "sampling_rates": [16000, 16000, 16000, 16000],
  "durations": [4.0, 4.0, 4.0, 4.0],
  "dataset": "PitchComparison-MultipleAudio",
  "pitches": [37, 83, 46, 34],
  "pitch_type": "midi_note",
  "source_dataset": "NSynth",
  "num_audios": 4,
  "sample_type": "same_source",
  "group_key": "brass",
  "metadata": {
    "instrument": "brass",
    "pitch_names": ["C#2", "B5", "A#2", "A#1"],
    "sound_production_methods": ["acoustic", "acoustic", "acoustic", "acoustic"]
  }
}
```

### ParaSpeechCaps Cross-Source
```json
{
  "id": "paraspeech_cross_000002_2",
  "paths": [
    "/path/to/id06004_utt.wav",
    "/path/to/EARS_p087_utt.wav"
  ],
  "sampling_rates": [44100, 48000],
  "durations": [5.6, 13.6],
  "dataset": "PitchComparison-MultipleAudio",
  "pitches": [150, 225],
  "pitch_type": "f0_hz",
  "source_dataset": "ParaSpeechCaps",
  "num_audios": 2,
  "sample_type": "cross_source",
  "source_ids": ["id06004", "EARS_p087"]
}
```

### NSynth Cross-Source
```json
{
  "id": "nsynth_cross_007456_4",
  "paths": [
    "/path/to/vocal_G4.wav",
    "/path/to/mallet_D#5.wav",
    "/path/to/bass_G#1.wav",
    "/path/to/string_C#4.wav"
  ],
  "sampling_rates": [16000, 16000, 16000, 16000],
  "durations": [4.0, 4.0, 4.0, 4.0],
  "dataset": "PitchComparison-MultipleAudio",
  "pitches": [67, 75, 32, 61],
  "pitch_type": "midi_note",
  "source_dataset": "NSynth",
  "num_audios": 4,
  "sample_type": "cross_source",
  "source_ids": ["vocal", "mallet", "bass", "string"],
  "metadata": {
    "instruments": ["vocal", "mallet", "bass", "string"],
    "pitch_names": ["G4", "D#5", "G#1", "C#4"],
    "sound_production_methods": ["acoustic", "electronic", "synthetic", "acoustic"]
  }
}
```

### Synthetic Same-Source
```json
{
  "id": "synthetic_same_square_000041_3",
  "paths": [
    "/synthetic/puretone_square_1046.5Hz.wav",
    "/synthetic/puretone_square_41.2Hz.wav",
    "/synthetic/puretone_square_523.3Hz.wav"
  ],
  "sampling_rates": [16000, 16000, 16000],
  "durations": [3.0, 3.0, 3.0],
  "dataset": "PitchComparison-MultipleAudio",
  "pitches": [1046.5, 41.2, 523.3],
  "pitch_type": "frequency_hz",
  "source_dataset": "Synthetic",
  "num_audios": 3,
  "sample_type": "same_source",
  "group_key": "square",
  "metadata": {
    "waveform_type": "square",
    "note_names": ["C6", "E1", "C5"]
  }
}
```

---

## Task Usage

### 1. Pitch Comparison Across Files
- **Target field:** `pitches`
- **Input:** 2-4 separate audio files
- **Task:** Compare and rank pitch levels across files, or identify highest/lowest
- **Ground truth:** Measured F0 values (Hz), MIDI note numbers, or frequencies (Hz)

---

## Sample Types

### Same Source (56.7% train, 60% test)

#### ParaSpeechCaps Same-Source (10,000 train, 200 test)
- **Description**: Multiple utterances from the same speaker at different F0 levels
- **Audio files**: 2-4 utterances with natural pitch variation
- **Purpose**: Test pitch comparison ability without timbral variation
- **Group key**: Speaker ID (e.g., `id01392`, `EARS_p028`)
- **F0 variation**: Natural variation across utterances
- **Sampling strategy**: Uniformly sample across speaker's F0 range for diversity

#### NSynth Same-Source (15,000 train, 200 test)
- **Description**: Multiple notes from the same instrument at different pitches
- **Audio files**: 2-4 notes at different MIDI pitches
- **Purpose**: Test pitch comparison ability with consistent timbre
- **Group key**: Instrument family (e.g., `brass`, `piano`, `guitar`)
- **Pitch variation**: Different musical notes
- **Sampling strategy**: Randomly select different pitches for each instrument

#### Synthetic Same-Source (5,000 train, 200 test)
- **Description**: Multiple pure tones with the same waveform at different frequencies
- **Audio files**: 2-4 tones at different musical frequencies
- **Purpose**: Test pitch comparison in the cleanest possible setting
- **Group key**: Waveform type (e.g., `sine`, `square`, `sawtooth`, `triangle`)
- **Frequency variation**: Musical notes from A0 (27.5 Hz) to C8 (4186 Hz)
- **Note**: Audio files are placeholder paths; actual synthesis happens on-the-fly

### Cross Source (43.3% train, 40% test)

#### ParaSpeechCaps Cross-Source (15,000 train, 200 test)
- **Description**: Utterances from different speakers with F0 constraints
- **Audio files**: 2-4 utterances from different speakers
- **Purpose**: Test pitch comparison ability with speaker/timbral variation
- **Constraint**: Extreme F0s (quietest and loudest) must be ≥20 Hz apart from all others
- **Source IDs**: List of speaker identifiers
- **F0 constraint reasoning**: At typical F0 ranges (100-200 Hz), 20 Hz ≈ 2-3 semitones, ensuring perceptual distinguishability

#### NSynth Cross-Source (15,000 train, 200 test)
- **Description**: Notes from different instruments with pitch constraints
- **Audio files**: 2-4 notes from different instruments
- **Purpose**: Test pitch comparison ability with instrumental timbral variation
- **Constraint**: Extreme pitches (lowest and highest) must be ≥3 semitones apart from all others
- **Source IDs**: List of instrument families
- **Pitch constraint reasoning**: 3 semitones = minor third interval (~16% frequency ratio), perceptually distinguishable despite timbre differences

---

## Dataset Construction

### Source Datasets

All audio comes from three source datasets:

#### 1. ParaSpeechCaps (F0Estimation)
- **Train**: 116,516 samples, 637 speakers
- **Test**: 14,756 samples, 163 speakers
- **F0 range**: 35-985 Hz (mean: 154.9 Hz)
- **Sampling rates**: 44.1 kHz or 48 kHz
- **Duration**: Variable (2-20 seconds)
- **Format**: VoxCeleb1/2, EARS, Expresso corpora

#### 2. NSynth
- **Train**: 289,205 samples, 11 instruments
- **Test**: 4,096 samples, 10 instruments
- **Pitch range**: 112 unique pitches (A#-1 to G8)
- **Sampling rate**: 16 kHz
- **Duration**: Exactly 4 seconds
- **Instruments**: bass, brass, flute, guitar, keyboard, mallet, organ, reed, string, synth_lead, vocal

#### 3. Synthetic
- **Generation**: On-the-fly pure tone synthesis
- **Waveforms**: sine, square, sawtooth, triangle
- **Frequency range**: Musical notes A0 (27.5 Hz) to C8 (4186 Hz)
- **Sampling rate**: 16 kHz
- **Duration**: 3 seconds

### Sampling Strategies

#### Same-Source Sampling

**ParaSpeechCaps**:
1. Filter speakers with ≥4 utterances
2. Randomly select number of audios (2-4)
3. Randomly select a speaker
4. Sort utterances by F0
5. Sample uniformly across F0 range for diversity

**NSynth**:
1. Filter instruments with ≥4 different pitches
2. Randomly select number of audios (2-4)
3. Randomly select an instrument
4. Randomly select different pitches
5. For each pitch, randomly select one recording

**Synthetic**:
1. Randomly select waveform type
2. Randomly select number of audios (2-4)
3. Randomly select different musical frequencies

#### Cross-Source Sampling (with Constraints)

**ParaSpeechCaps** (≥20 Hz constraint):
1. Randomly select number of audios (2-4)
2. Randomly select different speakers
3. For each speaker, randomly select one utterance
4. Check constraint: extreme F0s must be ≥20 Hz from all others
5. If constraint not met, resample (max 200 attempts per sample)

**NSynth** (≥3 semitones constraint):
1. Randomly select number of audios (2-4)
2. Randomly select different instruments
3. For each instrument, randomly select one note
4. Check constraint: extreme MIDI notes must be ≥3 semitones from all others
5. If constraint not met, resample (max 200 attempts per sample)

---

## Pitch Constraints

### Why Different Constraints?

The constraints ensure that extreme pitch values are perceptually distinguishable even with timbral variation:

| Dataset | Constraint | Reasoning |
|---------|-----------|-----------|
| ParaSpeechCaps | ≥20 Hz | At 100 Hz: 20 Hz ≈ 3.5 semitones<br>At 200 Hz: 20 Hz ≈ 1.7 semitones<br>Ensures distinguishability across typical voice ranges |
| NSynth | ≥3 semitones | Minor third interval (~16% frequency ratio)<br>Perceptually clear despite instrumental timbre differences |

### Constraint Application

For 2 audios:
- Simply require |pitch1 - pitch2| ≥ threshold

For 3+ audios:
- Extreme values (min and max) must be ≥ threshold from **all other values**
- Ensures the target is clearly distinguishable

---

## Pitch Representations

| Dataset | Type | Range | Unit |
|---------|------|-------|------|
| ParaSpeechCaps | `f0_hz` | 35-985 | Hz (fundamental frequency) |
| NSynth | `midi_note` | 10-103 | MIDI note number (A#-1 = 10, G8 = 103) |
| Synthetic | `frequency_hz` | 27.5-4186 | Hz (pure tone frequency) |

**MIDI Note Conversion**:
- MIDI note number = (octave + 1) × 12 + note offset
- Example: C3 → (3+1)×12 + 0 = 48
- Example: A#4 → (4+1)×12 + 10 = 70

---

## Generation Commands

### Generate Full Dataset
```bash
cd /home/tseng/FullSpectrumDataset/metadata/pitch/MultipleAudio
/home/tseng/miniconda3/envs/DeSTA2/bin/python generate_manifest.py
```

This will generate:
- 60,000 training samples
- 1,000 test samples

---

## Notes
- Audio files have **mixed sampling rates** (16 kHz, 44.1 kHz, 48 kHz) depending on source.
- Audio files are **separate** — not concatenated into a single file (unlike SingleAudio).
- **ParaSpeechCaps** uses real F0 measurements from speech utterances.
- **NSynth** uses MIDI note numbers from instrument recordings.
- **Synthetic** audio paths are placeholders for on-the-fly generation.
- The dataset evaluates:
  - **Cross-file pitch comparison**: Can models compare pitch across separate audio files?
  - **Timbral invariance**: Can models compare pitch despite speaker/instrument differences?
  - **Multi-modal pitch understanding**: Performance across different pitch representations (F0, MIDI, frequency)
  - **Same-source vs. cross-source**: Difficulty difference between consistent and varied timbres
- **Same-source samples** provide an easier baseline with consistent timbre.
- **Cross-source samples** are more challenging due to timbral variability.
- The dataset is **metadata-only for ParaSpeechCaps and NSynth** — it references audio files from existing corpora.
- **Synthetic samples** would require on-the-fly audio generation during dataset loading.
- Train and test splits use different random seeds:
  - **Train**: seeds 42-46 for different sample types
  - **Test**: seeds 995-999 for different sample types
- This dataset complements **PitchComparison-SingleAudio** by:
  - Using real pitch measurements (F0, MIDI) instead of only synthetic pitch shifts
  - Testing cross-file comparison (separate files vs. concatenated segments)
  - Providing both within-source and across-source comparison scenarios
  - Covering multiple pitch representation types (Hz, MIDI, frequency)

---

## Dependencies

- numpy
- tqdm
- json
- gzip

No special audio processing libraries required for manifest generation (only for actual audio loading/synthesis).
