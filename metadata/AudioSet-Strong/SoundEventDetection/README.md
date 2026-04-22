# AudioSet-Strong - Sound Event Detection

## Overview
**AudioSet-Strong** is a temporally annotated extension of AudioSet in which sound events are labeled with **start and end times**, making it useful for sound event detection and other tasks that require fine-grained event timing rather than only clip-level tags. The dataset includes **strong labels** (temporal boundaries) for all **16,996 available clips** in the original AudioSet evaluation set plus **103,463 randomly chosen training clips**, with **456 distinct event labels** in total. Audio is recorded at **16 kHz** and clips are typically **10 seconds** long, extracted from YouTube videos covering diverse real-world acoustic scenes.

Unlike the original AudioSet which provides only clip-level weak labels, AudioSet-Strong annotates the **precise temporal boundaries** of each sound event, enabling research in sound event detection, temporal localization, and other fine-grained audio understanding tasks.

## Supported Tasks
1. **Sound Event Detection (SED)**
2. **Query-Conditioned Sound Event Temporal Localization**
3. **Temporal Order Reasoning**

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
| `events` | Temporal event annotations in format `[start-end] Label` (newline-separated) |

---

## Example Entries

```json
{"id": "--4gqARaEJE_0", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/eval/--4gqARaEJE.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet-Strong", "events": "[2.29-3.51] Squeak\n[3.46-4.32] Dog\n[4.82-5.48] Squeak\n[5.62-6.69] Squeak\n[7.50-7.87] Dog\n[8.39-9.39] Squeak\n[8.82-9.16] Dog\n[9.44-9.68] Dog\n[9.63-10.00] Squeak"}

{"id": "--BfvyPmVMo_20000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/eval/--BfvyPmVMo.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet-Strong", "events": "[0.00-10.00] Mechanisms\n[3.02-3.52] Hammer\n[6.39-6.66] Hammer\n[6.91-7.17] Hammer\n[7.58-10.00] Male speech, man speaking"}

{"id": "--24LG2mr-Y_8000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/--24LG2mr-Y.wav", "sampling_rate": 16000, "duration": 9.984, "dataset": "AudioSet-Strong", "events": "[0.00-0.19] Female singing\n[0.00-9.11] Music\n[1.04-2.47] Female singing\n[3.17-9.11] Female singing"}
```

---

## Task Usage

### 1. Sound Event Detection (SED)
- **Target field:** `events` (temporal event boundaries and labels)
- **Task:** Detect all sound events and predict their start times, end times, and class labels

### 2. Query-Conditioned Sound Event Temporal Localization
- **Input:** Audio clip + query event label
- **Target field:** `events` (filtered for query event)
- **Task:** Given a query event class, predict all temporal boundaries where that event occurs

### 3. Temporal Order Reasoning
- **Target field:** `events` (temporal sequence)
- **Task:** Reason about the temporal ordering of sound events (e.g., "Does event A occur before event B?")

---

## Event Format

The `events` field contains newline-separated temporal annotations in the format:
```
[start_time-end_time] Event_Label
```

**Format details:**
- **start_time**: Event start time in seconds (e.g., `2.29`)
- **end_time**: Event end time in seconds (e.g., `3.51`)
- **Event_Label**: Human-readable event class name (e.g., `Dog`, `Female singing`)

**Properties:**
- Events can **overlap** in time (polyphonic detection)
- Multiple instances of the same event can occur in one clip
- Events are sorted chronologically by start time
- Background/ambient events may span the entire clip duration (e.g., `[0.00-10.00] Music`)

---

## Label Space

### Sound Event Classes
<details>
<summary>Show 456 available event labels:</summary>

The dataset uses the AudioSet ontology with 456 sound event classes including:

