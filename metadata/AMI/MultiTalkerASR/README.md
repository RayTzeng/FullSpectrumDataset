# AMI - Multi-Talker ASR

## Overview
**AMI Meeting Corpus** is a multimodal English meeting dataset containing roughly **100 hours** of recordings from both **scenario-based design-team meetings** and **naturally occurring meetings**. It provides synchronized audio from **close-talking** and **far-field microphones**, along with multiple cameras, presentation slides, whiteboards, digital pens, and rich annotations including transcripts, word timings, dialogue acts, topics, summaries, named entities, gestures, gaze, and emotions.

This metadata release focuses on the **audio meeting-segment** view of AMI for **multi-talker ASR** and related speaker-aware tasks. Each entry contains a segmented audio clip, a speaker-attributed transcript, the set of active speakers, and timestamped speaker-turn annotations. The default `train.jsonl.gz` and `test.jsonl.gz` manifests in this directory are **merged across two microphone conditions**:
- `ihm-mix`: mixed individual headset microphone audio
- `sdm`: single distant microphone audio

All audio in these manifests is stored at **16 kHz**.

## Supported Tasks
1. **Speaker-attributed ASR**
2. **Speaker Diarization**
3. **Speaker Counting**

---

## Dataset Statistics

| Split | # Segments |
|-------|-----------:|
| train | 29,899 |
| test | 3,606 |

**Segment Characteristics:**
- Average duration: **16.53s** (train), **15.19s** (test)
- Duration range: **0.03s to 60.0s** (train), **0.08s to 60.0s** (test)
- Total segment duration: **137.24h** (train), **15.22h** (test)
- Sampling rate: **16 kHz** for all segments

**Speaker Count per Segment:**
- Train: **1-5 speakers**
- Test: **1-4 speakers**

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment ID, prefixed by microphone condition such as `ihm-mix_` or `sdm_` |
| `path` | Path to the segmented meeting audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`AMI`) |
| `speakers` | List of unique speaker IDs active in the segment |
| `transcript` | Speaker-attributed transcript using `SpeakerNN:` line prefixes |
| `timestamps` | Newline-separated speaker-turn annotations in format `[start-end] SpeakerNN` |

---

## Example Entries

```json
{"id": "ihm-mix_TS3010c-0-1-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/ihm-mix/ihm-mix_TS3010c-0-1-0.wav", "sampling_rate": 16000, "duration": 9.94, "dataset": "AMI", "speakers": ["MTD037PM"], "transcript": "Speaker01: Okay\nSpeaker01: Well, let's start\nSpeaker01: What are we doing? Oops", "timestamps": "[0.0-2.6] Speaker01\n[2.6-6.6] Speaker01\n[6.6-9.9] Speaker01"}

{"id": "sdm_ES2006d-0-1-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/sdm/sdm_ES2006d-0-1-0.wav", "sampling_rate": 16000, "duration": 7.02, "dataset": "AMI", "speakers": ["MEO022", "FEE021"], "transcript": "Speaker01: I'm proud of it\nSpeaker02: Okay\nSpeaker02: This is our final meeting, the detailed design meeting", "timestamps": "[0.0-2.0] Speaker01\n[2.1-3.6] Speaker02\n[3.6-7.0] Speaker02"}

{"id": "sdm_EN2002a-0-1-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/sdm/sdm_EN2002a-0-1-0.wav", "sampling_rate": 16000, "duration": 34.04, "dataset": "AMI", "speakers": ["MEE071", "MEE073", "FEO072", "FEO070"], "transcript": "Speaker01: Funky sh-  stuff like that\nSpeaker02: Wonder how much of the meetings is talking about the stuff at the meetings\nSpeaker03: Yeah, exactly, yeah yeah yeah\nSpeaker01: Yeah\nSpeaker01: Yeah\nSpeaker01: Look at all this stuff man\nSpeaker02: Yeah\nSpeaker04: Okay\nSpeaker01: Okay\nSpeaker01: Right\nSpeaker04: So what do we need to talk about?\nSpeaker03: Should we\nSpeaker01: Has anybody\nSpeaker03: Well should we just go around and everyone says what they d-  what they've been doing, how far they've got\nSpeaker01: Has anybody done anything?\nSpeaker02: Not a lot\nSpeaker02: No\nSpeaker03: Well I hope so\nSpeaker02: Hmm\nSpeaker04: Yeah\nSpeaker02: Okay\nSpeaker02: Sounds like you've done some stuff\nSpeaker02: So\nSpeaker01: You better start\nSpeaker03: Okay\nSpeaker04: Uh\nSpeaker03: Well I've got a browser now, which Whoops\nSpeaker04: Yeah\nSpeaker02: 'Kay\nSpeaker03: Already gone", "timestamps": "[0.0-1.4] Speaker01\n[0.6-6.3] Speaker02\n[3.2-5.0] Speaker03\n[3.4-4.3] Speaker01\n[4.3-5.0] Speaker01\n[5.0-8.3] Speaker01\n[6.3-6.5] Speaker02\n[8.2-8.6] Speaker04\n[8.3-11.5] Speaker01\n[11.5-11.8] Speaker01\n[11.9-14.8] Speaker04\n[12.8-13.3] Speaker03\n[14.6-15.1] Speaker01\n[14.8-23.8] Speaker03\n[18.7-23.3] Speaker01\n[21.1-22.7] Speaker02\n[22.7-22.9] Speaker02\n[23.8-24.9] Speaker03\n[25.1-26.1] Speaker02\n[25.4-25.8] Speaker04\n[26.1-26.7] Speaker02\n[26.7-27.8] Speaker02\n[27.8-29.4] Speaker02\n[28.1-29.5] Speaker01\n[29.5-30.2] Speaker03\n[30.1-30.3] Speaker04\n[30.2-33.1] Speaker03"}
```

