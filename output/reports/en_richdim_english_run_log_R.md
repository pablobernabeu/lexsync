# lexsync run log: en_richdim

- Engine: R 4.6.0
- Started: 2026-07-06 08:56:42.436932
- Finished: 2026-07-06 08:56:44.303587

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06 08:56:42.444716**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-06 08:56:43.136699**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-06 08:56:43.157405**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-06 08:56:43.164119**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-06 08:56:43.864561**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-06 08:56:43.903848**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-07-06 08:56:43.910903**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:43.918964**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-06 08:56:43.926804**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-06 08:56:43.933788**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-07-06 08:56:43.940089**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-07-06 08:56:43.979274**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: b54d2cdc1945522b1b84c2dec9b9fda3
- **2026-07-06 08:56:44.003411**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-07-06 08:56:44.027341**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-07-06 08:56:44.139813**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: d5cb85fe8274db49ba39aae66f65e3bc
- **2026-07-06 08:56:44.15297**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: 3f5dd9da82e0df1f1029fcd672638b81
- **2026-07-06 08:56:44.163292**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: fa3bd0c33640193b2fe5e5995e335045
- **2026-07-06 08:56:44.27619**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: e0486b26468777dccfae114ac289bdd1
- **2026-07-06 08:56:44.29138**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 31af8ef400696d8f0cc605d43751a397
