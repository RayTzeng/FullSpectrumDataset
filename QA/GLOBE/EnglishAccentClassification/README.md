# GLOBE / EnglishAccentClassification

QA templates and generated instruction data for accent classification on GLOBE.

| | |
|---|---|
| Target field | `accent` |
| Label type | single-label, 17 classes |
| Stage split | disjoint, `md5(id) % 4 < 3` -> Stage 1, else Stage 2 |
| Output | `{train,dev,test}.jsonl.gz`, one QA row per clip |

## The label space is not the raw field

GLOBE copies Mozilla Common Voice's **self-reported** accent field verbatim. That
field is a comma-joined mix of the 16 checkbox varieties the Common Voice profile
form offers for English and free text the contributor typed, so raw values look
like `united states english,midwestern,low,demure` or `non native speaker,german
english`. Across the three splits there are **738 distinct raw strings**, and the
comma is not a clean separator - it also appears *inside* three of the checkbox
labels, e.g. `india and south asia (india, pakistan, sri lanka)`.

`prepare_manifest.py` reduces each row to a single canonical label:

1. Split the field on commas, **never inside parentheses**.
2. Map each tag to a canonical label; keep the row only if **exactly one**
   survives. Rows resolving to zero canonical labels (pure free text) or to two
   or more (contributors who ticked several boxes) are dropped.
3. Free-text tags sitting alongside a canonical label are commentary about a
   sub-variety, not a competing class, and are discarded.
4. `accent` is overwritten with the canonical label; the original is kept as
   `accent_raw`.

**17 classes**: the 16 Common Voice checkbox varieties, plus `german english`
promoted from free text - the only non-checkbox variety with enough rows in every
split to be learnable and evaluable. Its variants (`german`, `austrian`,
`south german accent`, `alemannic german accent`, ...) are merged into it;
biographical free text such as `born in west germany in 1966` is not.

Coverage after canonicalisation, before the per-class cap:

| split | kept | 0 canonical | >=2 canonical |
|---|---:|---:|---:|
| train | 694,572 (98.6%) | 4,200 | 6,120 |
| dev | 9,415 (98.0%) | 132 | 56 |
| test | 8,941 (97.4%) | 191 | 47 |

`train` is then capped at **45,000 rows per class** (by lowest `md5(id)`, so the
choice is reproducible), which flattens `united states english` from 49% to 15%
and lands the split at 299,177 clips.

### Two caveats worth knowing

* **`northern irish` is unevaluable.** 8,197 train rows but **2 dev / 1 test**.
  That is a property of GLOBE's own split, not of this pipeline.
* **`german english` is 11.8% of the capped train set but 0.3% of dev**, and
  34,527 of its train rows carry one identical accent string - the signature of a
  single prolific contributor. The uniform per-class cap does not bind it because
  it sits below 45,000. Lower `--per-class-cap` for that class if the skew matters.

## Templates

`stage1_template.jsonl` - 209 templates asking for the label itself. The answer is
always the label exactly as stored; departures are limited to casing and JSON
wrappers, each announced in the question.

`_display` forms appear **only inside MCQ**, where the option list defines the
answer vocabulary - `options_block` renders them, so `option_of` and
`pretty_label(gold_option)` must too, and a bare `{gold_option}` (which returns the
raw label) is a silent mismatch the validator does not catch. For the same reason
there are no `order: "alpha"` templates: the sort runs on raw labels while the
question shows `_display` forms, so an "alphabetised options" claim would be false.
Free-standing `pretty_label` answers were dropped as well - `united states english`
and `American English` are two names for one thing, not two formats, so no natural
question wording reliably selects one.

`stage2_template.jsonl` - 167 templates asking what the label means, all answered
from `label_semantics.json`. Context answers name the accent before explaining
("This is Australian English. English carried to Australia by ..."), so the answer
stands on its own. Fourteen of the 22 analogical templates present a candidate set
from the `confusable_choices` slot, because "which accent is this confused with?"
is otherwise a question about an inventory the asker never showed; the correct
option's position is varied by hand across the 17 labels. Family shares: category 22%, environmental 16%,
activity 14%, context 14%, functional 14% (the five guide-sheet families, 79%
of the file), plus analogical/comparative 13% and occasion/production-fit 8%.

### The wider candidate pool

Stage-1 MCQ distractors and yes/no probes may draw from a curated set of 18
further varieties attested in GLOBE's free text (`polish english`,
`nigerian english`, `thai english`, ...). Each is semantically **disjoint** from
all 17 canonical labels, so a distractor can never be quietly correct for the row
that drew it. Deliberately excluded: regional sub-varieties (`midwestern`,
`liverpool english`, `transatlantic english`) and umbrella terms
(`british accent`, `received pronunciation`), which *would* be true of a row whose
gold label is their parent.

### What `label_semantics.json` does and does not claim

Slots describe the accent **variety and the region it comes from**, never the
individual speaker. `english_status` is a fact about a region's language
situation ("English is an official second language in India"), not a claim about
how any particular speaker acquired English. Slot values are written the way a
person would say them ("that this person grew up speaking English in Australia"),
not in sociolinguistics register. There is deliberately **no slot for
personality, class, education or ability** - inferring those from an accent is
accent prejudice, not semantics, and no template can ask for it.

## Rebuilding

```bash
M=/home/tseng/FullSpectrumDataset/metadata/GLOBE
python3 prepare_manifest.py --metadata $M/train.jsonl.gz --output manifest/train.jsonl.gz --per-class-cap 45000
python3 prepare_manifest.py --metadata $M/dev.jsonl.gz   --output manifest/dev.jsonl.gz
python3 prepare_manifest.py --metadata $M/test.jsonl.gz  --output manifest/test.jsonl.gz

for SP in train dev test; do
  python3 partition_manifest.py --metadata manifest/$SP.jsonl.gz --outdir parts/
  for ST in 1 2; do
    python3 generate_stage${ST}_qa.py --template-jsonl stage${ST}_template.jsonl \
      --metadata parts/${SP}_stage${ST}.jsonl.gz --output parts/${SP}_qa_stage${ST}.jsonl.gz \
      --samples-per-entry 1 --seed 0 --target-field accent --label-separator ';' \
      --label-semantics label_semantics.json
  done
  cat parts/${SP}_qa_stage1.jsonl.gz parts/${SP}_qa_stage2.jsonl.gz > $SP.jsonl.gz
done
```

`parts/` is intermediate and not checked in; both scripts are deterministic.
