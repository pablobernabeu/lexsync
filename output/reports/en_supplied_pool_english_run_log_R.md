# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-15 03:29:37.473016
- Finished: 2026-10-15 03:29:40.643192

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 03:29:37.481772**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15 03:29:37.488361**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-15 03:29:39.517022**: supplied pool: 131 words (dimensions from 'corpora/derived/en_v2.csv')
    - words: 131
    - lexicon: corpora/derived/en_v2.csv
- **2026-10-15 03:29:39.525058**: pool after filters: 131 words
    - pool: 131
- **2026-10-15 03:29:39.549263**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-15 03:29:39.869204**: equivalence lower_frequency vs higher_frequency on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-15 03:29:39.878095**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.51 [2.66, 4.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 03:29:39.88587**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.18 [-0.36, 0.71], TOST p = 0.157 (not shown equivalent)
- **2026-10-15 03:29:39.895792**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.14 [-0.67, 0.39], TOST p = 0.131 (not shown equivalent)
- **2026-10-15 03:29:39.904432**: equivalence lower_frequency vs higher_frequency on 'n_syllables': d = 0.14 [-0.40, 0.67], TOST p = 0.130 (not shown equivalent)
- **2026-10-15 03:29:39.911486**: equivalence lower_frequency vs higher_frequency on 'bigram_freq': d = 0.62 [0.08, 1.17], TOST p = 0.651 (not shown equivalent)
- **2026-10-15 03:29:39.953048**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 326f0865b15a1420c09af4c155fd1368
- **2026-10-15 03:29:39.983795**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 12
    - md5: ad9da0a92065faccb3515559bbc5b1e0
- **2026-10-15 03:29:40.009912**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 6
    - md5: a134fbdbbdb5624cea325f608fb54911
- **2026-10-15 03:29:40.283835**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: fb264d2cb7a63cb2aadb4d0587819eb6
- **2026-10-15 03:29:40.298137**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: d2bc56f9954a15ec7ff067ea3e7010f5
- **2026-10-15 03:29:40.315619**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 224936f2ded2f01ae2abf16983d17e96
- **2026-10-15 03:29:40.335482**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 91cf227f235cdce35ad90c1c8201a432
- **2026-10-15 03:29:40.347349**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-15 03:29:40.361525**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: c95cb1f947b24b55ffe98ed33aaae5cb
- **2026-10-15 03:29:40.611064**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 89c217a7940b491cb5000a283d3301f2
- **2026-10-15 03:29:40.627951**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 644b3aceee9131be21b7ed73aac3d4c6
