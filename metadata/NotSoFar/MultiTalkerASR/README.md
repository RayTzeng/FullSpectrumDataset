# NOTSOFAR - Multi-Talker ASR

## Overview
**NOTSOFAR** (Natural Office Talkers in Settings of Far-field Audio Recordings) is a far-field meeting speech corpus introduced for the **NOTSOFAR-1 Challenge**, targeting distant automatic speech recognition and speaker diarization in realistic conference-room settings. The original benchmark includes roughly **315 English meetings** recorded across **30 rooms** with **4-8 attendees** per meeting, emphasizing natural multi-speaker overlap, reverberation, and challenging microphone conditions.

This metadata release provides a **segmented far-field meeting transcription** view of the corpus for **multi-talker ASR**, **speaker diarization**, and **speaker counting**. Each entry contains a short audio segment, a speaker-attributed transcript, the list of active speakers in that segment, and timestamped speaker-turn annotations. Audio is stored at **16 kHz** and segment durations are capped at **30 seconds**.

## Supported Tasks
1. **Speaker-attributed ASR**
2. **Speaker Diarization**
3. **Speaker Counting**

---

## Dataset Statistics

| Split | # Segments |
|-------|-----------:|
| train | 4,731 |
| dev | 2,458 |
| test | 2,230 |

**Segment Characteristics:**
- Average duration: **27.53s** (train), **26.94s** (dev), **27.28s** (test)
- Duration range: **0.27s to 30.0s**
- Sampling rate: **16 kHz** for all segments

**Speaker Count per Segment:**
- Train: **1-8 speakers**
- Dev: **1-7 speakers**
- Test: **1-7 speakers**

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment ID |
| `path` | Path to the far-field audio segment |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`NotSoFar`) |
| `speakers` | List of unique speaker names active in the segment |
| `transcript` | Speaker-attributed transcript using `SpeakerNN:` line prefixes |
| `timestamps` | Newline-separated speaker-turn annotations in format `[start-end] SpeakerNN` |

---

## Example Entries

```json
{"id": "sdm_MTG_30830_sc_meetup_0-0-1-0-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/NotSoFar/wav_segments/sdm_MTG_30830_sc_meetup_0-0-1-0-0.wav", "sampling_rate": 16000, "duration": 29.24, "dataset": "NotSoFar", "speakers": ["Sophie", "Peter"], "transcript": "Speaker01: So AI in schools? It's really interesting. I mean I think it helps me a lot with everything that I need to do, makes me work a lot less hard\nSpeaker01: which is a good thing and a bad thing. What do you think?\nSpeaker02: I think schools are about preparing children for\nSpeaker02: the adulthood.\nSpeaker02: and I actually think schools need to up their game a bit, because it's like\nSpeaker02: the real world or the world after school is advancing with AI and technology extensively\nSpeaker02: But schools are still kind of in their traditional way, figuring out, there have been some changes", "timestamps": "[0.0-6.7] Speaker01\n[7.0-9.1] Speaker01\n[9.3-12.4] Speaker02\n[12.9-13.9] Speaker02\n[14.1-17.9] Speaker02\n[18.0-24.1] Speaker02\n[24.4-29.2] Speaker02"}

{"id": "sdm_MTG_30860_sc_meetup_0-0-1-0-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/NotSoFar/wav_segments/sdm_MTG_30860_sc_meetup_0-0-1-0-0.wav", "sampling_rate": 16000, "duration": 29.64, "dataset": "NotSoFar", "speakers": ["Peter", "Ernie", "Walter"], "transcript": "Speaker01: So guys, we need to come up with an idea\nSpeaker01: to create a car that is revolutionary.\nSpeaker01: Now personally the one thing I hate about cars is sitting in traffic. So, how is our car\nSpeaker01: going to avoid traffic completely? What do you guys think? Do you have any ideas? .\nSpeaker02: Hmm.\nSpeaker03: Well have you ever seen backseat feature?\nSpeaker01: Yes.\nSpeaker01: One of my best movies, I've seen it like three times.\nSpeaker02: I was thinking like no wheels.\nSpeaker01: No wheels, so how do we move around?\nSpeaker02: No wheels.\nSpeaker02: We were the only car that can fly.\nSpeaker01: Whoa! But then we need a patent.\nSpeaker02: every other car is on the ground.\nSpeaker01: Because if other cars\nSpeaker02: OK.", "timestamps": "[0.0-3.2] Speaker01\n[3.3-5.7] Speaker01\n[5.8-11.6] Speaker01\n[11.9-15.4] Speaker01\n[12.0-12.3] Speaker02\n[14.5-16.3] Speaker03\n[16.3-17.0] Speaker01\n[17.1-19.5] Speaker01\n[19.0-20.7] Speaker02\n[21.0-23.0] Speaker01\n[21.1-21.9] Speaker02\n[22.8-24.6] Speaker02\n[24.7-27.7] Speaker01\n[25.1-26.5] Speaker02\n[27.8-29.6] Speaker01\n[28.4-29.1] Speaker02"}

{"id": "sdm_MTG_32000_sc_meetup_0-0-1-0-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/NotSoFar/wav_segments/sdm_MTG_32000_sc_meetup_0-0-1-0-0.wav", "sampling_rate": 16000, "duration": 29.96, "dataset": "NotSoFar", "speakers": ["Rachel", "Linda", "Sarah"], "transcript": "Speaker01: Hello my friends, we're gonna start the meeting now, talking about this new uh\nSpeaker01: um a park that we're going to create in center of the town. What are your suggestions?\nSpeaker01: Um\nSpeaker01: Linda ?\nSpeaker02: OK, uh where do we want to start? We have a Do we have an exact uh map of the of the location for everybody?\nSpeaker01: Don't start.\nSpeaker03: I\nSpeaker03: I think the\nSpeaker03: green there should be greenery. Should There should be trees.\nSpeaker01: Yes.\nSpeaker01: but she was the asking a question, so maybe we", "timestamps": "[0.0-4.0] Speaker01\n[4.2-9.8] Speaker01\n[10.4-10.8] Speaker01\n[10.8-11.4] Speaker01\n[12.0-18.4] Speaker02\n[19.0-20.5] Speaker01\n[19.3-19.7] Speaker03\n[19.9-22.7] Speaker03\n[22.9-26.3] Speaker03\n[26.0-26.6] Speaker01\n[26.8-30.0] Speaker01"}
```

