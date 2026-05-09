# Counting

## Overview
**Counting** is a synthetic dataset designed to evaluate audio models' ability to count the number of repetitions of a single sound event within an audio clip. The dataset contains **100,000 training samples** and **1,000 test samples**, each featuring **1-12 repetitions** of a specific sound event drawn from diverse acoustic domains. Audio clips are constructed by repeating a single sound (e.g., a beep, a spoken word, a musical note, or an environmental sound) with random temporal spacing, including potential overlaps for music and environmental audio.

The dataset aggregates sounds from four source domains:
- **Speech**: Spoken words from SpeechCommands
- **Audio**: Environmental sounds from FSD50K (filtered to single events)
- **Music**: Musical notes from NSynth
- **Synthetic**: Procedurally generated beeps and clicks

All audio is sampled at **16 kHz** and normalized to **-20 dBFS RMS** for consistent volume. This benchmark is particularly useful for evaluating counting, event detection, repetition analysis, and temporal reasoning capabilities in audio understanding models.

## Supported Tasks
1. **Sound Event Counting**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 100,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **1.0s to 30.0s**
- Average duration: **~12.0s**
- Repetition count range: **1 to 12 events**
- Sampling rate: **16 kHz** for all audio files

### Source Dataset Distribution (Training Set)

| Source Dataset | # Samples | Domain |
|----------------|----------:|--------|
| Click | 20,209 | Synthetic |
| Beep | 20,103 | Synthetic |
| FSD50K | 20,019 | Audio |
| NSynth | 19,845 | Music |
| SpeechCommands | 19,824 | Speech |

### Count Distribution (Training Set)

| Count | # Samples |
|------:|----------:|
| 1 | 8,350 |
| 2 | 8,303 |
| 3 | 8,251 |
| 4 | 8,420 |
| 5 | 8,320 |
| 6 | 10,653 |
| 7 | 13,977 |
| 8 | 6,883 |
| 9 | 6,609 |
| 10 | 6,915 |
| 11 | 6,786 |
| 12 | 6,533 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (e.g., `train_000000`, `test_000000`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`Counting`) |
| `count` | Number of sound event repetitions (1-12) |
| `source_dataset` | Original dataset the sound was sourced from |
| `source_domain` | Acoustic domain (Speech, Audio, Music, Synthetic) |
| `event_label` | Label of the repeated sound event |

---

## Example Entries

```json
{"id": "train_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Counting/wavs/train_000000.wav", "sampling_rate": 16000, "duration": 20.545, "dataset": "Counting", "count": 10, "source_dataset": "SpeechCommands", "source_domain": "Speech", "event_label": "seven"}

{"id": "train_000001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Counting/wavs/train_000001.wav", "sampling_rate": 16000, "duration": 11.164, "dataset": "Counting", "count": 9, "source_dataset": "Beep", "source_domain": "Synthetic", "event_label": "beep"}

{"id": "train_000002", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Counting/wavs/train_000002.wav", "sampling_rate": 16000, "duration": 26.227, "dataset": "Counting", "count": 6, "source_dataset": "NSynth", "source_domain": "Music", "event_label": "bass"}

{"id": "test_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Counting/wavs/test_000000.wav", "sampling_rate": 16000, "duration": 24.697, "dataset": "Counting", "count": 10, "source_dataset": "SpeechCommands", "source_domain": "Speech", "event_label": "yes"}

{"id": "test_000001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Counting/wavs/test_000001.wav", "sampling_rate": 16000, "duration": 1.604, "dataset": "Counting", "count": 1, "source_dataset": "FSD50K", "source_domain": "Audio", "event_label": "Thump, thud"}
```

---

## Task Usage

### 1. Sound Event Counting
- **Target field:** `count`
- **Task:** Predict the number of times a specific sound event occurs in the audio clip (regression or classification: 1-12)

---

## Label Space

### Count Values
<details>
<summary>Show 12 possible count values:</summary>

`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`

</details>

### Count Range
- **Range**: 1 to 12 (inclusive)
- **Type**: Integer regression or 12-class classification task
- **Interpretation**:
  - **1**: Single occurrence of the sound event
  - **2-11**: Multiple repetitions with varying temporal spacing
  - **12**: Maximum repetition count in the dataset

---

## Audio Generation Methodology

### Base Sound Extraction
- **Speech**: Random words from SpeechCommands (e.g., "yes", "seven", "stop")
- **Audio**: Short environmental sounds from FSD50K, filtered to single events using onset detection (duration < 1.0s, onset count ≤ 1)
- **Music**: Musical notes from NSynth (4-second monophonic notes)
- **Synthetic**: Procedurally generated beeps (sine waves at 220-880 Hz) and clicks (short noise bursts)

