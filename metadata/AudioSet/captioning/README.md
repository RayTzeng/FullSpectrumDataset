# AudioSet Audio Captioning

## Overview
**AudioSet Audio Captioning** is a large-scale dataset for fine-grained audio captioning, created by pairing AudioSet audio clips with detailed captions from the **FusionAudio-1.2M** dataset. FusionAudio was designed to provide richer, more context-aware audio understanding by combining audio with multimodal contextual cues such as speech, music, general sound, and associated visual information. The dataset contains **1.2 million detailed audio captions** describing diverse soundscapes, with caption lengths averaging **~48 words**, significantly more detailed than earlier captioning datasets. Audio is sampled at **16 kHz** in **WAV format**, with clips typically lasting **~10 seconds**.

## Supported Tasks
1. **Audio Captioning**

---

## Dataset Statistics

| Split | # Samples | Total Duration |
|-------|-----------|----------------|
| train | 1,200,000 | ~3,316 hours |
| test | 27,675 | ~76 hours |

**Audio Characteristics:**
- Average duration: 9.95 seconds
- Duration range: 0.03s - 10.08s
- Sampling rate: 16 kHz (all clips)

**Caption Characteristics:**
- Average length: 47.6 words
- Length range: 1 - 349 words
- Significantly more detailed than traditional short captions

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique AudioSet clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration (seconds) |
| `dataset` | Source dataset |
| `caption` | Detailed audio caption text |

---

## Example Entries

```json
{"id": "---2_BBVHAA_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---2_BBVHAA.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "caption": "Clear speech dominated the audio with rhythmic pauses, accompanied by persistent clattering of dishes, pots, and pans in the background. The vocal delivery suggests active participation in a conversation, possibly alongside tasks involving metallic objects."}

{"id": "---B_v8ZoBY_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---B_v8ZoBY.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "caption": "An energetic live music performance featuring a blend of country rock and blues styles is heard, with a punchy snare drum, shimmering cymbals, and a prominent bassline. The recording exhibits a raw, noisy quality with mono sound, accompanied by enthusiastic audience clapping and lively crowd reactions. A dynamic vocal performance with distortion and rhythmic engagement is central to the track."}

{"id": "---fcVQUf3E_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/---fcVQUf3E.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "AudioSet", "caption": "A prominent vehicle engine sound dominates the audio, likely characteristic of a water vehicle, accompanied by sustained wind and water environmental sounds. Intermittent low-frequency impact noises are heard, possibly corresponding to wave collisions against a submerged structure or nearby objects. The audio maintains consistent outdoor ambiance with marine environmental characteristics throughout."}
```

---

## Task Usage

### 1. Audio Captioning
- **Input:** Audio clip
- **Target field:** `caption` (detailed textual description)

**Task Description:** Generate rich, detailed natural language descriptions of audio content, including information about sound sources, acoustic characteristics, environmental context, and temporal dynamics.

---

## Label Space

*This is an open-vocabulary generation task - captions are free-form natural language descriptions with no predefined vocabulary.*

---

## Caption Characteristics

### Fine-Grained Detail
Unlike traditional audio captioning datasets with short descriptions (e.g., "A dog barking"), FusionAudio captions provide:
- **Acoustic details**: Timbre, pitch, rhythm, spatial characteristics
- **Contextual information**: Environmental setting, likely activities
- **Temporal dynamics**: Changes and patterns over time
- **Multi-modal cues**: Integration of visual, speech, music, and sound information

### Caption Complexity
- **Average length**: 47.6 words (vs. ~10 words in earlier datasets)
- **Rich vocabulary**: Descriptive adjectives, technical audio terms
- **Compositional**: Often describe multiple sound sources and their relationships
- **Interpretive**: Include inferred context and likely scenarios

### Example Complexity Levels
**Simple (short clips):**
```
"A human speech with a calm, explanatory tone is heard, accompanied by intermittent bird chirps in an outdoor setting."
```

**Complex (multi-source):**
```
"Electronic music with techno and trance characteristics is prominently present, featuring a groovy piano melody intertwined with synth pads. Shimmering hi-hat patterns and a persistent 4-on-the-floor kick drum drive the rhythmic foundation. Reverberant synth lines evolve dynamically alongside an echoing female vocal component that adds atmospheric depth."
```

---

## Dataset Construction

### Source Audio
Audio clips from **AudioSet**, a large-scale audio event dataset:
- YouTube audio segments (10-second clips)
- Diverse content: music, speech, environmental sounds, animals, vehicles, etc.
- Original AudioSet ontology of 527+ sound classes

