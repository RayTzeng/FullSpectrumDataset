# AliMeeting - Target Speaker ASR

## Overview
**AliMeeting** is a Mandarin Chinese meeting corpus recorded from real meetings with roughly **120 hours** of speech data. The dataset was introduced for the **ICASSP 2022 Multi-Channel Multi-Party Meeting Transcription Challenge (M2MeT)** and includes far-field speech collected by **8-channel microphone arrays** as well as near-field speech from individual **headset microphones**. Sessions feature **2-4 participants** in **13 different conference rooms** ranging from **8-55 m²**, with speaker-to-microphone distances from **0.3 to 5 meters** and an average speech overlap ratio of over **40%**.

This metadata release focuses on **target speaker ASR**, a task where the model must transcribe only the speech of a designated target speaker from a multi-speaker Mandarin meeting recording. Each entry contains two audio files: a **speaker enrollment audio** (containing speech from the target speaker only) and a **multi-speaker meeting segment** (containing overlapping speech from multiple participants). The model must use the enrollment audio to identify and transcribe only the target speaker's utterances from the mixture. All audio is stored at **16 kHz** and segment durations are capped at **60 seconds**.

## Supported Tasks
1. **Target Speaker ASR**
2. **Target Speaker ASR with Timestamps**
3. **Target Speaker Attribution**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 118,896 |
| test | 11,550 |

**Sample Characteristics:**
- Each sample includes **1 enrollment audio** + **1 meeting segment audio**
- Enrollment audio duration: typically **3-20 seconds**
- Meeting segment duration: typically **1-60 seconds**
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
| `dataset` | Source dataset (`Ali_Meeting`) |
| `target_text` | Newline-separated Mandarin transcript of target speaker's utterances only |
| `target_timestamped_text` | Timestamped transcript in format `[start-end] text` |
| `target_attribution` | Time intervals when target speaker is active in format `[start-end]` |

---

## Example Entries

```json
{"id": "R0020_M0190-0-0.5-3_0378_0", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/speaker_profiles/0378/0003_train_sdm_R0020_M0190-0378-3.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R0020_M0190-0-0.5-3.wav"], "sampling_rates": [16000, 16000], "durations": [13.82, 42.77], "dataset": "Ali_Meeting", "target_text": "舞台的话，我觉得要肯定那舞台肯定要有红毯是吧，红色的那种地毯的那种。\n也可以也可以。\n对。\n对对对也行这样也行，就是说最好就是说那个咱们的舞台就是后边儿是一个墙壁，墙壁上做咱们公司的名字。\n哦可以啊对对对，我太远了的话就可能看不到他们就能，就是观众呢可能看着大屏幕就可液晶显示屏就可以了。\n嗯。", "target_timestamped_text": "[0.0-6.6] 舞台的话，我觉得要肯定那舞台肯定要有红毯是吧，红色的那种地毯的那种。\n[10.2-11.6] 也可以也可以。\n[14.4-14.7] 对。\n[16.7-26.4] 对对对也行这样也行，就是说最好就是说那个咱们的舞台就是后边儿是一个墙壁，墙壁上做咱们公司的名字。\n[29.4-37.5] 哦可以啊对对对，我太远了的话就可能看不到他们就能，就是观众呢可能看着大屏幕就可液晶显示屏就可以了。\n[39.9-40.3] 嗯。", "target_attribution": "[0.0-6.6]\n[10.2-11.6]\n[14.4-14.7]\n[16.7-26.4]\n[29.4-37.5]\n[39.9-40.3]"}

{"id": "R8004_M8005-0-0.5-0_8017_0", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/speaker_profiles/8017/0043_test_sdm_R8004_M8005-8017-80.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R8004_M8005-0-0.5-0.wav"], "sampling_rates": [16000, 16000], "durations": [3.79, 23.28], "dataset": "Ali_Meeting", "target_text": "啊今天咱们来聊聊各自的家庭财务规划的事情啊，然后各自都聊一聊每家都有什么固定的财务支出啊？\n有没有什么房贷车贷可以还的啥的？", "target_timestamped_text": "[0.0-10.6] 啊今天咱们来聊聊各自的家庭财务规划的事情啊，然后各自都聊一聊每家都有什么固定的财务支出啊？\n[18.4-20.8] 有没有什么房贷车贷可以还的啥的？", "target_attribution": "[0.0-10.6]\n[18.4-20.8]"}

{"id": "R0020_M0190-0-0.5-3_0379_0", "paths": ["/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/speaker_profiles/0379/0062_train_sdm_R0020_M0190-0379-305.wav", "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R0020_M0190-0-0.5-3.wav"], "sampling_rates": [16000, 16000], "durations": [8.29, 42.77], "dataset": "Ali_Meeting", "target_text": "嗯。\n啊。\n对。\n哎这这个是不是咱们让那个就是专门的这个搭建公司或广告公司来专门做是吧啊。\n啊。\n对对对外包啊对。\n对对对对啊可以可以嗯。\n嗯。\n对。\n嗯。\n啊。\n昂可以可以可以，对对对对对对嗯。\n对。\n对对对他这然后两边都放这对。\n对。", "target_timestamped_text": "[0.1-0.4] 嗯。\n[2.4-2.6] 啊。\n[4.1-4.5] 对。\n[5.1-11.4] 哎这这个是不是咱们让那个就是专门的这个搭建公司或广告公司来专门做是吧啊。\n[12.0-12.2] 啊。\n[14.1-15.6] 对对对外包啊对。\n[16.6-19.3] 对对对对啊可以可以嗯。\n[20.8-20.9] 嗯。\n[23.8-24.0] 对。\n[25.6-25.8] 嗯。\n[27.1-27.2] 啊。\n[29.2-33.3] 昂可以可以可以，对对对对对对嗯。\n[35.5-35.8] 对。\n[36.9-40.0] 对对对他这然后两边都放这对。\n[40.7-40.9] 对。", "target_attribution": "[0.1-0.4]\n[2.4-2.6]\n[4.1-4.5]\n[5.1-11.4]\n[12.0-12.2]\n[14.1-15.6]\n[16.6-19.3]\n[20.8-20.9]\n[23.8-24.0]\n[25.6-25.8]\n[27.1-27.2]\n[29.2-33.3]\n[35.5-35.8]\n[36.9-40.0]\n[40.7-40.9]"}
```

