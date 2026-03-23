# PodSarc

## Overview
**PodSarc** is a large-scale spoken sarcasm dataset created from a publicly available sarcasm-focused podcast, designed to support speech-based sarcasm detection in realistic audio-only settings. The dataset was built using an **LLM-assisted annotation pipeline** with GPT-4o and LLaMA 3, followed by human verification, ensuring high-quality labels for naturalistic conversational speech.

## Supported Tasks
1. **Sarcasm Detection in Speech**
2. **Sarcasm Understanding**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 7,392 |
| test | 747 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique utterance ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source dataset |
| `text` | Transcribed text of the utterance |
| `sarcasm` | Ground-truth sarcasm detection label (boolean) |
| `emotion` | Emotional tone label |
| `comment` | Explanation of why the utterance is sarcastic or not |

---

## Example Entries

```json
{"id": "70_223", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/PodSarc/all_processed/overly-sarcastic-podcast__ospod-episode-70/ospod-episode-70_223.mp3", "sampling_rate": 24000, "duration": "11.904", "dataset": "PodSarc", "text": "I got a Sherlock Holmes deer stalker hat for my birthday and it slaps. So I was like, unfortunately, now we have to do some kind of stream where I get to wear this hat. So you'll just have to trust me. It looks great.", "sarcasm": true, "emotion": "sarcasm", "comment": "The speaker humorously describes their hat as something they 'have to' show on stream. The playful tone and the phrase 'you'll just have to trust me' convey sarcasm."}

{"id": "78_47", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/PodSarc/all_processed/overly-sarcastic-podcast__ospod-episode-78/ospod-episode-78_47.mp3", "sampling_rate": 24000, "duration": "19.008", "dataset": "PodSarc", "text": "Um, I, I was able to actually talk about it a little bit in the context of my, my presentation, uh, in Baltimore, where I was kind of giving a little bit of, like, case studies of how I construct the narratives in different videos, one of which was the, uh, the Ukrainian cathedral, um, and how I did the research process on that. One was how I told the story for.", "sarcasm": false, "emotion": "informative", "comment": "The speaker is providing context about a presentation and explaining their research and storytelling approach. The tone is straightforward, with no indication of sarcasm."}

{"id": "53_80", "path": "/saltpool0/data/tseng/FullSpectrumDataset/corpus/PodSarc/all_processed/overly-sarcastic-podcast__ospod-episode-53/ospod-episode-53_80.mp3", "sampling_rate": 24000, "duration": "3.648", "dataset": "PodSarc", "text": "a dick joke or whatever. It's so important and you didn't mention it in your 10 minute video.", "sarcasm": true, "emotion": "sarcasm", "comment": "This line continues the sarcasm, humorously presenting trivial content as if it were essential, underscoring the absurdity of some viewer demands."}
```

---

## Task Usage

### 1. Sarcasm Detection in Speech
- **Target field:** `sarcasm` (boolean sarcasm label)

### 2. Sarcasm Understanding
- **Target field:** `sarcasm`,`comment` (explanation of the cause of sarcasm)

---

## Label Space

### Sarcasm Labels
<details>
<summary>Show 2 available labels:</summary>

`true`, `false`

</details>

### Label Definitions
<details>
<summary>Show detailed descriptions for each label:</summary>

- **true**: The utterance is sarcastic, conveying meaning that is contrary to or different from the literal interpretation, often with humorous or ironic intent
- **false**: The utterance is non-sarcastic, with the literal meaning matching the speaker's intent

</details>

---

## Notes
- All audio files are sampled at **24 kHz**.
- Audio files are stored in **MP3 format**.
- The `comment` field provides explanations for why the utterance is sarcastic or not, enabling the Sarcasm Understanding task.
- The dataset was created using an LLM-assisted annotation pipeline with GPT-4o and LLaMA 3, followed by human verification.
- The sarcasm labels are stored as boolean values (`true`/`false`).