---

## Task Usage

### 1. Speaker-attributed ASR
- **Input:** Far-field meeting audio segment
- **Target field:** `transcript`
- **Task:** Generate the transcript with speaker attribution preserved via `SpeakerNN:` prefixes

### 2. Speaker Diarization
- **Input:** Far-field meeting audio segment
- **Target field:** `timestamps`
- **Task:** Predict who spoke when using timestamped speaker-turn boundaries

### 3. Speaker Counting
- **Input:** Far-field meeting audio segment
- **Target field:** `speakers`
- **Task:** Predict the number of distinct active speakers in the segment, i.e., `len(speakers)`

---

## Label Space

### Speaker Attribution Format
- The `transcript` field uses canonical placeholders such as `Speaker01`, `Speaker02`, and `Speaker03`.
- These placeholders are local to each segment and provide a consistent ordering for the attributed transcript and timestamps.
- The `speakers` field contains the corresponding human-readable speaker names active in the segment.

### Timestamp Format

The `timestamps` field contains newline-separated speaker turns in the format:

```text
[start_time-end_time] SpeakerNN
```

**Properties:**
- `start_time` and `end_time` are given in seconds
- Speaker turns can **overlap**
- The format is suitable for diarization evaluation and turn-boundary supervision
- `SpeakerNN` identifiers align with the prefixes used in `transcript`

### Speaker Count
- Speaker counting is derived from the number of distinct names in `speakers`
- Segment-level counts range from **1 to 8 speakers** in the provided manifests

---

## Notes
- All audio segments are sampled at **16 kHz**.
- The manifests in this directory are **segmented excerpts**, not full meetings. Most segments are close to **30 seconds** long.
- The source domain is **far-field meeting speech**, so audio may contain:
  - Reverberation
  - Background room noise
  - Overlapping speech
  - Distant microphone effects
- The `transcript` field in the default manifests (`train.jsonl.gz`, `dev.jsonl.gz`, `test.jsonl.gz`) has been cleaned into a readable speaker-attributed format using `SpeakerNN:` line prefixes.
- Companion files `train_unfiltered.jsonl.gz`, `dev_unfiltered.jsonl.gz`, and `test_unfiltered.jsonl.gz` preserve the original transcript text before cleaning.
- The script [filter_notsofar_fillers.py](/home/tseng/FullSpectrumDataset/metadata/NotSoFar/MultiTalkerASR/filter_notsofar_fillers.py) documents the cleanup step:
  - Removes most inline filler tags
  - Preserves `<PAUSE/>`
  - Converts `<FILLlaugh/>` to `<LAUGH/>`
  - Drops segments only if a cleaned speaker segment becomes empty
- The `timestamps` field provides speaker-turn timing only; lexical content is stored separately in `transcript`.
- This release is particularly suitable for:
  - **Speaker-attributed transcription**
  - **Far-field diarization**
  - **Counting active speakers in noisy meeting audio**
  - **Studying overlap and turn-taking in realistic meeting scenarios**
