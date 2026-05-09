# Audio Activity Detection

## Overview
**Audio Activity Detection** is a synthetic dataset designed to evaluate models' ability to detect the presence of sound in audio and identify when sound is active. The dataset contains **100,000 training samples** and **1,000 test samples**, each featuring either silence or audible content at varying loudness levels. Audio clips are constructed by embedding sounds from diverse acoustic domains (speech, music, environmental audio, and synthetic sounds) into silence at random positions, with controlled loudness normalization to create different difficulty levels.

The dataset includes three audio activity categories:
- **Silence**: Pure silence with no audible content (30%)
- **Soft**: Very quiet sounds at -75 to -55 LUFS, barely audible (30%)
- **Normal**: Clearly audible sounds at typical listening levels (40%)

Sounds are sourced from five domains:
- **Speech**: Spoken content from LibriSpeech and VoxCeleb1
- **Music**: Musical content from MTG-Jamendo
- **Audio**: Environmental sounds from TUT2017 and FSD50K
- **Synthetic**: Procedurally generated pure tones and noise

All audio is sampled at **16 kHz** with durations ranging from **5-30 seconds**. This benchmark is particularly useful for evaluating audio activity detection, voice activity detection (VAD), audibility thresholds, and temporal localization capabilities.

## Supported Tasks
1. **Audibility Detection** (Binary classification: is sound present?)
2. **Audio Activity Detection** (Temporal localization: when is sound active?)

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 100,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **5.0s to 30.0s**
- Average duration: **~17.5s**
- Sampling rate: **16 kHz** for all audio files

### Audio Activity Distribution (Training Set)

| Activity Type | # Samples | Percentage | Description |
|---------------|----------:|-----------:|-------------|
| normal | 40,240 | 40.2% | Clearly audible sound |
| soft | 29,830 | 29.8% | Very quiet sound (-75 to -55 LUFS) |
| silence | 29,930 | 29.9% | Pure silence (no sound) |

### Label Distribution (Training Set)

| Label | Meaning | # Samples | Percentage |
|------:|---------|----------:|-----------:|
| 0 | Silent | 29,930 | 29.9% |
| 1 | Audible | 70,070 | 70.1% |

### Source Dataset Distribution (Training Set)

| Source Dataset | # Samples | Domain |
|----------------|----------:|--------|
| Silence | 29,930 | None |
| MTG-Jamendo | 17,614 | Music |
| TUT2017 | 9,312 | Audio |
| VoxCeleb1 | 8,747 | Speech |
| LibriSpeech | 8,742 | Speech |
| Noise | 8,734 | Synthetic |
| PureTone | 8,671 | Synthetic |
| FSD50K | 8,250 | Audio |

### Domain Distribution (Training Set)

| Domain | # Samples |
|--------|----------:|
| None (Silence) | 29,930 |
| Music | 17,614 |
| Audio | 17,562 |
| Speech | 17,489 |
| Synthetic | 17,405 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (e.g., `aad_001000`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`AudioActivityDetection`) |
| `audio_activity` | Activity category: `silence`, `soft`, or `normal` |
| `label` | Binary audibility label: 0 (silent) or 1 (audible) |
| `time_interval` | Time range `[start, end]` in seconds when sound is active, or `null` for silence |
| `domain` | Acoustic domain: `Speech`, `Music`, `Audio`, `Synthetic`, or `None` |
| `source_dataset` | Original dataset the sound was sourced from |
| `loudness_LUFS` | Integrated loudness in LUFS (ITU-R BS.1770), or `null` for silence |
| `source_metadata` | Metadata from the original source sample (varies by dataset) |

---

## Example Entries

