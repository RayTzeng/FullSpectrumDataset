# AMI - Target Speaker ASR

## Overview
**AMI Meeting Corpus** is a multimodal English meeting dataset containing roughly **100 hours** of recordings from both **scenario-based design-team meetings** and **naturally occurring meetings**. It provides synchronized audio from **close-talking** and **far-field microphones**, along with multiple cameras, presentation slides, whiteboards, digital pens, and rich annotations including transcripts, word timings, dialogue acts, topics, summaries, named entities, gestures, gaze, and emotions.

This metadata release focuses on **target speaker ASR**, a task where the model must transcribe only the speech of a designated target speaker from a multi-speaker meeting recording. Each entry contains two audio files: a **speaker enrollment audio** (containing speech from the target speaker only) and a **multi-speaker meeting segment** (containing overlapping speech from multiple participants). The model must use the enrollment audio to identify and transcribe only the target speaker's utterances from the mixture. This release includes segments from two microphone conditions:
- `ihm-mix`: mixed individual headset microphone audio
- `sdm`: single distant microphone audio

All audio in these manifests is stored at **16 kHz**.

## Supported Tasks
1. **Target Speaker ASR**
2. **Target Speaker ASR with Timestamps**
3. **Target Speaker Attribution**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 125,100 |
| test | 13,830 |

**Sample Characteristics:**
- Each sample includes **1 enrollment audio** + **1 meeting segment audio**
- Enrollment audio duration: typically **3-20 seconds**
- Meeting segment duration: typically **2-60 seconds**
- Total training samples represent multiple enrollment-segment pairings per unique meeting segment
- Sampling rate: **16 kHz** for all audio files

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique sample ID combining segment ID, speaker ID, and enrollment index |
| `paths` | List of 2 audio paths: [enrollment_audio, meeting_segment_audio] |
| `sampling_rates` | List of 2 sampling rates (both 16000 Hz) |
| `durations` | List of 2 audio durations in seconds |
| `dataset` | Source dataset (`AMI`) |
| `target_text` | Newline-separated transcript of target speaker's utterances only |
| `target_timestamped_text` | Timestamped transcript in format `[start-end] text` |
| `target_attribution` | Time intervals when target speaker is active in format `[start-end]` |

---

## Example Entries

```json
{"id": "ihm-mix_TS3010c-0-1-0_MTD037PM_0", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/speaker_profiles/MTD037PM/0175_ami-sdm_train_sdm_TS3010b-146.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/ihm-mix/ihm-mix_TS3010c-0-1-0.wav"], "sampling_rates": [16000, 16000], "durations": [5.58, 9.94], "dataset": "AMI", "target_text": "Okay\nWell, let's start\nWhat are we doing? Oops", "target_timestamped_text": "[0.0-2.6] Okay\n[2.6-6.6] Well, let's start\n[6.6-9.9] What are we doing? Oops", "target_attribution": "[0.0-2.6]\n[2.6-6.6]\n[6.6-9.9]"}

{"id": "ihm-mix_ES2004c-0-1-5_FEE013_0", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/speaker_profiles/FEE013/0006_ami-ihm-mix_test_ihm-mix_ES2004c-295.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/ihm-mix/ihm-mix_ES2004c-0-1-5.wav"], "sampling_rates": [16000, 16000], "durations": [16.78, 2.36], "dataset": "AMI", "target_text": "Put it on in that way\nThanks", "target_timestamped_text": "[0.0-2.1] Put it on in that way\n[2.1-2.4] Thanks", "target_attribution": "[0.0-2.1]\n[2.1-2.4]"}

{"id": "sdm_ES2006d-0-1-0_MEO022_1", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/speaker_profiles/MEO022/0132_ami-sdm_train_sdm_ES2006a-254.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/AMI/wav_segments/sdm/sdm_ES2006d-0-1-0.wav"], "sampling_rates": [16000, 16000], "durations": [8.45, 7.02], "dataset": "AMI", "target_text": "I'm proud of it", "target_timestamped_text": "[0.0-2.0] I'm proud of it", "target_attribution": "[0.0-2.0]"}
```

---

## Task Usage

### 1. Target Speaker ASR
- **Input:** Enrollment audio (`paths[0]`) + Meeting segment audio (`paths[1]`)
- **Target field:** `target_text`
- **Task:** Transcribe only the speech of the target speaker (identified by enrollment audio) from the multi-speaker meeting segment

### 2. Target Speaker ASR with Timestamps
- **Input:** Enrollment audio (`paths[0]`) + Meeting segment audio (`paths[1]`)
- **Target field:** `target_timestamped_text`
- **Task:** Transcribe the target speaker's utterances with precise time boundaries in format `[start-end] text`

### 3. Target Speaker Attribution
- **Input:** Enrollment audio (`paths[0]`) + Meeting segment audio (`paths[1]`)
- **Target field:** `target_attribution`
- **Task:** Identify when the target speaker is active, returning time intervals in format `[start-end]`

---

## Label Space

*This task generates open-vocabulary text transcriptions — there is no predefined label space.*

### Transcript Format

The `target_text` field contains newline-separated utterances from the target speaker only:
```
Okay
Well, let's start
What are we doing? Oops
```

### Timestamped Format

The `target_timestamped_text` field includes timing information for each utterance:
```
[0.0-2.6] Okay
[2.6-6.6] Well, let's start
[6.6-9.9] What are we doing? Oops
```

**Properties:**
- Timestamps are in seconds relative to the meeting segment start
- Format: `[start-end] transcription`
- Each line represents one utterance from the target speaker
- Times indicate when the target speaker's voice is active

### Attribution Format

The `target_attribution` field contains only the time intervals when the target speaker is active:
```
[0.0-2.6]
[2.6-6.6]
[6.6-9.9]
```

---

## Notes
- All audio files are sampled at **16 kHz**.
- The manifests contain **multiple samples per meeting segment**, each with a different target speaker and enrollment audio.
- The ID format is `{segment_id}_{speaker_id}_{enrollment_index}`:
  - **segment_id**: Meeting segment identifier (e.g., `ihm-mix_TS3010c-0-1-0`)
  - **speaker_id**: AMI speaker identifier (e.g., `MTD037PM`, `FEE013`)
  - **enrollment_index**: Index of the enrollment audio for this speaker (0, 1, 2, ...)
- Each target speaker has **multiple enrollment audio samples** from different parts of the meeting, enabling evaluation of robustness to enrollment variation.
- The **enrollment audio** (`paths[0]`) contains only the target speaker's voice extracted from other meeting segments.
- The **meeting segment audio** (`paths[1]`) may contain overlapping speech from multiple speakers.
- This task is particularly challenging because:
  - Meeting segments often contain **overlapping speech** from multiple speakers
  - The model must perform **speaker verification** (matching enrollment to target) and **selective transcription** simultaneously
  - Both **close-talking** (`ihm-mix`) and **far-field** (`sdm`) conditions are included
- The dataset supports research on:
  - **Enrollment-based speaker extraction**
  - **Target speaker ASR in multi-talker scenarios**
  - **Speaker-conditioned speech recognition**
  - **Cocktail party problem** in realistic meeting scenarios
- Time boundaries in `target_timestamped_text` and `target_attribution` may have slight gaps or overlaps depending on the original annotation.
- Only utterances from the **target speaker** are included in the transcripts; other speakers' speech is ignored.
- This release complements the **Multi-Talker ASR** task (which transcribes all speakers) by focusing on selective attention to a single speaker.
