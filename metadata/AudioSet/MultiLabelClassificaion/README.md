# AudioSet

## Overview
**AudioSet** consists of an expanding ontology of **632 audio event classes** and a collection of over **2 million** human-labeled 10-second sound clips drawn from YouTube videos. The ontology is organized as a hierarchical graph covering a wide range of human and animal sounds, musical instruments and genres, and everyday environmental sounds.

## Supported Tasks
1. **Multi-Label Audio Event Classification**

---

## Dataset Statistics

| Split | # Samples |
|------|----------:|
| train | 1,782,501 |
| test | 17,354 |

---

## Data Format

Each sample is stored as a JSON entry with the following fields:

| Field | Description |
|------|-------------|
| `id` | Unique clip ID |
| `path` | Path to audio file |
| `sampling_rate` | Audio sampling rate |
| `duration` | Audio duration in seconds |
| `dataset` | Source subset |
| `audio_events` | Ground-truth audio event labels |

---

## Example Entries

```json
{"id": "KXx4m6v4TEo_270_280", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/KXx4m6v4TEo.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "unbalanced", "audio_events": "Guitar; Acoustic guitar; Music; Musical instrument; Speech; Plucked string instrument"}

{"id": "Crz5VpdpDII_30_40", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/Crz5VpdpDII.wav", "sampling_rate": 16000, "duration": 9.984, "dataset": "unbalanced", "audio_events": "Music; Speech"}

{"id": "gLQL4gVAHQk_29_39", "path": "/saltpool0/data/tseng/FullSpectrumDataset/audio/AudioSet/unbalanced/gLQL4gVAHQk.wav", "sampling_rate": 16000, "duration": 10.016, "dataset": "unbalanced", "audio_events": "Music"}
```

---

## Task Usage

### 1. Multi-Label Audio Event Classification
- **Target field:** `audio_events` (semicolon-separated audio event labels)

---

## Label Space

### Audio Event Labels
<details>
<summary>Show 515 available labels in this manifest:</summary>

