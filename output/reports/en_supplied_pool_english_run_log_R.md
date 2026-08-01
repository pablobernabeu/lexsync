# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:45.392085
- Finished: 2026-08-01 00:33:45.929794

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01 00:33:45.395007**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-08-01 00:33:45.677495**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-08-01 00:33:45.681107**: pool after filters: 131 words
    - pool: 131
- **2026-08-01 00:33:45.687273**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-08-01 00:33:45.697733**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-08-01 00:33:45.700511**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [3.00, 4.06], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:45.703026**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-08-01 00:33:45.705403**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-08-01 00:33:45.719642**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-08-01 00:33:45.734308**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-08-01 00:33:45.746166**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: a6ed40f01c6a55726fccd8f520ab8333
- **2026-08-01 00:33:45.801762**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-08-01 00:33:45.810799**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-08-01 00:33:45.817203**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 049942042c0f160bef7a4b9b3a37b7ae
- **2026-08-01 00:33:45.912151**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 4a1038390f5e649ef95e498749a19cc7
- **2026-08-01 00:33:45.921638**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 8918990bbfcdf9169a31832f58cc0e46
