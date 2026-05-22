# StreamSegregation

## Overview
**StreamSegregation** is a synthetic dataset designed to evaluate audio models' ability to count and identify concurrent audio streams (sources) within a mixture. The dataset contains **100,000 training samples** and **1,000 test samples**, each featuring **1-5 simultaneous audio streams** from four distinct acoustic domains: **speech**, **environmental audio**, **music**, and **synthetic sounds**. Audio mixtures are constructed by overlapping streams with random temporal offsets and normalizing each source to a target loudness range of **-28 to -22 dBFS RMS** before mixing.

The dataset aggregates sources from four domains:
- **Speech**: Read speech from LibriSpeech audiobooks
- **Audio**: Environmental sounds from ESC-50 (looped when necessary)
- **Music**: Musical instrument stems from Slakh2100 (VAD-selected segments)
- **Synthetic**: Procedurally generated pure tones with amplitude modulation

All audio is sampled at **16 kHz** and mixtures range from **6 to 30 seconds** with an average duration of **~10.7 seconds**. This benchmark is particularly useful for evaluating auditory scene analysis, source counting, stream segregation, and multi-source separation capabilities in audio understanding models.

## Supported Tasks
1. **Audio Stream Counting**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 100,000 |
| test | 1,000 |

**Sample Characteristics:**
- Duration range: **6.0s to 30.0s**
- Average duration: **~10.7s**
- Number of concurrent streams: **1 to 5**
- Sampling rate: **16 kHz** for all audio files

### Stream Count Distribution (Training Set)

| # Streams | # Samples |
|----------:|----------:|
| 1 | 30,836 |
| 2 | 24,385 |
| 3 | 19,343 |
| 4 | 14,719 |
| 5 | 10,717 |

### Source Domain Distribution (Training Set)

| Domain | # Stream Instances | Dataset |
|--------|-------------------:|---------|
| Speech | 89,376 | LibriSpeech |
| Audio | 79,811 | ESC-50 |
| Synthetic | 55,247 | Pure Tone |
| Music | 25,662 | Slakh2100 |

**Note:** Total stream instances (250,096) exceeds total samples (100,000) because each sample can contain multiple streams.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID (e.g., `streamseg_train_000000`, `streamseg_test_000000`) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`StreamSegregation`) |
| `n_streams` | Number of concurrent audio streams in the mixture (1-5) |
| `streams` | List of source dataset names for each stream |

---

## Example Entries

```json
{"id": "streamseg_train_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/StreamSegregation/wavs/train/streamseg_train_000000.wav", "sampling_rate": 16000, "duration": 14.524, "dataset": "StreamSegregation", "n_streams": 1, "streams": ["pure_tone"]}

{"id": "streamseg_train_000001", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/StreamSegregation/wavs/train/streamseg_train_000001.wav", "sampling_rate": 16000, "duration": 9.354, "dataset": "StreamSegregation", "n_streams": 5, "streams": ["pure_tone", "esc50", "esc50", "librispeech", "librispeech"]}

{"id": "streamseg_train_000002", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/StreamSegregation/wavs/train/streamseg_train_000002.wav", "sampling_rate": 16000, "duration": 7.258, "dataset": "StreamSegregation", "n_streams": 2, "streams": ["esc50", "esc50"]}

{"id": "streamseg_test_000000", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/StreamSegregation/wavs/test/streamseg_test_000000.wav", "sampling_rate": 16000, "duration": 7.944, "dataset": "StreamSegregation", "n_streams": 3, "streams": ["librispeech", "esc50", "pure_tone"]}

{"id": "streamseg_test_000002", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/StreamSegregation/wavs/test/streamseg_test_000002.wav", "sampling_rate": 16000, "duration": 9.184, "dataset": "StreamSegregation", "n_streams": 5, "streams": ["esc50", "pure_tone", "librispeech", "esc50", "librispeech"]}
```

---

## Task Usage

### 1. Audio Stream Counting
- **Target field:** `n_streams`
- **Task:** Predict the number of concurrent audio streams in the mixture (regression or classification: 1-5)

---

## Label Space

### Stream Count Values
<details>
<summary>Show 5 possible stream count values:</summary>

`1`, `2`, `3`, `4`, `5`

</details>

### Stream Count Range
- **Range**: 1 to 5 (inclusive)
- **Type**: Integer regression or 5-class classification task
- **Interpretation**:
  - **1**: Single source (isolated speech, audio, music, or synthetic tone)
  - **2-4**: Multi-source mixtures with moderate overlap
  - **5**: Maximum complexity mixtures with up to 5 simultaneous streams