`Speech`; `Male speech, man speaking`; `Female speech, woman speaking`; `Child speech, kid speaking`; `Conversation`; `Narration, monologue`; `Babbling`; `Speech synthesizer`; `Shout`; `Bellow`; `Whoop`; `Yell`; `Battle cry`; `Children shouting`; `Screaming`; `Whispering`; `Laughter`; `Baby laughter`; `Giggle`; `Snicker`; `Belly laugh`; `Chuckle, chortle`; `Crying, sobbing`; `Baby cry, infant cry`; `Whimper`; `Wail, moan`; `Sigh`; `Singing`; `Choir`; `Yodeling`; `Chant`; `Mantra`; `Male singing`; `Female singing`; `Child singing`; `Synthetic singing`; `Rapping`; `Humming`; `Groan`; `Grunt`; `Whistling`; `Breathing`; `Wheeze`; `Snoring`; `Gasp`; `Pant`; `Snort`; `Cough`; `Throat clearing`; `Sneeze`; `Sniff`; `Run`; `Shuffle`; `Walk, footsteps`; `Chewing, mastication`; `Biting`; `Gargling`; `Stomach rumble`; `Burping, eructation`; `Hiccup`; `Fart`; `Hands`; `Finger snapping`; `Clapping`; `Heart sounds, heartbeat`; `Cheering`; `Applause`; `Chatter`; `Crowd`; `Hubbub, speech noise, speech babble`; `Children playing`; `Animal`; `Domestic animals, pets`; `Dog`; `Bark`; `Yip`; `Howl`; `Bow-wow`; `Growling`; `Whimper (dog)`; `Cat`; `Purr`; `Meow`; `Hiss`; `Caterwaul`; `Livestock, farm animals, working animals`; `Horse`; `Clip-clop`; `Neigh, whinny`; `Cattle, bovinae`; `Moo`; `Cowbell`; `Pig`; `Oink`; `Goat`; `Bleat`; `Sheep`; `Fowl`; `Chicken, rooster`; `Cluck`; `Crowing, cock-a-doodle-doo`; `Turkey`; `Gobble`; `Duck`; `Quack`; `Goose`; `Honk`; `Wild animals`; `Roaring cats (lions, tigers)`; `Roar`; `Bird`; `Bird vocalization, bird call, bird song`; `Chirp, tweet`; `Squawk`; `Pigeon, dove`; `Coo`; `Crow`; `Caw`; `Owl`; `Hoot`; `Bird flight, flapping wings`; `Canidae, dogs, wolves`; `Rodents, rats, mice`; `Mouse`; `Insect`; `Cricket`; `Mosquito`; `Fly, housefly`; `Buzz`; `Bee, wasp, etc.`; `Frog`; `Croak`; `Snake`; `Rattle`; `Whale vocalization`; `Music`; `Musical instrument`; `Plucked string instrument`; `Guitar`; `Electric guitar`; `Bass guitar`; `Acoustic guitar`; `Steel guitar, slide guitar`; `Tapping (guitar technique)`; `Strum`; `Banjo`; `Sitar`; `Mandolin`; `Zither`; `Ukulele`; `Keyboard (musical)`; `Piano`; `Electric piano`; `Organ`; `Electronic organ`; `Hammond organ`; `Synthesizer`; `Sampler`; `Harpsichord`; `Percussion`; `Drum kit`; `Drum machine`; `Drum`; `Snare drum`; `Rimshot`; `Drum roll`; `Bass drum`; `Timpani`; `Tabla`; `Cymbal`; `Hi-hat`; `Wood block`; `Tambourine`; `Rattle (instrument)`; `Maraca`; `Gong`; `Tubular bells`; `Mallet percussion`; `Marimba, xylophone`; `Glockenspiel`; `Vibraphone`; `Steelpan`; `Orchestra`; `Brass instrument`; `French horn`; `Trumpet`; `Trombone`; `Bowed string instrument`; `String section`; `Violin, fiddle`; `Pizzicato`; `Cello`; `Double bass`; `Wind instrument, woodwind instrument`; `Flute`; `Saxophone`; `Clarinet`; `Harp`; `Bell`; `Church bell`; `Jingle bell`; `Bicycle bell`; `Tuning fork`; `Chime`; `Wind chime`; `Change ringing (campanology)`; `Harmonica`; `Accordion`; `Bagpipes`; `Didgeridoo`; `Shofar`; `Theremin`; `Singing bowl`; `Scratching (performance technique)`; `Pop music`; `Hip hop music`; `Beatboxing`; `Rock music`; `Heavy metal`; `Punk rock`; `Grunge`; `Progressive rock`; `Rock and roll`; `Psychedelic rock`; `Rhythm and blues`; `Soul music`; `Reggae`; `Country`; `Swing music`; `Bluegrass`; `Funk`; `Folk music`; `Middle Eastern music`; `Jazz`; `Disco`; `Classical music`; `Opera`; `Electronic music`; `House music`; `Techno`; `Dubstep`; `Drum and bass`; `Electronica`; `Electronic dance music`; `Ambient music`; `Trance music`; `Music of Latin America`; `Salsa music`; `Flamenco`; `Blues`; `Music for children`; `New-age music`; `Vocal music`; `A capella`; `Music of Africa`; `Afrobeat`; `Christian music`; `Gospel music`; `Music of Asia`; `Carnatic music`; `Music of Bollywood`; `Ska`; `Traditional music`; `Independent music`; `Background music`; `Theme music`; `Jingle (music)`; `Soundtrack music`; `Lullaby`; `Video game music`; `Christmas music`; `Dance music`; `Wedding music`; `Happy music`; `Funny music`; `Sad music`; `Tender music`; `Exciting music`; `Angry music`; `Scary music`; `Wind`; `Rustling leaves`; `Wind noise (microphone)`; `Thunderstorm`; `Thunder`; `Water`; `Rain`; `Raindrop`; `Rain on surface`; `Stream`; `Waterfall`; `Ocean`; `Waves, surf`; `Steam`; `Gurgling`; `Fire`; `Crackle`; `Vehicle`; `Boat, Water vehicle`; `Sailboat, sailing ship`; `Rowboat, canoe, kayak`; `Motorboat, speedboat`; `Ship`; `Motor vehicle (road)`; `Car`; `Vehicle horn, car horn, honking`; `Toot`; `Car alarm`; `Power windows, electric windows`; `Skidding`; `Tire squeal`; `Car passing by`; `Race car, auto racing`; `Truck`; `Air brake`; `Air horn, truck horn`; `Reversing beeps`; `Ice cream truck, ice cream van`; `Bus`; `Emergency vehicle`; `Police car (siren)`; `Ambulance (siren)`; `Fire engine, fire truck (siren)`; `Motorcycle`; `Traffic noise, roadway noise`; `Rail transport`; `Train`; `Train whistle`; `Train horn`; `Railroad car, train wagon`; `Train wheels squealing`; `Subway, metro, underground`; `Aircraft`; `Aircraft engine`; `Jet engine`; `Propeller, airscrew`; `Helicopter`; `Fixed-wing aircraft, airplane`; `Bicycle`; `Skateboard`; `Engine`; `Light engine (high frequency)`; `Dental drill, dentist's drill`; `Lawn mower`; `Chainsaw`; `Medium engine (mid frequency)`; `Heavy engine (low frequency)`; `Engine starting`; `Idling`; `Accelerating, revving, vroom`; `Door`; `Doorbell`; `Ding-dong`; `Sliding door`; `Slam`; `Knock`; `Tap`; `Squeak`; `Cupboard open or close`; `Drawer open or close`; `Dishes, pots, and pans`; `Cutlery, silverware`; `Chopping (food)`; `Frying (food)`; `Microwave oven`; `Blender`; `Water tap, faucet`; `Sink (filling or washing)`; `Bathtub (filling or washing)`; `Hair dryer`; `Toilet flush`; `Toothbrush`; `Electric toothbrush`; `Vacuum cleaner`; `Zipper (clothing)`; `Keys jangling`; `Coin (dropping)`; `Scissors`; `Electric shaver, electric razor`; `Shuffling cards`; `Typing`; `Typewriter`; `Computer keyboard`; `Writing`; `Alarm`; `Telephone`; `Telephone bell ringing`; `Ringtone`; `Telephone dialing, DTMF`; `Dial tone`; `Busy signal`; `Alarm clock`; `Siren`; `Civil defense siren`; `Buzzer`; `Smoke detector, smoke alarm`; `Fire alarm`; `Foghorn`; `Whistle`; `Steam whistle`; `Mechanisms`; `Ratchet, pawl`; `Clock`; `Tick`; `Tick-tock`; `Gears`; `Pulleys`; `Sewing machine`; `Mechanical fan`; `Air conditioning`; `Cash register`; `Printer`; `Camera`; `Single-lens reflex camera`; `Tools`; `Hammer`; `Jackhammer`; `Sawing`; `Filing (rasp)`; `Sanding`; `Power tool`; `Drill`; `Explosion`; `Gunshot, gunfire`; `Machine gun`; `Artillery fire`; `Cap gun`; `Fireworks`; `Firecracker`; `Burst, pop`; `Eruption`; `Boom`; `Wood`; `Chop`; `Splinter`; `Crack`; `Glass`; `Chink, clink`; `Shatter`; `Liquid`; `Splash, splatter`; `Slosh`; `Squish`; `Drip`; `Pour`; `Trickle, dribble`; `Gush`; `Fill (with liquid)`; `Spray`; `Pump (liquid)`; `Stir`; `Boiling`; `Sonar`; `Arrow`; `Whoosh, swoosh, swish`; `Thump, thud`; `Thunk`; `Effects unit`; `Chorus effect`; `Basketball bounce`; `Bang`; `Slap, smack`; `Whack, thwack`; `Smash, crash`; `Breaking`; `Bouncing`; `Whip`; `Flap`; `Scratch`; `Scrape`; `Rub`; `Crushing`; `Crumpling, crinkling`; `Tearing`; `Beep, bleep`; `Ping`; `Ding`; `Clang`; `Squeal`; `Creak`; `Rustle`; `Whir`; `Sizzle`; `Clicking`; `Clickety-clack`; `Rumble`; `Plop`; `Jingle, tinkle`; `Hum`; `Zing`; `Boing`; `Crunch`; `Silence`; `Sine wave`; `Chirp tone`; `Sound effect`; `Pulse`; `Inside, small room`; `Inside, large room or hall`; `Inside, public space`; `Outside, urban or manmade`; `Outside, rural or natural`; `Reverberation`; `Echo`; `Noise`; `Environmental noise`; `Static`; `Mains hum`; `Distortion`; `Cacophony`; `White noise`; `Pink noise`; `Throbbing`; `Television`; `Radio`

</details>

---

## Notes
- All audio files are sampled at **16 kHz**.
- Each clip is approximately **10 seconds** long.
- This is a **multi-label** classification task: each clip may contain one, or multiple event labels.
- In this manifest, labels are stored in the `audio_events` field as a **semicolon-separated string**.
- The original AudioSet ontology contains **632 classes**, while this manifest exposes **515 available labels** for all available audio files.
- There is no `dev` split in the provided manifest.
- If your manifest uses exact string labels, keep the README label names identical to the manifest values.