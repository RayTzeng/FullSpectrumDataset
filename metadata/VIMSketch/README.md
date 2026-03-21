# VIMSketch

## Overview
**VIMSketch** is a dataset for query-by-vocal-imitation research that pairs human vocal imitations with target sounds, enabling systems to retrieve sounds based on how people imitate them with their voices. The dataset combines two earlier Interactive Audio Lab datasets and contains **416 reference sounds** together with **11,619 vocal imitations**, spanning categories such as animal sounds, musical excerpts, and environmental noises.

## Supported Tasks
1. **Vocal Imitation Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 10,480 |
| test | 1,139 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique vocal imitation ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source subset (VocalImitationSet or VocalSketch) |
| `imitation_ref` | Ground-truth reference sound being imitated |

---

## Example Entries

```json
{"id": "VocalImitationSet_967", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/VocalSketch/VocalImitationSet/VocalImitationSet/vocal_imitations/included/028Animal_Wild animals_Roaring cats (lions_ tigers)_Roar-5192735183077376.wav", "sampling_rate": 48000, "duration": 4.778667, "dataset": "VocalImitationSet", "imitation_ref": "roar"}

{"id": "VocalSketch_can crush - 6622804405387264", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/VocalSketch/VocalSketch/interactiveaudiolab-VocalSketchDataSet-6c9f381/vocal_imitations_set2/included/can crush - 6622804405387264.wav", "sampling_rate": 48000, "duration": 1.877333, "dataset": "VocalSketch", "imitation_ref": "can crushing"}

{"id": "VocalSketch_police siren - 5873713119494144", "path": "/saltpool0/scratch/tseng/FullSpectrumDataset/raw/VocalSketch/VocalSketch/interactiveaudiolab-VocalSketchDataSet-6c9f381/vocal_imitations/included/police siren - 5873713119494144.wav", "sampling_rate": 44100, "duration": 3.020068, "dataset": "VocalSketch", "imitation_ref": "police siren"}
```

---

## Task Usage

### 1. Vocal Imitation Classification
- **Target field:** `imitation_ref` (reference sound being imitated)

---

## Label Space

### Imitation Reference Labels
<details>
<summary>Show 416 available labels:</summary>