### Repetition Construction
Each audio clip is constructed by:
1. Selecting a base sound from one of the source datasets
2. Normalizing volume to **-20 dBFS RMS**
3. Repeating the sound **1-12 times** with random temporal spacing:
   - **Speech/Synthetic**: Gaps of 0.5-2.0 seconds (no overlap)
   - **Music/Audio**: Gaps of -0.25× to 1.0× base audio duration (can overlap)
4. Adding **0.5s silence** at the beginning and end
5. Clipping total duration to **30 seconds maximum**

### Audio Processing
- **Volume normalization**: All sounds normalized to -20 dBFS RMS
- **Fade in/out**: 100ms fades applied to reduce clicks (except synthetic sounds)
- **Sampling rate**: Resampled to 16 kHz if necessary
- **Format**: WAV files, 16-bit PCM

---

## Event Labels

The dataset includes **205 unique event labels** across all domains:

### Speech Labels (SpeechCommands)
Common words like: `yes`, `no`, `up`, `down`, `left`, `right`, `on`, `off`, `stop`, `go`, `zero` through `nine`, etc.

### Audio Labels (FSD50K)
Environmental sounds such as:
<details>
<summary>Show sample audio event labels:</summary>

`Accordion`, `Acoustic guitar`, `Alarm`, `Animal`, `Bark`, `Bass drum`, `Bell`, `Bicycle bell`, `Bird`, `Boiling`, `Boom`, `Breathing`, `Bus`, `Car`, `Cat`, `Chatter`, `Chewing, mastication`, `Chicken, rooster`, `Chime`, `Chink, clink`, `Chopping`, `Clapping`, `Clock`, `Cow`, `Crack`, `Creak`, `Cricket`, `Crowd`, `Crumpling, crinkling`, `Crying, sobbing`, `Cymbal`, `Dog`, `Drawer open or close`, `Drip`, `Drum`, `Engine`, `Fart`, `Fire`, `Footsteps`, `Frog`, `Glass`, `Gunshot, gunfire`, `Hammer`, `Hiss`, `Knock`, `Laughter`, `Meow`, `Music`, `Rattle`, `Roar`, `Scissors`, `Screaming`, `Sink`, `Slam`, `Sneeze`, `Snoring`, `Splash, splatter`, `Squeak`, `Stream`, `Thunder`, `Tick`, `Toilet flush`, `Traffic noise, roadway noise`, `Train`, `Trickle, dribble`, `Vacuum cleaner`, `Water tap, faucet`, `Waves, surf`, `Whispering`, `Wind`, `Writing`, and many more...

</details>

### Music Labels (NSynth)
Instrument families: `bass`, `brass`, `flute`, `guitar`, `keyboard`, `mallet`, `organ`, `reed`, `string`, `synth_lead`, `vocal`

### Synthetic Labels
- `beep`: Sine wave tones at various frequencies
- `click`: Short noise bursts

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** (1.0s to 30.0s) depending on the number of repetitions and temporal spacing.
- The `count` field represents the **actual number of events** that fit within the 30-second duration limit (may be less than the target if the base sound is very long).
- **Temporal spacing** varies by domain:
  - Speech and synthetic sounds have **positive gaps** (0.5-2.0s between events, no overlap)
  - Music and audio sounds can **overlap** (gaps from -0.25× base duration to 1.0s)
- **FSD50K sounds** are filtered to ensure single events:
  - Duration must be < 1.0s
  - Onset detection (using librosa) must detect ≤ 1 onset
- All sounds are **volume-normalized** to -20 dBFS RMS to ensure consistent loudness across different source datasets.
- The dataset is **synthetic** — all samples are procedurally generated by the `generate_manifest.py` script.
- The distribution of counts is **approximately uniform** across 1-12, with slight variation due to random sampling.
- This benchmark evaluates:
  - **Counting ability**: Can the model accurately count repetitions?
  - **Cross-domain generalization**: Performance across speech, music, audio, and synthetic sounds
  - **Temporal reasoning**: Handling variable gaps and overlaps between events
  - **Event detection**: Identifying discrete occurrences in continuous audio
- The `source_dataset`, `source_domain`, and `event_label` fields are provided for **analysis and debugging** but are not part of the primary counting task.
- Sounds from different source datasets may have different acoustic characteristics:
  - **SpeechCommands**: Short spoken words (~1s duration)
  - **FSD50K**: Diverse environmental sounds (filtered to < 1s)
  - **NSynth**: Musical notes (4s duration, can be truncated or overlapped)
  - **Beep**: Pure tones at 220-880 Hz (0.05-0.2s duration)
  - **Click**: Short percussive bursts (0.03-0.08s duration)
- The dataset is split with different random seeds:
  - **Train**: seed=888, 100,000 samples
  - **Test**: seed=999, 1,000 samples
- This ensures **no overlap** between train and test in terms of specific sound instances or repetition patterns.