```json
{"id": "aad_001000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AudioActivityDetection/wavs/aad_001000.wav", "sampling_rate": 16000, "duration": 22.142, "dataset": "AudioActivityDetection", "audio_activity": "normal", "label": 1, "time_interval": [3.14, 12.13], "domain": "Music", "source_dataset": "MTG-Jamendo", "loudness_LUFS": -21.24, "source_metadata": {"id": "track_0420274_30s_seg1", "sampling_rate": 16000, "duration": 30.041, "dataset": "MTG-Jamendo", "genre": ["easylistening", "electronic"], "instrument": ["piano"], "moodtheme": ["drama", "emotional", "uplifting"]}}

{"id": "aad_001001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AudioActivityDetection/wavs/aad_001001.wav", "sampling_rate": 16000, "duration": 28.725, "dataset": "AudioActivityDetection", "audio_activity": "silence", "label": 0, "time_interval": null, "domain": "None", "source_dataset": "Silence", "loudness_LUFS": null, "source_metadata": {}}

{"id": "aad_001002", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AudioActivityDetection/wavs/aad_001002.wav", "sampling_rate": 16000, "duration": 21.569, "dataset": "AudioActivityDetection", "audio_activity": "soft", "label": 1, "time_interval": [1.03, 15.41], "domain": "Speech", "source_dataset": "LibriSpeech", "loudness_LUFS": -47.41, "source_metadata": {"id": "3318-164984-0018", "duration": "14.380", "dataset": "LibriSpeech", "text": "AND FINALLY HE CLAIMED AND WAS ALLOWED A NEST OF HIS OWN IN THE WARMEST AND DARKEST NOOK OF OLD MOK'S DEN WHERE HE SLEPT EVERY NIGHT AND SOMETIMES A GOOD PART OF THE DAY WHEN ONE OF HIS TIMES OF PAIN AND WEAKNESS WAS UPON HIM", "sampling_rate": 16000}}

{"id": "aad_001009", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AudioActivityDetection/wavs/aad_001009.wav", "sampling_rate": 16000, "duration": 6.31, "dataset": "AudioActivityDetection", "audio_activity": "normal", "label": 1, "time_interval": [0.45, 4.66], "domain": "Synthetic", "source_dataset": "PureTone", "loudness_LUFS": -5.77, "source_metadata": {"frequency": 6246.33}}

{"id": "aad_000004", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AudioActivityDetection/wavs/aad_000004.wav", "sampling_rate": 16000, "duration": 12.689, "dataset": "AudioActivityDetection", "audio_activity": "silence", "label": 0, "time_interval": null, "domain": "None", "source_dataset": "Silence", "loudness_LUFS": null, "source_metadata": {}}
```

---

## Task Usage

### 1. Audibility Detection
- **Target field:** `label`
- **Task:** Binary classification — predict whether the audio contains any audible sound (1) or is completely silent (0)
- **Evaluation:** Classification accuracy, precision, recall, F1-score

### 2. Audio Activity Detection
- **Target field:** `time_interval`
- **Task:** Temporal localization — predict the time range `[start, end]` in seconds when sound is active
- **Output format:** `[start_time, end_time]` in seconds, or `null` for silent clips
- **Evaluation:** IoU (Intersection over Union), temporal boundary accuracy

---

## Label Space

### Audibility Labels
<details>
<summary>Show 2 binary labels:</summary>

- **0**: Silent — no audible content in the audio
- **1**: Audible — sound is present (may be soft or normal loudness)

</details>

### Audio Activity Categories
<details>
<summary>Show 3 activity types:</summary>

- **silence**: Pure silence, no sound present (label=0)
- **soft**: Very quiet sound at -75 to -55 LUFS, barely audible (label=1)
- **normal**: Clearly audible sound at typical listening levels (label=1)

</details>

### Time Interval Format
The `time_interval` field represents when sound is active:
- **Format**: `[start_seconds, end_seconds]` rounded to 2 decimal places
- **Range**: Times are relative to the audio clip start (0.0 to duration)
- **Null value**: `null` for clips with `label=0` (silence)
- **Detection method**: Computed by finding first and last non-zero samples in the audio waveform

---

## Audio Generation Methodology

### Sound Selection and Embedding
Each audio clip is generated through the following process:

1. **Choose activity mode** (weighted random):
   - 40% probability: `normal` (clearly audible)
   - 30% probability: `soft` (barely audible)
   - 30% probability: `silence` (no sound)

2. **Select total clip duration**: Random from 5.0 to 30.0 seconds

3. **For silence mode**:
   - Generate pure digital silence (all zeros)
   - Set `label=0`, `time_interval=null`

