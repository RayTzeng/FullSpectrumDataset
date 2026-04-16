# MuST-C (en → zh)

## Overview
**MuST-C** (Multilingual Speech Translation Corpus) is a large-scale multilingual speech-to-text translation dataset derived from English **TED Talks**, designed to support research in end-to-end spoken language translation. This manifest covers the **English-to-Mandarin Chinese (en → zh)** translation direction. Audio consists of segmented English speech clips from TED Talk recordings paired with English source transcriptions and Mandarin Chinese target translations. Audio is segmented from long-form talk recordings at **16 kHz** and stored in **WAV format**.

## Supported Tasks
1. **Speech Translation (ST): English → Mandarin Chinese**

---

## Dataset Statistics

| Split | # Samples |
|-------|----------:|
| train | 184,795 |
| dev | 890 |
| test | 2,376 |

The test split combines two official MuST-C test sets:
- **tst-COMMON** (1,824 samples): Shared test set across all MuST-C language pairs
- **tst-HE** (552 samples): Human evaluation subset

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique segment ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset (`MuST-C_en_zh`) |
| `source_text` | English source transcription |
| `target_text` | Mandarin Chinese target translation |

---

## Example Entries

```json
{"id": "en-zh_train_19c8f945ec70", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-zh/train/train_ted_1_19c8f945ec70.wav", "duration": "7.940", "sampling_rate": 16000, "dataset": "MuST-C_en_zh", "source_text": "Thank you so much, Chris. And it's truly a great honor to have the opportunity to come to this stage twice; I'm extremely grateful.", "target_text": "非常谢谢 ， 克里斯。的确非常荣幸能有第二次站在这个台上的机会 ， 我真是非常感激。"}

{"id": "en-zh_train_555f9320301b", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-zh/train/train_ted_1_555f9320301b.wav", "duration": "16.930", "sampling_rate": 16000, "dataset": "MuST-C_en_zh", "source_text": "I have been blown away by this conference, and I want to thank all of you for the many nice comments about what I had to say the other night. And I say that sincerely, partly because (Mock sob) I need that.", "target_text": "这个会议真是让我感到惊叹不已 ， 我还要谢谢你们留下的关于我上次演讲的精彩评论我是非常真诚的 ， 部分原因是因为 — (模拟呜咽) — 我的确非常需要 ！ （ 笑声 ） 你设身处地为我想想 ！ 我坐了 8 年的空军二号。"}

{"id": "en-zh_train_723e29aa69aa", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/MUST-C/en-zh/train/train_ted_1_723e29aa69aa.wav", "duration": "24.690", "sampling_rate": 16000, "dataset": "MuST-C_en_zh", "source_text": "Now I have to take off my shoes or boots to get on an airplane! (Laughter) (Applause)", "target_text": "不过现在上飞机前我则要脱掉我的鞋子 （ 笑声 ） （ 掌声 ）"}
```

---

## Task Usage

### 1. Speech Translation (ST): English → Mandarin Chinese
- **Input:** Audio (English speech)
- **Target field:** `target_text` (Mandarin Chinese translation)

---

## Label Space

*Both tasks generate open-vocabulary text — there is no predefined label space.*

---

## Notes
- All audio files are sampled at **16 kHz** and stored in **WAV format**.
- Audio clips have **variable duration**, typically ranging from under 1 second to ~25 seconds, with an average of ~8.5 seconds per segment.
- Total dataset duration: **~889 hours** across all splits.
- Audio segments are extracted from long-form TED Talk recordings using timestamps from the MuST-C YAML metadata, via ffmpeg.
- The `source_text` field contains the English transcription of the spoken segment.
- The `target_text` field contains the Mandarin Chinese translation (simplified characters) provided by MuST-C annotators.
- Chinese target text uses **space-delimited tokens** (e.g., `非常谢谢 ， 克里斯`) rather than continuous character strings, reflecting the tokenization style of the original MuST-C annotation.
- Spoken annotations in the source (e.g., `(Laughter)`, `(Applause)`) are translated into Chinese equivalents in the target (e.g., `（ 笑声 ）`, `（ 掌声 ）`).
- The dataset originates from TED Talks and therefore reflects **prepared public-speaking style** English: clear articulation, varied vocabulary, and a wide range of topics.
- Compared to en-de and en-es, the en-zh split is somewhat smaller in training data (~185K vs ~251–266K samples), reflecting the relative size of the MuST-C Chinese portion.
- The `train` split is sharded across two files (`en-zh_train_00000`, `_00001`) due to its size; `train.jsonl.gz` is the merged manifest.
- The `test` split merges the two official evaluation sets, `tst-COMMON` and `tst-HE`, which are also available as separate files.
- English-to-Chinese translation presents unique structural challenges including:
  - **Script divergence**: Source uses the Latin alphabet; target uses logographic simplified Chinese characters
  - **Word order and syntax**: Different clause structures and lack of morphological agreement in Chinese
  - **Segmentation granularity**: Chinese translation segments may cover more or fewer spoken words than the German/Spanish equivalents