---

## Task Usage

### 1. Target Speaker ASR
- **Input:** Enrollment audio (`paths[0]`) + Meeting segment audio (`paths[1]`)
- **Target field:** `target_text`
- **Task:** Transcribe only the Mandarin speech of the target speaker (identified by enrollment audio) from the multi-speaker meeting segment

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

*This task generates open-vocabulary Mandarin text transcriptions — there is no predefined label space.*

### Transcript Format

The `target_text` field contains newline-separated Mandarin utterances from the target speaker only:
```
舞台的话，我觉得要肯定那舞台肯定要有红毯是吧，红色的那种地毯的那种。
也可以也可以。
对。
```

### Timestamped Format

The `target_timestamped_text` field includes timing information for each utterance:
```
[0.0-6.6] 舞台的话，我觉得要肯定那舞台肯定要有红毯是吧，红色的那种地毯的那种。
[10.2-11.6] 也可以也可以。
[14.4-14.7] 对。
```

**Properties:**
- Timestamps are in seconds relative to the meeting segment start
- Format: `[start-end] transcription`
- Each line represents one utterance from the target speaker
- Times indicate when the target speaker's voice is active
- May include gaps between utterances when other speakers are talking or during silence

### Attribution Format

The `target_attribution` field contains only the time intervals when the target speaker is active:
```
[0.0-6.6]
[10.2-11.6]
[14.4-14.7]
```

---

## Notes
- All audio files are sampled at **16 kHz**.
- The manifests contain **multiple samples per meeting segment**, each with a different target speaker and enrollment audio.
- The ID format is `{segment_id}_{speaker_id}_{enrollment_index}`:
  - **segment_id**: Meeting segment identifier (e.g., `R0020_M0190-0-0.5-3`)
  - **speaker_id**: AliMeeting speaker identifier (e.g., `0378`, `8017`)
  - **enrollment_index**: Index of the enrollment audio for this speaker (0, 1, 2, ...)
- Each target speaker has **multiple enrollment audio samples** from different parts of the meeting, enabling evaluation of robustness to enrollment variation.
- The **enrollment audio** (`paths[0]`) contains only the target speaker's voice extracted from other meeting segments.
- The **meeting segment audio** (`paths[1]`) contains overlapping speech from **2-4 speakers** in highly reverberant conditions.
- This task is particularly challenging because:
  - Meeting segments have an average **speech overlap ratio over 40%**
  - The model must perform **speaker verification** (matching enrollment to target) and **selective transcription** simultaneously
  - Audio is recorded in **far-field conditions** with varying reverberation across 13 conference rooms
  - Speaker-to-microphone distances range from **0.3 to 5 meters**
- The dataset supports research on:
  - **Enrollment-based speaker extraction in Mandarin**
  - **Target speaker ASR in highly overlapped multi-talker scenarios**
  - **Speaker-conditioned speech recognition**
  - **Cocktail party problem** in realistic far-field meeting conditions
  - **Mandarin conversational speech understanding**
- Time boundaries in `target_timestamped_text` and `target_attribution` may have slight gaps or overlaps depending on the original annotation.
- Only utterances from the **target speaker** are included in the transcripts; other speakers' speech is ignored.
- The transcripts contain natural Mandarin conversational speech including:
  - **Backchannels** (嗯, 啊, 对, etc.)
  - **Disfluencies** and **hesitations**
  - **Overlapping turns** and **interruptions**
- This release complements the **Multi-Talker ASR** task (which transcribes all speakers) by focusing on selective attention to a single Mandarin speaker.
- The original AliMeeting corpus was introduced for the **ICASSP 2022 M2MeT Challenge** (Multi-Channel Multi-Party Meeting Transcription).
- Full corpus details and downloads are available at: https://openslr.org/119/
