# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-09-24 17:00:18.344947
- Finished: 2026-09-24 17:00:19.785584

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 17:00:18.35353**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-09-24 17:00:19.224441**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-09-24 17:00:19.230247**: pool after filters: 131 words
    - pool: 131
- **2026-09-24 17:00:19.24431**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-09-24 17:00:19.292021**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-09-24 17:00:19.298998**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 17:00:19.309175**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-09-24 17:00:19.31424**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-09-24 17:00:19.343915**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-09-24 17:00:19.366226**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-09-24 17:00:19.385492**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: 35a87203c30fae56f60a96fc70db958c
- **2026-09-24 17:00:19.516057**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-09-24 17:00:19.534274**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-09-24 17:00:19.550001**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 96361646fdb301915726601716042d9e
- **2026-09-24 17:00:19.75657**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: cee38f9b0c3ccf63c0bb4a860db13c02
- **2026-09-24 17:00:19.772214**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: ba13eab61d9e81d10c7a822b927bc220
