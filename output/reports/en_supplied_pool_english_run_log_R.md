# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-07-30 15:20:58.725226
- Finished: 2026-07-30 15:21:00.132086

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:20:58.72991**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-07-30 15:20:59.487319**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-07-30 15:20:59.50036**: pool after filters: 131 words
    - pool: 131
- **2026-07-30 15:20:59.53008**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-07-30 15:20:59.562583**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-07-30 15:20:59.570746**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [3.00, 4.06], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:20:59.581023**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-07-30 15:20:59.591532**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-07-30 15:20:59.628726**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-07-30 15:20:59.653091**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 67befed7f76a1bf7977a55f7ee2c3d12
- **2026-07-30 15:20:59.686877**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: a6ed40f01c6a55726fccd8f520ab8333
- **2026-07-30 15:20:59.825679**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-07-30 15:20:59.850631**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-07-30 15:20:59.87193**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: ad63841f4f114db7d8afa8b04bb2aa77
- **2026-07-30 15:21:00.086953**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 1e3161ca41963a38d9010a356319ca01
- **2026-07-30 15:21:00.109031**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 8918990bbfcdf9169a31832f58cc0e46
