# AliMeeting - Multi-Talker ASR

## Overview
**AliMeeting** is a Mandarin Chinese meeting corpus recorded from real meetings with roughly **120 hours** of speech data. The dataset was introduced for the **ICASSP 2022 Multi-Channel Multi-Party Meeting Transcription Challenge (M2MeT)** and includes far-field speech collected by **8-channel microphone arrays** as well as near-field speech from individual **headset microphones**. Sessions feature **2-4 participants** in **13 different conference rooms** ranging from **8-55 m²**, with speaker-to-microphone distances from **0.3 to 5 meters** and an average speech overlap ratio of over **40%**.

This metadata release provides a **segmented meeting transcription** view of the corpus for **multi-talker ASR**, **speaker diarization**, and **speaker counting**. Each entry contains a short audio segment, a speaker-attributed Mandarin transcript, the list of active speakers in that segment, and timestamped speaker-turn annotations. Audio is stored at **16 kHz** and segment durations are capped at **60 seconds**.

## Supported Tasks
1. **Speaker-attributed ASR**
2. **Speaker Diarization**
3. **Speaker Counting**

---

## Dataset Statistics

| Split | # Segments |
|-------|-----------:|
| train | 24,176 |
| dev | 1,018 |
| test | 2,771 |

**Segment Characteristics:**
- Average duration: **13.21s** (train), **12.83s** (dev), **11.99s** (test)
- Duration range: **0.10s to 59.98s** (train), **0.16s to 59.60s** (dev), **0.15s to 59.91s** (test)
- Total segment duration: **88.75h** (train), **3.63h** (dev), **9.23h** (test)
- Sampling rate: **16 kHz** for all segments

**Speaker Count per Segment:**
- Train: **1-4 speakers**
- Dev: **1-4 speakers**
- Test: **1-4 speakers**

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment ID derived from meeting room and session |
| `path` | Path to the segmented meeting audio file |
| `sampling_rate` | Audio sampling rate (16000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`Ali_Meeting`) |
| `speakers` | List of unique speaker IDs active in the segment |
| `transcript` | Speaker-attributed Mandarin transcript using `SpeakerNN:` line prefixes |
| `timestamps` | Newline-separated speaker-turn annotations in format `[start-end] SpeakerNN` |

---

## Example Entries