### Caption Generation
Captions sourced from **FusionAudio-1.2M**:
1. **Multi-modal integration**: Combines audio analysis with visual, textual, and contextual cues
2. **Fine-grained descriptions**: Detailed acoustic and semantic information
3. **Context-aware**: Considers environmental and situational factors
4. **Quality filtering**: Captions validated for accuracy and detail

### Train/Test Split
- **Train set**: 1,200,000 samples for model training
- **Test set**: 27,675 samples (randomly selected, no overlap with train)
- Split created with random seed 42 for reproducibility

---

## Notes
- All audio files are sampled at **16 kHz**.
- Audio clips are approximately **10 seconds** long (range: 0.03s - 10.08s).
- Audio format is **WAV** (uncompressed).
- This dataset focuses on **descriptive captioning** rather than event classification.
- Captions are **significantly longer and more detailed** than traditional audio captioning datasets (47.6 words vs. ~10 words average).
- The dataset inherits AudioSet's diversity:
  - **Music**: Various genres, instruments, vocal styles
  - **Speech**: Conversations, monologues, broadcasts
  - **Environmental sounds**: Nature, urban, indoor, outdoor
  - **Mechanical sounds**: Vehicles, tools, machinery
  - **Animal sounds**: Domestic and wild animals
- **Caption style characteristics**:
  - Use of technical audio terms (e.g., "reverberant", "timbre", "4-on-the-floor kick")
  - Descriptive language for acoustic properties
  - Temporal descriptions of sound evolution
  - Inferred contextual information
- The dataset is particularly valuable for:
  - **Audio-to-text generation**: Training models to describe audio content
  - **Multi-modal learning**: Bridging audio and language understanding
  - **Fine-grained audio understanding**: Detailed acoustic analysis
  - **Content accessibility**: Generating descriptions for hearing-impaired users
  - **Audio search and retrieval**: Text-based audio indexing
- **Comparison to other datasets**:
  - **AudioCaps**: ~10 words per caption, simpler descriptions
  - **Clotho**: ~15 words per caption, moderate detail
  - **FusionAudio/AudioSet**: ~48 words per caption, rich contextual detail
- **Modeling challenges**:
  - Long caption generation (47+ words)
  - Fine-grained acoustic detail recognition
  - Multi-source sound disentanglement
  - Temporal reasoning over 10-second clips
  - Balancing acoustic accuracy with contextual interpretation
- Captions may include:
  - Sound source identification
  - Acoustic characteristic description
  - Environmental context inference
  - Temporal progression description
  - Emotional or stylistic interpretation
  - Spatial and relational information

---

## Evaluation Metrics

Audio captioning models are typically evaluated using:
- **BLEU**: N-gram overlap with reference captions
- **METEOR**: Semantic similarity with synonym matching
- **ROUGE-L**: Longest common subsequence
- **CIDEr**: Consensus-based image description evaluation (adapted for audio)
- **SPICE**: Semantic propositional content evaluation
- **SPIDEr**: Average of CIDEr and SPICE

Human evaluation dimensions:
- **Relevance**: How well caption matches audio content
- **Fluency**: Grammatical correctness and readability
- **Detail**: Richness of descriptive information
- **Accuracy**: Correctness of sound source identification

---

## Modeling Approaches

### 1. End-to-End Audio Encoder-Decoder
```
Audio → CNN/Transformer Encoder → Decoder (LSTM/Transformer) → Caption
```
**Example**: PANNs + Transformer decoder

### 2. Pre-trained Audio Representations
```
Audio → Pre-trained Encoder (CLAP, AudioMAE) → Language Model → Caption
```
**Example**: CLAP features + GPT-style decoder

### 3. Multi-modal Fusion
```
Audio → [Audio Features + Visual Context] → Fusion → Language Generation
```
**Example**: CLIP-like audio-visual alignment

---

## Citation

If using this dataset, please cite:

```bibtex
@article{fusionaudio2024,
  title={FusionAudio: A Large-Scale Dataset for Fine-Grained Audio Captioning},
  author={[Authors TBD]},
  journal={arXiv preprint},
  year={2024}
}

@inproceedings{audioset2017,
  title={Audio Set: An ontology and human-labeled dataset for audio events},
  author={Gemmeke, Jort F and Ellis, Daniel PW and Freedman, Dylan and Jansen, Aren and Lawrence, Wade and Moore, R Channing and Plakal, Manoj and Ritter, Marvin},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={776--780},
  year={2017},
  organization={IEEE}
}
```

## References
- FusionAudio dataset: https://huggingface.co/datasets/SatsukiVie/FusionAudio
- AudioSet: https://research.google.com/audioset/
- Original AudioSet contains 2M+ human-labeled 10-second clips
- FusionAudio provides 1.2M detailed captions and 6M QA pairs
- Caption source combines audio analysis with multi-modal contextual cues
