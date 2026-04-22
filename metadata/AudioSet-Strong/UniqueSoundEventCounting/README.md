# AudioSet-Strong - Unique Sound Event Counting

## Overview
**AudioSet-Strong** is a temporally annotated extension of AudioSet in which sound events are labeled with **start and end times**, making it useful for sound event detection and other tasks that require fine-grained event timing. This **Unique Sound Event Counting** subset focuses on counting the number of **distinct sound event types** present in each audio clip, regardless of how many times each event occurs.

The dataset contains the same **101,791 training clips** and **16,678 test clips** as the Sound Event Detection subset, with **456 distinct event labels** in total. Audio is recorded at **16 kHz** and clips are typically **10 seconds** long, extracted from YouTube videos covering diverse real-world acoustic scenes. Unlike sound event detection which requires predicting temporal boundaries, this task focuses on **enumerating unique event types** present in the audio.

## Supported Tasks
1. **Unique Sound Event Counting**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 101,791 |
| test | 16,678 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID (YouTube video ID + start time in milliseconds) |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `events_list` | List of unique sound event labels present in the clip |
| `num_events` | Count of unique sound event types (target for regression/classification) |

---

## Example Entries

```json
{"id": "--4gqARaEJE_0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/eval/--4gqARaEJE.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet-Strong", "events_list": ["Squeak", "Dog"], "num_events": 2}

{"id": "--BfvyPmVMo_20000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/eval/--BfvyPmVMo.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet-Strong", "events_list": ["Mechanisms", "Hammer", "Male speech, man speaking"], "num_events": 3}

{"id": "--i-y1v8Hy8_0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/eval/--i-y1v8Hy8.wav", "sampling_rate": 16000, "duration": 8.672, "dataset": "AudioSet-Strong", "events_list": ["Hubbub, speech noise, speech babble", "Music", "Child speech, kid speaking", "Male speech, man speaking", "Shout", "Laughter"], "num_events": 6}

{"id": "--330hg-Ocw_30000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/--330hg-Ocw.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet-Strong", "events_list": ["Medium engine (mid frequency)", "Generic impact sounds", "Surface contact"], "num_events": 3}
```

---

## Task Usage

### 1. Unique Sound Event Counting
- **Target field:** `num_events` (count of unique event types)
- **Task:** Predict the number of distinct sound event types present in the audio clip
- **Formulation:** Can be treated as either:
  - **Regression**: Predict the exact count as a continuous value
  - **Classification**: Classify into discrete count bins (1-16 classes)

---

## Count Distribution

### Event Count Statistics (Training Set)

| Count | # Samples | Percentage |
|------:|----------:|-----------:|
| 1 | 8,298 | 8.2% |
| 2 | 15,907 | 15.6% |
| 3 | 18,486 | 18.2% |
| 4 | 18,441 | 18.1% |
| 5 | 15,363 | 15.1% |
| 6 | 11,049 | 10.9% |
| 7 | 7,004 | 6.9% |
| 8 | 3,818 | 3.8% |
| 9 | 2,031 | 2.0% |
| 10+ | 1,394 | 1.4% |

**Summary statistics:**
- **Minimum count**: 1 unique event
- **Maximum count**: 16 unique events
- **Average count**: 4.18 unique events per clip
- **Most common**: 3-4 unique events per clip (36.3% combined)

The distribution shows that most clips contain **2-6 unique event types**, with a long tail of clips containing many simultaneous events.

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips typically have **10-second duration** (some may be slightly shorter).
- This task focuses on **counting unique event types**, not counting individual event instances:
  - Example: If a dog barks 5 times in a clip, it counts as **1 unique event type** (Dog)
  - If a dog barks and a person speaks, it counts as **2 unique event types**
- The `events_list` field provides the actual event labels for reference and analysis, but models should predict `num_events`.
- **Relationship to Sound Event Detection**:
  - Same audio clips and event annotations
  - SED task: Predict what events occur and when (temporal boundaries)
  - Counting task: Predict how many unique event types occur (no temporal information needed)
- **Task difficulty factors**:
  - **Polyphonic complexity**: More simultaneous events makes counting harder
  - **Overlapping sounds**: Difficult to distinguish individual event types
  - **Event similarity**: Similar-sounding events may be miscounted
  - **Background noise**: May introduce spurious event detections
- **Evaluation metrics**:
  - **Mean Absolute Error (MAE)**: Average absolute difference between predicted and true counts
  - **Mean Squared Error (MSE)**: Squared differences, penalizing larger errors more
  - **Accuracy**: Percentage of exact count predictions (for classification approach)
  - **Off-by-one accuracy**: Percentage within ±1 of true count
  - **Correlation**: Pearson or Spearman correlation with ground truth counts
- The dataset is particularly challenging due to:
  - **Class imbalance**: Few clips with very high event counts (10+)
  - **Perceptual difficulty**: Humans may also struggle to count events in dense polyphonic scenes
  - **Ambiguous boundaries**: Some events are hierarchical (e.g., "Music" vs. "Piano" vs. "Classical music")
  - **Overlapping events**: Simultaneous events can mask each other
- **Comparison to event detection**:
  - Simpler task (no temporal localization required)
  - Still requires recognizing all event types present
  - Can be solved with clip-level models (no need for frame-level predictions)
  - Lower computational cost than full detection
- The `events_list` field is derived from the temporal annotations in the Sound Event Detection subset by extracting unique event labels.
- **Important distinction**: This counts **types** not **instances**:
  - A clip with 10 dog barks has `num_events=1` if only dogs are present
  - A clip with 1 bark and 1 meow has `num_events=2`
- The count distribution is **approximately normal** centered around 3-4 events, with slight right skew due to high-complexity clips.

---

## Relationship to Sound Event Detection

This counting task is derived from the AudioSet-Strong Sound Event Detection annotations:

| Feature | Sound Event Detection | Unique Event Counting |
|---------|----------------------|----------------------|
| **Input** | Audio clip | Audio clip |
| **Output** | Event labels + temporal boundaries | Number of unique event types |
| **Temporal info** | Required (start/end times) | Not required |
| **Task type** | Structured prediction | Regression/Classification |
| **Complexity** | High (predict segments + labels) | Medium (predict single number) |
| **Model output** | Frame-level predictions | Clip-level prediction |

**Derivation**: The `num_events` and `events_list` fields are computed from the temporal annotations by:
1. Parsing all events in the clip
2. Extracting unique event labels (removing duplicates)
3. Counting the number of unique labels

---

## Citation

If using this dataset, please cite:

```bibtex
@inproceedings{hershey2021audioset,
  title={The Benefit of Temporally-Strong Labels in Audio Event Classification},
  author={Hershey, Shawn and Ellis, Daniel PW and Fonseca, Eduardo and Jansen, Aren and Liu, Caroline and Moore, R Channing and Plakal, Manoj},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={366--370},
  year={2021},
  organization={IEEE}
}

@inproceedings{gemmeke2017audioset,
  title={Audio Set: An Ontology and Human-Labeled Dataset for Audio Events},
  author={Gemmeke, Jort F and Ellis, Daniel PW and Freedman, Dylan and Jansen, Aren and Lawrence, Wade and Moore, R Channing and Plakal, Manoj and Ritter, Marvin},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={776--780},
  year={2017},
  organization={IEEE}
}
```

## References
- AudioSet website: https://research.google.com/audioset/
- AudioSet ontology: https://research.google.com/audioset/ontology/index.html
- AudioSet-Strong paper: https://research.google/pubs/pub50298/
- Original AudioSet paper: https://research.google.com/pubs/pub45857/