4. **For soft/normal modes**:
   - Choose domain: Speech, Music, Audio, or Synthetic (equal probability)
   - Load or generate sound based on domain:
     - **Speech**: Random excerpt from LibriSpeech or VoxCeleb1
     - **Music**: Random excerpt from MTG-Jamendo
     - **Audio**: Random excerpt from TUT2017 or FSD50K
     - **Synthetic**: Generate pure tone (100-8000 Hz) or noise (white/pink/brown)
   - Sound duration: Random from 1.0s to min(clip_duration - 1.0s, 30.0s)

5. **Loudness normalization**:
   - Measure integrated loudness using ITU-R BS.1770 (pyloudnorm)
   - **Soft mode**: Normalize to -75 to -55 LUFS (very quiet)
   - **Normal mode**: Normalize to -50 to -30 LUFS if originally < -55 LUFS
   - Apply safe normalization: cap boost to +20 dB, limit peaks to -0.5 dBFS

6. **Embedding**:
   - Apply 100ms fade-in/fade-out to sound
   - Insert sound at random position within silence
   - Set `time_interval=[start, end]` based on actual audio activity

### Loudness Levels
The dataset uses **ITU-R BS.1770** integrated loudness (LUFS):
- **Silence**: `null` (no sound)
- **Soft sounds**: -75 to -55 LUFS (barely perceptible, challenging for detection)
- **Normal sounds**: Typically -50 to -5 LUFS (clearly audible)

### Time Interval Recovery
The `time_interval` field is computed post-generation by:
1. Loading the audio waveform
2. Finding the first non-zero sample (start)
3. Finding the last non-zero sample (end)
4. Converting sample indices to seconds, rounded to 2 decimal places

This approach is reliable because silence regions are exactly zero in the generated audio.

---

## Source Datasets

### Speech
- **LibriSpeech**: Audiobook recordings in English
- **VoxCeleb1**: Celebrity interview audio

### Music
- **MTG-Jamendo**: Music tracks with genre, instrument, and mood annotations

### Audio (Environmental Sounds)
- **TUT2017**: Acoustic scene recordings
- **FSD50K**: Freesound dataset with diverse sound events (filtered to short sounds < 1s)

### Synthetic
- **PureTone**: Procedurally generated sine waves at 100-8000 Hz
- **Noise**: White, pink, and brown noise

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips have **variable duration** (5.0s to 30.0s).
- The dataset is **synthetic** — all samples are procedurally generated by the `generate_dataset.py` script.
- **Loudness normalization** uses the **pyloudnorm** library implementing ITU-R BS.1770-4.
- The `time_interval` field is added post-generation using the `add_vad_time_intervals.py` script.
- **70% of samples contain sound** (soft + normal), 30% are pure silence.
- The dataset evaluates:
  - **Binary audibility detection**: Can the model distinguish silence from sound?
  - **Loudness sensitivity**: Can the model detect very quiet sounds (-75 to -55 LUFS)?
  - **Temporal localization**: Can the model accurately identify when sound is active?
  - **Cross-domain robustness**: Performance across speech, music, environmental audio, and synthetic sounds
- **Soft sounds** are particularly challenging:
  - At -75 to -55 LUFS, they are barely audible even to human listeners
  - They test the model's sensitivity to low-amplitude signals
  - They simulate real-world scenarios like distant speech or quiet environmental sounds
- **Source metadata** varies by domain and includes:
  - Speech: transcriptions, speaker IDs
  - Music: genre, instruments, mood/theme tags
  - Audio: event labels, acoustic scenes
  - Synthetic: frequency (pure tones) or noise type
- The dataset is split with different random seeds:
  - **Train**: seed=42, 100,000 samples, start_id=1000
  - **Test**: seed=610, 1,000 samples, start_id=0
- **FSD50K sounds** are filtered to duration < 1.0s to ensure they represent discrete events.
- **Peak limiting** is applied to prevent clipping: audio is limited to -0.5 dBFS (≈0.94 amplitude).
- The `loudness_LUFS` field may contain `-inf` for extremely quiet or silent passages within otherwise audible clips.
- This benchmark complements traditional Voice Activity Detection (VAD) datasets by:
  - Including non-speech sounds (music, environmental audio)
  - Providing controlled loudness variations
  - Testing detection at extreme low volumes
  - Including diverse acoustic content beyond human speech
