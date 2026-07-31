# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:30.183957
- Finished: 2026-07-31 21:48:30.756883

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:30.186403**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-07-31 21:48:30.494088**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-07-31 21:48:30.497699**: pool after filters: 131 words
    - pool: 131
- **2026-07-31 21:48:30.504034**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-07-31 21:48:30.520678**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-07-31 21:48:30.525416**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [3.00, 4.06], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:30.528566**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-07-31 21:48:30.531047**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-07-31 21:48:30.550783**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-07-31 21:48:30.565428**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-07-31 21:48:30.581165**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: a6ed40f01c6a55726fccd8f520ab8333
- **2026-07-31 21:48:30.637778**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-07-31 21:48:30.647466**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-07-31 21:48:30.654983**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: ad63841f4f114db7d8afa8b04bb2aa77
- **2026-07-31 21:48:30.738463**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 053789972afd9c35d299ff93d205f2f7
- **2026-07-31 21:48:30.748388**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 8918990bbfcdf9169a31832f58cc0e46