```json
{"id": "R0020_M0190-0-0.5-0", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R0020_M0190-0-0.5-0.wav", "sampling_rate": 16000, "duration": 1.12, "dataset": "Ali_Meeting", "speakers": ["0379"], "transcript": "Speaker01: 好大大家好啊。", "timestamps": "[0.00-1.12] Speaker01"}

{"id": "R0020_M0176-1-0.5-3", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R0020_M0176-1-0.5-3.wav", "sampling_rate": 16000, "duration": 4.2, "dataset": "Ali_Meeting", "speakers": ["0356", "0354"], "transcript": "Speaker01: 这是用人单位给予劳动者的几种的保障性的待遇。\nSpeaker02: 嗯。", "timestamps": "[0.00-4.20] Speaker01\n[0.52-0.97] Speaker02"}

{"id": "R0020_M0190-0-0.5-3", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/Ali_Meeting/wav_segments/R0020_M0190-0-0.5-3.wav", "sampling_rate": 16000, "duration": 42.77, "dataset": "Ali_Meeting", "speakers": ["0378", "0379", "0380", "0377"], "transcript": "Speaker01: 舞台的话，我觉得要肯定那舞台肯定要有红毯是吧，红色的那种地毯的那种。\nSpeaker02: 嗯。\nSpeaker03: 到时候儿啊。\nSpeaker02: 啊。\nSpeaker02: 对。\nSpeaker03: 对是。\nSpeaker02: 哎这这个是不是咱们让那个就是专门的这个搭建公司或广告公司来专门做是吧啊。\nSpeaker04: 嗯，对我们还要被。\nSpeaker01: 也可以也可以。\nSpeaker03: 这一块儿我们可以就是包给外边的，呃让他们就是全程负责嗯嗯嗯。\nSpeaker04: 嗯可以可以。\nSpeaker02: 啊。\nSpeaker02: 对对对外包啊对。\nSpeaker01: 对。\nSpeaker02: 对对对对啊可以可以嗯。\nSpeaker01: 对对对也行这样也行，就是说最好就是说那个咱们的舞台就是后边儿是一个墙壁，墙壁上做咱们公司的名字。\nSpeaker02: 嗯。\nSpeaker02: 对。\nSpeaker04: 唉，我我我觉得最好有要有一个led屏。\nSpeaker02: 嗯。\nSpeaker02: 啊。\nSpeaker02: 昂可以可以可以，对对对对对对嗯。\nSpeaker01: 哦可以啊对对对，我太远了的话就可能看不到他们就能，就是观众呢可能看着大屏幕就可液晶显示屏就可以了。\nSpeaker03: 哦，可以啊可以儿这也很好。\nSpeaker04: 这样会比较。\nSpeaker04: 嗯。\nSpeaker02: 对。\nSpeaker02: 对对对他这然后两边都放这对。\nSpeaker03: 对您说这也是非常好的这个，嗯还有还有一个就是。\nSpeaker01: 嗯。\nSpeaker02: 对。\nSpeaker04: 嗯。", "timestamps": "[0.00-6.56] Speaker01\n[0.15-0.40] Speaker02\n[0.32-1.11] Speaker03\n[2.42-2.63] Speaker02\n[4.14-4.45] Speaker02\n[4.50-5.26] Speaker03\n[5.10-11.40] Speaker02\n[6.92-9.16] Speaker04\n[10.22-11.58] Speaker01\n[10.62-19.19] Speaker03\n[11.12-12.32] Speaker04\n[12.03-12.24] Speaker02\n[14.11-15.60] Speaker02\n[14.36-14.70] Speaker01\n[16.60-19.34] Speaker02\n[16.70-26.37] Speaker01\n[20.78-20.95] Speaker02\n[23.80-24.00] Speaker02\n[24.33-29.53] Speaker04\n[25.60-25.79] Speaker02\n[27.05-27.21] Speaker02\n[29.18-33.27] Speaker02\n[29.36-37.46] Speaker01\n[29.82-32.12] Speaker03\n[30.31-31.07] Speaker04\n[34.80-35.18] Speaker04\n[35.47-35.75] Speaker02\n[36.92-40.03] Speaker02\n[37.65-42.77] Speaker03\n[39.93-40.32] Speaker01\n[40.74-40.94] Speaker02\n[40.82-41.19] Speaker04"}
```

---

## Task Usage

### 1. Speaker-attributed ASR
- **Input:** Meeting audio segment
- **Target field:** `transcript`
- **Task:** Generate the Mandarin transcript with speaker attribution preserved via `SpeakerNN:` prefixes

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
- The `speakers` field contains the original AliMeeting speaker identifiers active in the segment (e.g., `0379`, `0378`).

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
- Segment-level counts range from **1 to 4 speakers** across all splits

---

## Notes
- All audio segments are sampled at **16 kHz**.
- The manifests in this directory are **segmented excerpts**, not full meetings.
- Segment durations are capped at **60 seconds**, with most segments substantially shorter.
- The dataset features **high speaker overlap** (average overlap ratio over 40% in the original meetings), making it particularly challenging for multi-talker ASR and diarization systems.
- Audio is recorded in diverse acoustic conditions across **13 different conference rooms** with varying sizes and reverberation characteristics.
- The source data includes both:
  - Far-field audio from **8-channel microphone arrays**
  - Near-field audio from individual **headset microphones**
- The `transcript` field contains **Mandarin Chinese** text with speaker attribution using `SpeakerNN:` line prefixes.
- Speaker IDs in the `speakers` field are anonymized numeric identifiers from the original AliMeeting corpus.
- This release is particularly suitable for:
  - **Mandarin multi-speaker ASR**
  - **Meeting diarization with high overlap**
  - **Speaker counting in realistic meeting scenarios**
  - **Cross-condition modeling** across different acoustic environments
  - **Overlap-aware meeting speech understanding**
- The original AliMeeting corpus was introduced for the **ICASSP 2022 M2MeT Challenge** (Multi-Channel Multi-Party Meeting Transcription).
- Full corpus details and downloads are available at: https://openslr.org/119/