---

## Task Usage

### 1. Speaker-attributed ASR
- **Input:** Meeting audio segment
- **Target field:** `transcript`
- **Task:** Generate the transcript with speaker attribution preserved via `SpeakerNN:` prefixes

### 2. Speaker Diarization
- **Input:** Meeting audio segment
- **Target field:** `timestamps`
- **Task:** Predict who spoke when using timestamped speaker-turn boundaries

### 3. Speaker Counting
- **Input:** Meeting audio segment
- **Target field:** `speakers`
- **Task:** Predict the number of distinct active speakers in the segment, i.e., `len(speakers)`

---

## Label Space

### Speaker Attribution Format
- The `transcript` field uses canonical placeholders such as `Speaker01`, `Speaker02`, `Speaker03`, and `Speaker04`.
- These placeholders are local to each segment and align with the order used in the `timestamps` field.
- The `speakers` field contains the original AMI speaker identifiers active in the segment, such as `MTD037PM` or `FEE021`.

### Timestamp Format

The `timestamps` field contains newline-separated speaker turns in the format:

```text
[start_time-end_time] SpeakerNN
```

**Properties:**
- `start_time` and `end_time` are given in seconds
- Speaker turns can **overlap**
- The format supports diarization supervision and turn-boundary evaluation
- `SpeakerNN` identifiers align with the prefixes used in `transcript`

### Speaker Count
- Speaker counting is derived from the number of distinct entries in `speakers`
- Segment-level counts range from **1 to 5 speakers** in the default merged training manifest

---

## Notes
- All audio segments are sampled at **16 kHz**.
- The manifests in this directory are **segmented excerpts**, not full meetings.
- The default `train.jsonl.gz` and `test.jsonl.gz` manifests are **merged** across:
  - `ihm-mix` close-talking mixed headset audio
  - `sdm` far-field single distant microphone audio
- Additional condition-specific manifests are also available in this directory:
  - `ihm-mix_train.jsonl.gz`, `ihm-mix_dev.jsonl.gz`, `ihm-mix_test.jsonl.gz`
  - `sdm_train.jsonl.gz`, `sdm_dev.jsonl.gz`, `sdm_test.jsonl.gz`
  - `dev.jsonl.gz` as the merged development split
- Segment durations are capped at **60 seconds**, with many segments substantially shorter.
- The speaker-attributed formatting in the default manifests has been normalized from inline tags like `<Speaker1>` into a more readable multiline format using `SpeakerNN:` prefixes.
- The conversion process is documented in:
  - [CONVERSION_SUMMARY.md](/home/tseng/FullSpectrumDataset/metadata/AMI/MultiTalkerASR/CONVERSION_SUMMARY.md)
  - [README_convert_diarization.md](/home/tseng/FullSpectrumDataset/metadata/AMI/MultiTalkerASR/README_convert_diarization.md)
  - [convert_diarization_format.py](/home/tseng/FullSpectrumDataset/metadata/AMI/MultiTalkerASR/convert_diarization_format.py)
- This release is useful for:
  - **Speaker-attributed transcription**
  - **Meeting diarization**
  - **Cross-condition modeling** across close-talking and far-field audio
  - **Overlap-aware meeting speech understanding**
