# SpatialAudio / SpatialSoundQA

## Overview
**SpatialSoundQA** is a large-scale question-answering benchmark for spatial sound perception and reasoning, built on synthesized binaural audio from the combination of AudioSet sound events and spatial acoustic simulation from SoundSpaces 2.0. The dataset contains **201,220 training samples** and **3,500 test samples** covering diverse spatial audio understanding tasks including sound event detection, sound source localization, distance estimation, and relational reasoning between multiple sound sources in 3D space. Audio is rendered as binaural recordings at **32 kHz** with realistic room acoustics and head-related transfer functions (HRTFs), simulating immersive spatial audio experiences.

## Supported Tasks
1. **Spatial Sound Event Detection**
2. **Sound Source Localization**
3. **Distance Estimation**
4. **Spatial Reasoning QA**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 201,220 |
| test | 3,500 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample identifier (includes stage and category info) |
| `path` | Path to binaural audio file |
| `sampling_rate` | Audio sampling rate (32000 Hz) |
| `duration` | Audio duration in seconds (typically 10.0) |
| `dataset` | Source dataset (SpatialSoundQA) |
| `question` | Natural language question about the spatial audio |
| `answer` | Ground-truth answer (format varies by task type) |

---

## Example Entries

```json
{"id": "stage3-mixup-000002", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpatialAudio/binaural_wavs/stage3-mixup/stage3-mixup-000002.wav", "sampling_rate": 32000, "duration": 10.0, "dataset": "SpatialSoundQA", "question": "How would you express the spatial source of this sound clip?", "answer": "right, behind, above; 3.5m"}

{"id": "stage3-mixup-000014", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpatialAudio/binaural_wavs/stage3-mixup/stage3-mixup-000014.wav", "sampling_rate": 32000, "duration": 10.0, "dataset": "SpatialSoundQA", "question": "What are the distinct sounds present in this audio clip originating from the right, front, above, about 4 meters distant?", "answer": "clock; music"}

{"id": "stage3-mixup-000018", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpatialAudio/binaural_wavs/stage3-mixup/stage3-mixup-000018.wav", "sampling_rate": 32000, "duration": 10.0, "dataset": "SpatialSoundQA", "question": "Regarding linear distance, is the origin of the sound of music further from you than that of cash register?", "answer": "No"}

{"id": "eval-stage1-classification-000000", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/SpatialAudio/binaural_wavs/eval-stage1-classification/eval-stage1-classification-000000.wav", "sampling_rate": 32000, "duration": 10.0, "dataset": "SpatialSoundQA", "question": "What sound events can you detect in the audio recording?", "answer": "drum; percussion; tabla"}
```

---

## Task Usage

### 1. Spatial Sound Event Detection
- **Target field:** `answer` (semicolon-separated list of sound event labels)
- **Question patterns:**
  - "What sound events can you detect in the audio recording?"
  - "Identify the sound events in the audio clip."
  - "Determine the types of sounds present in the audio clip."

### 2. Sound Source Localization
- **Target field:** `answer` (spatial coordinates in format: "direction; distance")
- **Question patterns:**
  - "How would you express the spatial source of this sound clip?"
  - "From your standpoint, where exactly, considering direction and distance, is the sound of the [event]?"
  - "From which direction and at what distance can the sound of the [event] be detected?"
- **Answer format:** Directional descriptors (left/right, front/behind, above/below) followed by distance in meters
  - Example: "right, behind, above; 3.5m"

### 3. Distance Estimation
- **Target field:** `answer` (distance value with unit)
- **Question patterns:**
  - "How far away is the sound of the [event1] from the sound of the [event2]?"
  - "What is the distance between the sound of the [event1] and the sound of the [event2]?"
  - "How many meters or feet apart are the sounds of the [event1] and the [event2]?"
- **Answer format:** Distance in meters (e.g., "2m", "7m")

### 4. Spatial Reasoning QA
- **Target field:** `answer` (task-dependent: binary, categorical, or descriptive)
- **Sub-tasks include:**
  - **Distance comparison:** Binary yes/no answers comparing relative distances
    - "Is the sound from [event1] further away from you than the sound from [event2]?"
  - **Relational positioning:** Binary answers about shared directional attributes
    - "Are the sound of [event1] and the sound of [event2] both positioned to your left?"
  - **Conditional detection:** Multi-label detection with spatial constraints
    - "What are the distinct sounds present originating from the left, front, below, about 2.5 meters distant?"
  - **Directional queries:** Categorical answers (left/right/front/behind/above/below)
    - "Does the sound from [event1] emanate from the left or right side of [event2]'s sound?"