**Human sounds**: Speech, singing, laughter, crying, breathing, coughing, sneezing, etc.
**Animal sounds**: Dog, cat, bird, insect, roar, meow, bark, chirp, etc.
**Musical instruments**: Piano, guitar, drums, violin, trumpet, saxophone, etc.
**Music genres**: Music, rock music, pop music, jazz, classical, etc.
**Natural sounds**: Rain, wind, thunder, water, fire, ocean, stream, etc.
**Vehicle sounds**: Car, truck, motorcycle, aircraft, train, bus, engine, etc.
**Domestic sounds**: Door, alarm, bell, telephone, appliance, dishes, etc.
**Tools and machinery**: Hammer, drill, saw, machine gun, chainsaw, etc.
**Environmental sounds**: Explosion, gunshot, fireworks, siren, horn, etc.

**Note:** The complete list of 456 event labels follows the AudioSet ontology. Common labels include `Generic impact sounds`, `Surface contact`, `Male speech, man speaking`, `Female singing`, `Music`, `Dog`, `Mechanisms`, `Medium engine (mid frequency)`, etc.

</details>

### Event Statistics
- **Total unique event classes**: 456
- **Events per clip**: Ranges from 1 to 40+, average ~9 events per clip
- **Event duration**: Highly variable, from <0.1s (e.g., impact sounds) to 10s (background events)
- **Polyphonic events**: Multiple events frequently occur simultaneously

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips typically have **10-second duration** (some may be slightly shorter).
- This dataset provides **strong labels** (temporal boundaries) unlike the original AudioSet which has only **weak labels** (clip-level tags).
- The `id` field format is `{youtube_id}_{start_time_ms}`, where start_time_ms indicates the offset in the original YouTube video.
- **Temporal annotations** were created through:
  - Manual annotation by human annotators
  - Listening to audio and marking precise event boundaries
  - Quality control to ensure temporal accuracy
- **Polyphonic nature**: Clips often contain multiple overlapping events:
  - Example: Music playing while someone speaks and a dog barks
  - Models must detect all concurrent events and their boundaries
- **Event granularity varies**:
  - **Short events**: Generic impact sounds (~0.1-0.3s)
  - **Medium events**: Dog barks, speech utterances (~1-3s)
  - **Long events**: Background music, ambient sounds (up to 10s)
- **Evaluation metrics** for Sound Event Detection:
  - **Segment-based F1**: F1 score computed on fixed time segments (e.g., 1-second windows)
  - **Event-based F1**: F1 score for event instances with collar-based matching
  - **Intersection over Union (IoU)**: Temporal overlap between predicted and ground-truth events
  - **Collar-based scoring**: Events matched if temporal overlap exceeds threshold (e.g., 200ms collar)
- This dataset captures **real-world acoustic complexity**:
  - Background noise and reverberation
  - Multiple simultaneous sound sources
  - Variable recording conditions (indoor/outdoor, different microphones)
  - Spontaneous and scripted content
  - Music, speech, environmental sounds, and their combinations
- **Query-Conditioned Temporal Localization** enables:
  - Searching for specific sound events within long recordings
  - Zero-shot detection of new event types via text queries
  - Fine-grained retrieval: "Find all segments containing dog barks"
- **Temporal Order Reasoning** tasks include:
  - "Does the door slam occur before or after the dog barks?"
  - "What sound event happens first in this clip?"
  - Understanding causal relationships between events

---

## Differences from Original AudioSet

| Feature | AudioSet (Original) | AudioSet-Strong |
|---------|---------------------|-----------------|
| **Label type** | Weak (clip-level tags) | Strong (temporal boundaries) |
| **Annotation format** | List of present event classes | `[start-end] Label` for each event instance |
| **Temporal information** | None | Precise start/end times in seconds |
| **Coverage** | 2M+ clips (full dataset) | ~120K clips (subset with strong labels) |
| **Primary task** | Audio tagging / classification | Sound event detection / temporal localization |
| **Evaluation** | Clip-level accuracy / mAP | Segment/event-based F1, IoU |

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