### Source Dataset Labels
<details>
<summary>Show 4 possible source types:</summary>

`librispeech` - Speech streams from LibriSpeech audiobooks
`esc50` - Environmental audio streams from ESC-50
`slakh2100` - Musical instrument streams from Slakh2100
`pure_tone` - Synthetic pure tone streams with amplitude modulation

</details>

---

## Audio Generation Methodology

### Source Selection and Constraints

The dataset enforces domain-specific limits on the number of simultaneous streams:
- **Speech (LibriSpeech)**: Maximum 3 concurrent streams
- **Audio (ESC-50)**: Maximum 2 concurrent streams
- **Music (Slakh2100)**: Maximum 2 concurrent streams
- **Synthetic (Pure Tone)**: Maximum 1 stream
- **Overall maximum**: 5 concurrent streams total

### Domain-Specific Processing

#### Speech (LibriSpeech)
- **Source**: LibriSpeech ASR manifests (train/test splits matched)
- **Selection**: Random speech segments ≥5 seconds
- **Processing**: Direct crop from random starting position
- **Duration**: Uses actual audio duration (no looping)

#### Audio (ESC-50)
- **Source**: ESC-50 environmental sound dataset
- **Selection**: Random labels, then random sample from that label
- **Processing**: Looped with 20ms crossfade to reach target duration (60% probability of 2× repeat)
- **Duration**: Base duration × repeat factor (1 or 2)

#### Music (Slakh2100)
- **Source**: Slakh2100 multi-track MIDI stems (non-drum instruments only)
- **Selection**: Random instruments, VAD-selected segments on-the-fly
- **Processing**:
  - Energy-based VAD (30ms frames, 0.0005 threshold)
  - Selects loud segments (RMS ≥ 0.002)
  - Random crop from valid segment
- **Duration**: Uses actual stem segment duration

#### Synthetic (Pure Tone)
- **Generation**: Procedurally generated sine waves with amplitude modulation
- **Parameters**:
  - Frequency: 120-1600 Hz (uniform random)
  - Modulation frequency: 0.1-1.2 Hz (tremolo effect)
  - Modulation depth: 5-25%
  - Duration: 5-14 seconds (uniform random)
- **Formula**: `sin(2πft + φ) × [1 - d + d·sin(2πf_mod·t + φ)]`

### Mixture Construction

Each mixture is constructed through the following process:

1. **Stream Sampling**: Randomly select 1-5 source streams following domain constraints
2. **Duration Determination**:
   - Base duration = shortest stream duration
   - Add random extra context: 1.0-2.5 seconds
   - Clip total to maximum 30 seconds
   - Minimum mixture duration: 6 seconds (enforced by MIN_SOURCE_SEC=5.0)
3. **Stream Preparation**:
   - Load/generate each stream at target duration
   - Apply 25ms fade-in/fade-out to reduce clicks
   - Normalize each stream to -28 to -22 dBFS RMS (random target per stream)
4. **Temporal Alignment**:
   - Longest stream starts at offset 0
   - Shortest stream placed at random offset ensuring full overlap with at least one other stream
   - Intermediate streams placed between these bounds
5. **Final Mixing**:
   - Sum all streams with their assigned temporal offsets
   - Peak-normalize to 0.98 if mixture exceeds this threshold
   - Write as 16-bit PCM WAV

### Audio Processing Details
- **Volume normalization**: Each stream normalized to -28 to -22 dBFS RMS before mixing
- **Fade in/out**: 25ms applied to each stream to reduce discontinuities
- **Peak limiting**: Final mixture clipped to ±0.98 to prevent clipping
- **Sampling rate**: All sources resampled to 16 kHz
- **Format**: WAV files, 16-bit PCM

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio mixtures have **variable duration** (6.0s to 30.0s) with average ~10.7s.
- The `n_streams` field represents the **actual number of concurrent streams** in the mixture.
- The `streams` field is an **ordered list** of source dataset names, but temporal order is randomized during mixing.
- **Temporal overlap strategy**:
  - All streams are guaranteed to temporally overlap with at least one other stream
  - The shortest stream determines the minimum overlap window
  - Streams are placed with random offsets within valid bounds
- **Source diversity**:
  - Speech: Different speakers, acoustic conditions, and content
  - Audio: 50 environmental sound classes from ESC-50, potentially looped
  - Music: Various instruments from Slakh2100, VAD-selected active segments only
  - Synthetic: Pure tones with random frequency and amplitude modulation
