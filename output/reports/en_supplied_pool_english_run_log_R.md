# lexsync run log: en_supplied_pool

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:03.382848
- Finished: 2026-09-02 19:25:03.68957

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:03.383069**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-09-02 19:25:03.630605**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-09-02 19:25:03.63091**: pool after filters: 131 words
    - pool: 131
- **2026-09-02 19:25:03.635818**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-09-02 19:25:03.651255**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.1121 (not shown equivalent)
- **2026-09-02 19:25:03.651504**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [3.00, 4.06], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:03.651654**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.1245 (not shown equivalent)
- **2026-09-02 19:25:03.65179**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.2093 (not shown equivalent)
- **2026-09-02 19:25:03.656847**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-09-02 19:25:03.659053**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-09-02 19:25:03.660924**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: a6ed40f01c6a55726fccd8f520ab8333
- **2026-09-02 19:25:03.673317**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: db685471ea7d349bf708ed0e3434b085
- **2026-09-02 19:25:03.673537**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-09-02 19:25:03.673628**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 02b986a4f7aa3ba7f242afa29777a16c
- **2026-09-02 19:25:03.689271**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: c9901ad1813f04314baf63f36b0bcd6e
- **2026-09-02 19:25:03.689442**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: dddac013cdff32921016747a7997ebf7