---

## Question Type Distribution

### Test Set Breakdown (3,500 samples)

| Question Type | Count | Percentage |
|---------------|------:|-----------:|
| Sound Event Detection | 512 | 14.6% |
| Sound Source Localization | 831 | 23.7% |
| Distance Estimation | 113 | 3.2% |
| Distance Comparison | 398 | 11.4% |
| Relational Positioning | 120 | 3.4% |
| Conditional Detection | 159 | 4.5% |
| Other Spatial Reasoning | 1,367 | 39.1% |

---

## Answer Format Taxonomy

### 1. Multi-label Detection
- **Format:** Semicolon-separated event labels
- **Example:** `"drum; percussion; tabla"`

### 2. Spatial Coordinates
- **Format:** Direction descriptors + distance
- **Example:** `"left, front, below; 3.5m"`
- **Direction components:**
  - Lateral: `left` or `right`
  - Sagittal: `front` or `behind`
  - Vertical: `above` or `below`

### 3. Distance Values
- **Format:** Numeric value + unit (meters)
- **Example:** `"2m"`, `"7m"`

### 4. Binary Answers
- **Format:** `"Yes"` or `"No"`
- **Used for:** Distance comparisons, relational queries

### 5. Categorical Directional
- **Format:** Single directional descriptor
- **Example:** `"left"`, `"right"`, `"above"`

### 6. Single Event Label
- **Format:** Single sound event name
- **Example:** `"squeak"`

---

## Dataset Construction

### Audio Synthesis Pipeline

1. **Source Material:**
   - Sound events from **AudioSet** corpus
   - Room impulse responses from **SoundSpaces 2.0** (based on Matterport3D scenes)

2. **Spatial Rendering:**
   - Binaural audio synthesis using head-related transfer functions (HRTFs)
   - Realistic room acoustics simulation
   - Multiple sound sources positioned in 3D space

3. **Spatial Configuration:**
   - **Directional dimensions:** 3-axis positioning (left/right, front/behind, above/below)
   - **Distance range:** 1m to 10m from listener
   - **Multi-source scenes:** Up to multiple simultaneous sound sources

4. **Training Stages:**
   - **Stage 1 (clsdoa):** Single-source classification and direction-of-arrival
   - **Stage 2 (single):** Single-source with full spatial attributes
   - **Stage 3 (mixup):** Multi-source scenes with complex spatial reasoning

---

## Notes
- All audio files are sampled at **32 kHz** in **WAV format**.
- Audio clips have **fixed duration of 10 seconds**.
- Audio is **binaural stereo**, simulating human spatial hearing with left/right ear channels.
- The dataset uses **synthesized audio** to ensure precise ground-truth spatial labels.
- **Question diversity:** Over **59,000 unique question templates** in the training set.
- Spatial coordinates use a **listener-centric reference frame** (egocentric coordinates).
- Distance measurements are **Euclidean distances** in 3D space.
- The dataset supports both **audio-only** and **audio-language** multimodal learning.
- Sound events are sourced from **AudioSet ontology**, covering diverse acoustic categories.
- Room acoustics include realistic **reverberation** and **occlusion** effects from SoundSpaces 2.0.
- The benchmark is designed to evaluate:
  - **Spatial audio understanding:** Perception of sound location and distance in 3D
  - **Multi-source scene analysis:** Handling multiple simultaneous sound sources
  - **Audio-language reasoning:** Answering natural language questions about spatial audio
  - **Binaural processing:** Leveraging inter-aural cues for spatial perception
- **Evaluation metrics:**
  - **Detection:** Precision, Recall, F1-score for multi-label classification
  - **Localization:** Angular error (degrees), distance error (meters)
  - **QA:** Exact match accuracy, relaxed accuracy for numerical answers
  - **Distance estimation:** Mean Absolute Error (MAE), Root Mean Square Error (RMSE)
- The binaural rendering preserves **inter-aural time differences (ITD)** and **inter-aural level differences (ILD)** that humans use for sound localization.
