# Spoken-DREAM (Speech Summarization)

## Overview
**Spoken-DREAM** is a spoken dialogue comprehension benchmark derived from **DREAM**, a dialogue-based multiple-choice reading comprehension dataset constructed from English-as-a-foreign-language (EFL) exam materials. In this work, the original text dialogues are converted into speech by synthesizing each dialogue with the **VibeVoice** TTS model. This manifest (`SpeechSummarization`) pairs each synthesized dialogue audio with an **abstractive summary** and a short **topic label** sourced from the **DialogSum** dataset (Chen et al., ACL-Findings 2021), enabling spoken dialogue summarization experiments. Audio is synthesized at **24 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Spoken Dialogue Summarization** — Generate a concise abstractive summary of the content of a synthesized multi-turn dialogue

---

## Dataset Statistics

| Split | # Samples | Total Duration | Avg Duration |
|-------|----------:|---------------:|-------------:|
| train | 1,003 | ~12.77h | ~45.85s |
| dev | 326 | ~4.11h | ~45.40s |
| test | 338 | ~4.38h | ~46.70s |

**Total: 1,667 samples, ~21.26 hours across all splits.**

Audio duration ranges from ~8.8 to ~263.5 seconds.

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique dialogue ID (e.g., `1-102_dialogue_UM__train_10956`) |
| `path` | Path to synthesized dialogue audio file |
| `sampling_rate` | Audio sampling rate (24000 Hz) |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset (`Spoken-DREAM`) |
| `summary` | Abstractive summary of the dialogue content |
| `topic` | Short topic label describing the dialogue subject |

---

## Example Entries

```json
{"id": "1-102_dialogue_UM__train_10956", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Spoken-DREAM/wavs/train/1-102_dialogue_UM_generated.wav", "sampling_rate": 24000, "duration": 127.46666666666667, "dataset": "Spoken-DREAM", "summary": "Mr. Smith is taking a road test to get his driving license. During the test, Mr. Smith forgets the speed limit and forgets to signal. He doesn't keep his eyes on the road. He is tailgating a vehicle and almost hits a pedestrian. He doesn't pass the test and Speaker1 asks him to take it again when Speaker1 is off.", "topic": "road test"}

{"id": "1-106_dialogue_MF__train_7610", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Spoken-DREAM/wavs/dev/1-106_dialogue_MF_generated.wav", "sampling_rate": 24000, "duration": 149.06666666666666, "dataset": "Spoken-DREAM", "summary": "Speaker1 brags to Speaker2 that Speaker1 is good at fishing but Speaker2 doesn't believe it. Speaker2 shows Speaker1 Speaker2's fishing skill by catching a big fish.", "topic": "fishing"}

{"id": "1-100_dialogue_UM__train_6651", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/Spoken-DREAM/wavs/test/1-100_dialogue_UM_generated.wav", "sampling_rate": 24000, "duration": 58.4, "dataset": "Spoken-DREAM", "summary": "Speaker2 phones Greg, but Greg isn't available. Speaker2 leaves a message to blame Greg for not telling him Cindy isn't single so that Speaker2 was nearly strangled by Butch and chased by Butch's dog.", "topic": "a maniac"}
```

---

## Task Usage

### 1. Spoken Dialogue Summarization
- **Input:** Audio (synthesized multi-turn dialogue)
- **Target field:** `summary` (abstractive summary of the dialogue)
- **Auxiliary field:** `topic` (short subject label, not used as a generation target)

---

## Label Space

*This task generates open-vocabulary text — there is no predefined label space.*

The `summary` field contains abstractive, multi-sentence descriptions of the dialogue content. Summaries are written in third person and refer to participants as `Speaker1` and `Speaker2` (or by name if mentioned in the dialogue). The `topic` field is a short free-text label (e.g., `road test`, `fishing`, `job interview`) describing the dialogue's subject matter.

---

## Notes
- All audio files are sampled at **24 kHz** and stored in **WAV format**.
- Audio duration ranges from ~8.8 to ~263.5 seconds, with an average of ~45.8 seconds per dialogue.
- All speech is **synthesized** using the **VibeVoice** TTS model. Speaker gender for each dialogue turn is encoded in the filename suffix (e.g., `_FM` = female–male, `_MF` = male–female, `_MM` = male–male, `_UM` = unknown–male).
- The original DREAM dataset covers a wide range of everyday conversational topics drawn from EFL exam materials. Topics represented include (but are not limited to): job interviews, road tests, fishing, dental treatment, travel plans, neighborhood disputes, and family interactions.
- Summaries use generic speaker labels (`Speaker1`, `Speaker2`) rather than character names unless the name is explicitly stated in the dialogue.
- The `summary` and `topic` fields are sourced from the **DialogSum** dataset (Chen et al., "DialogSum: A Real-Life Scenario Dialogue Summarization Dataset", ACL-Findings 2021), which provides abstractive summaries and topic labels for spoken dialogue transcripts.
- The companion manifest at `../ReasoningQA/` pairs the same synthesized dialogue audio with multiple-choice comprehension questions and answers.
