# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-07-15 10:09:59.366334
- Finished: 2026-07-15 10:10:01.266662

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15 10:09:59.371406**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15 10:10:00.023035**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15 10:10:00.047943**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-15 10:10:00.0596**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-15 10:10:00.696714**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-15 10:10:00.73464**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-07-15 10:10:00.740939**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-07-15 10:10:00.746382**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-15 10:10:00.752416**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-15 10:10:00.757943**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-07-15 10:10:00.7648**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-07-15 10:10:00.835956**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: b54d2cdc1945522b1b84c2dec9b9fda3
- **2026-07-15 10:10:00.86875**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-07-15 10:10:00.90182**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-07-15 10:10:01.051672**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: d5cb85fe8274db49ba39aae66f65e3bc
- **2026-07-15 10:10:01.06225**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: 3f5dd9da82e0df1f1029fcd672638b81
- **2026-07-15 10:10:01.076623**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: fa3bd0c33640193b2fe5e5995e335045
- **2026-07-15 10:10:01.228491**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: 3edbf58752255c2fbb5f2603916af6b6
- **2026-07-15 10:10:01.248139**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 044d91691e18bc617b6ac8cb5cd6eeb2