`abyss of despair`, `accordion`, `acoustic guitar`, `air brake`, `air conditioning`, `air machine`, `airplane`, `alarm clock`, `alien discovery`, `alto saxophone`, `ambulance siren`, `anti-matter clouds`, `applause`, `artillery fire`, `audio feedback`, `baby crying`, `baby laughter`, `bagpipes`, `bamboo air strings`, `bang`, `banjo`, `basketball bounce`, `bass drum`, `bass guitar`, `bassoon`, `bathtub filling`, `bell swarm`, `bicycle bell`, `bird chirp`, `bird chirping`, `bird wings flapping`, `biting`, `blender`, `boat horn`, `boiling`, `bongo drums`, `booing`, `bouncing`, `bowed cello`, `bowed crash cymbal`, `bowed vibraphone`, `bowed viola`, `bowed violin`, `bowling`, `breaking`, `bugle`, `bullet time`, `burp`, `burst / pop`, `bus`, `busy signal`, `buzz`, `buzzer`, `camera shutter`, `can crushing`, `can opening`, `cap gun`, `car alarm`, `car crash`, `car horn`, `car passing by`, `car skidding`, `cash register`, `castanets`, `cat growl`, `cat hiss`, `cat meow`, `cat purr`, `cat vocalization`, `cello`, `cellphone vibration`, `chainsaw`, `cheering`, `chewing`, `chicken cluck`, `chicken clucking`, `child coughing`, `children shouting`, `chinese cymbal`, `choir`, `choked crash cymbal`, `chuckle`, `church bell`, `church bells`, `civil defense siren`, `clapping`, `clarinet`, `claves`, `clock tick`, `clunk`, `coin drop`, `computer keyboard`, `cork pop`, `cornet`, `cow moo`, `cowbell`, `crash cymbal`, `crash cymbal roll`, `cricket`, `crickets`, `crotales`, `crow caw`, `crushing`, `cuckoo clock`, `cupboard open/close`, `cutlery`, `cyborg breathing`, `cymbal`, `dark attack bass`, `dark synth pad`, `dental drill`, `dial tone`, `didgeridoo`, `dishes / pots / pans`, `dissonant bells`, `dog bark`, `dog growl`, `dog howl`, `donkey bray`, `door closing`, `door knock`, `door slam`, `door squeak`, `doorbell`, `double bass`, `dove coo`, `drawer open/close`, `drill`, `drum machine`, `drum roll`, `drums`, `duck call`, `duck quack`, `electric guitar`, `electric piano`, `electric shaver`, `electric toothbrush`, `electrical interference`, `electronic organ`, `elephant vocalization`, `engine idling`, `engine revving`, `engine starting`, `eruption`, `euro hook`, `explosion`, `fart`, `filing`, `filter bubble`, `finger snapping`, `fire alarm`, `fire crackle`, `fire truck siren`, `firecracker`, `firecrackers`, `flap`, `flute`, `foghorn`, `food chopping`, `footsteps`, `freaky moonlight`, `french horn`, `frog croak`, `frying`, `fusillade`, `gargling`, `gasp`, `gears`, `ghost in the machine`, `giggle`, `glass breaking`, `glass clink`, `glockenspiel`, `goat bleat`, `gong`, `goose honk`, `grinding`, `groan`, `grunt`, `guitar`, `guitar strum`, `guitar tapping`, `gunshots`, `güiro`, `hair dryer`, `hammering`, `hammond organ`, `harmonica`, `harp`, `harpsichord`, `heart murmur`, `helicopter`, `hi-hat`, `hiccup`, `horn`, `horse gallop`, `horse neigh`, `horse snort`, `humming`, `ice cream truck`, `ice in glass`, `ice synth`, `instrument scratching`, `jackhammer`, `jet engine`, `jingle bell`, `kettle whistle`, `keys jangling`, `knock`, `knocking`, `laughter`, `lawn mower`, `lion roar`, `liquid filling`, `liquid pump`, `liquid spray`, `liquid squish`, `liquid stirring`, `little summer boy`, `machine gun`, `mains hum`, `mandolin`, `maraca`, `marble in glass bowl`, `marble rolling`, `marimba`, `marimba / xylophone`, `mechanical fan`, `medium engine`, `mellotron`, `metallic synth`, `metaloid`, `microwave oven`, `mister frosty`, `monkey vocalization`, `morphing can drum`, `mosquito`, `motorboat`, `motorcycle`, `mouse`, `musical ensemble`, `narrow timbre`, `needle strings`, `nose blowing`, `oboe`, `ocean waves`, `orbit station`, `orchestra`, `organ`, `owl hoot`, `page turning`, `panting`, `paper crumpling`, `paper cutting`, `paper tearing`, `photon blast`, `piano`, `pig oink`, `pinball`, `ping-pong`, `pink noise`, `pizzicato strings`, `plucked bass`, `plucked cello`, `plucked viola`, `plucked violin`, `police siren`, `power windows`, `printer`, `propeller`, `pull-chain light switch`, `pulleys`, `race car`, `rain`, `ratchet`, `rattlesnake`, `resonant clouds`, `reversed envelope`, `reversing beeps`, `rimshot`, `ringtone`, `river stream`, `roar`, `rolling`, `rooster crow`, `rowboat / canoe / kayak`, `rubbing`, `running`, `rustling leaves`, `sailboat`, `sampler`, `sanding`, `sandpaper rubbing`, `sawing`, `saxophone`, `scissors`, `scraping`, `scratching`, `screaming`, `seal vocalization`, `sewing machine`, `shadowland highs`, `sheep bleat`, `shimmer`, `ship`, `shuffling cards`, `shuffling footsteps`, `sigh`, `singing bowl`, `sink filling`, `sitar`, `skateboard`, `slap / smack`, `slide guitar`, `sliding door`, `slosh`, `slow warm swells`, `smash / crash`, `snake rattle`, `sneeze`, `sniff`, `snoring`, `soft shimmer`, `sonar`, `sonic boom`, `soprano saxophone`, `spacecraft engine`, `sparkle motion`, `stapler`, `steam hiss`, `stomach rumble`, `stream`, `string section`, `subway`, `sustained vibraphone`, `sword clash`, `synth brass`, `synth lead`, `tabla`, `tambourine`, `tambourine roll`, `tap`, `tape`, `tape hiss`, `tearing`, `telephone`, `telephone dialing`, `telephone ringing`, `thai gong`, `theremin`, `thick bass`, `throat clearing`, `thunder`, `thunk`, `tick-tock`, `timpani`, `toilet flush`, `toot`, `toothbrushing`, `traffic noise`, `train`, `train horn`, `train wagon`, `train wheels squealing`, `train whistle`, `triangle`, `trickle / dribble`, `trombone`, `truck`, `truck horn`, `trumpet`, `tuba`, `tubular bells`, `tuning fork`, `turkey gobble`, `typewriter`, `ukulele`, `vacuum cleaner`, `velcro`, `vibraphone`, `violin`, `wail / moan`, `water bubbling`, `water draining`, `water dripping`, `water gurgling`, `water pouring`, `water tap`, `waterfall`, `whack / thwack`, `whip`, `whispering`, `whistle`, `whistling`, `white noise`, `whoop`, `wind`, `wind chime`, `wind chimes`, `wind gong`, `wind howl`, `window blinds`, `wolf howl`, `wolf whistle`, `wood block`, `wood chop`, `wood crack`, `wood snap`, `wood splinter`, `woodpecker pecking`, `writing`, `xylophone`, `yawn`, `yell`, `zipper`, `zither`

</details>

---

## Notes
- Audio files have **variable sampling rates** (44.1 kHz and 48 kHz).
- Audio clips have **variable duration**, typically ranging from 1 to 5 seconds.
- This is a **single-label** classification task where each vocal imitation corresponds to one reference sound.
- The dataset combines two source datasets:
  - **VocalImitationSet**: Vocal imitations from the earlier VocalImitationSet dataset
  - **VocalSketch**: Vocal imitations from the VocalSketch dataset
- Labels represent **416 distinct reference sounds** across diverse categories including:
  - **Animal sounds** (e.g., roar, dog bark, bird chirping)
  - **Musical instruments** (e.g., piano, guitar, drums)
  - **Environmental noises** (e.g., rain, wind, traffic)
  - **Mechanical sounds** (e.g., car horn, alarm clock, helicopter)
  - **Synthetic sounds** (e.g., synth pad, resonant clouds)
- All entries with `subsynth####` labels have been removed as their definitions are unknown.
- There is no `dev` split in the provided manifest.