- All sounds are **volume-normalized** before mixing to ensure consistent loudness across different source domains.
- The dataset is **synthetic** — all mixtures are procedurally generated by the `generate_manifest.py` script.
- The distribution of stream counts follows a **decreasing pattern** (more single-stream samples than 5-stream samples), reflecting natural variability.
- This benchmark evaluates:
  - **Stream counting ability**: Can the model accurately count concurrent sources?
  - **Cross-domain discrimination**: Performance across speech, music, environmental audio, and synthetic sounds
  - **Cocktail party problem**: Separating and identifying multiple simultaneous audio streams
  - **Auditory scene analysis**: Understanding complex acoustic mixtures
- The `streams` field provides **ground-truth source composition** for analysis but lists datasets, not semantic content:
  - Models must infer the number and types of streams from audio alone
  - Multiple instances of the same source type (e.g., two `librispeech` streams) represent different speakers or utterances
- **ESC-50 sound classes** may repeat when `repeat_factor=2` (60% probability), creating longer environmental sound loops
- **Slakh2100 music stems** undergo on-the-fly VAD to ensure active musical content:
  - Excludes silent or very quiet segments
  - Selects from loud, continuous musical passages
  - Does not rely on pre-computed segment indices (fully reproducible)
- The dataset uses different random seeds for splits:
  - **Train**: base seed=610, samples 0-99,999
  - **Test**: base seed=10,000,610, samples 0-999
- This ensures **no overlap** between train and test in terms of:
  - Specific source audio instances
  - Mixture configurations
  - Temporal alignments
- **Challenges** for models:
  - **Variable stream count**: Must handle 1-5 sources
  - **Domain diversity**: Speech, music, environmental sounds, and synthetic tones have very different characteristics
  - **Temporal overlap**: Streams may fully or partially overlap in time
  - **Volume variation**: Each stream has independently randomized loudness
  - **Mixture ambiguity**: Multiple sources may blend perceptually
- **Applications** include:
  - **Audio source separation**: Identifying and separating concurrent sources
  - **Acoustic scene analysis**: Understanding complex soundscapes
  - **Multi-speaker detection**: Counting overlapping speakers
  - **Sound event detection**: Identifying multiple simultaneous events
  - **Auditory attention**: Modeling selective attention to specific streams

---

## Source Datasets

This dataset is built from the following source datasets:

### LibriSpeech
- **Type**: Speech (read audiobooks)
- **Usage**: Speech streams
- **Reference**: http://www.openslr.org/12/
- **Manifest**: `FullSpectrumDataset/metadata/LibriSpeech/ASR/`

### ESC-50
- **Type**: Environmental sounds
- **Usage**: Audio streams (looped)
- **Classes**: 50 environmental sound categories
- **Reference**: https://github.com/karolpiczak/ESC-50
- **Manifest**: `FullSpectrumDataset/metadata/ESC50/`

### Slakh2100
- **Type**: Multi-track MIDI music
- **Usage**: Music streams (VAD-selected segments)
- **Instruments**: Various (drums excluded)
- **Reference**: http://www.slakh.com/
- **Note**: Uses FLAC stems from `slakh2100_flac_redux`

### Pure Tone (Synthetic)
- **Type**: Procedurally generated
- **Usage**: Synthetic streams
- **Generation**: Sine waves with amplitude modulation (tremolo)
- **Parameters**: Random frequency (120-1600 Hz), modulation (0.1-1.2 Hz, 5-25% depth)

---

## Citation

If using this dataset, please cite the source datasets:

```bibtex
@inproceedings{panayotov2015librispeech,
  title={Librispeech: An ASR corpus based on public domain audio books},
  author={Panayotov, Vassil and Chen, Guoguo and Povey, Daniel and Khudanpur, Sanjeev},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={5206--5210},
  year={2015},
  organization={IEEE}
}

@inproceedings{piczak2015esc,
  title={ESC: Dataset for Environmental Sound Classification},
  author={Piczak, Karol J},
  booktitle={Proceedings of the 23rd ACM International Conference on Multimedia},
  pages={1015--1018},
  year={2015}
}

@inproceedings{manilow2019slakh,
  title={Cutting Music Source Separation Some Slakh: A Dataset to Study the Impact of Training Data Quality and Quantity},
  author={Manilow, Ethan and Wichern, Gordon and Seetharaman, Prem and Le Roux, Jonathan},
  booktitle={IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA)},
  pages={45--49},
  year={2019},
  organization={IEEE}
}
```

## References
- LibriSpeech: http://www.openslr.org/12/
- ESC-50: https://github.com/karolpiczak/ESC-50
- Slakh2100: http://www.slakh.com/
- Generation script: [generate_manifest.py](generate_manifest.py)
