# lexsync run log: en_richdim

- Engine: R 4.5.1
- Started: 2026-06-13 22:44:12.113264
- Finished: 2026-06-13 22:44:13.173413

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:44:12.113599** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 22:44:12.540814** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:44:12.546362** -- pool after filters: 10205 words
    - pool: 10205
- **2026-06-13 22:44:12.54664** -- computing bigram frequency (phonotactic-probability proxy)
- **2026-06-13 22:44:12.939115** -- matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 22:44:12.951278** -- equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-06-13 22:44:12.951522** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:44:12.951705** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-06-13 22:44:12.951867** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-06-13 22:44:12.952018** -- equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-06-13 22:44:12.952165** -- equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-06-13 22:44:12.97536** -- wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: b54d2cdc1945522b1b84c2dec9b9fda3
- **2026-06-13 22:44:12.987151** -- wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-06-13 22:44:12.996811** -- wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 162f35b51b1447f53296db33e95dcff5
- **2026-06-13 22:44:13.070084** -- wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: 274e323bb1488dcbf9b98ab94cffce55
- **2026-06-13 22:44:13.075681** -- wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: 3f5dd9da82e0df1f1029fcd672638b81
- **2026-06-13 22:44:13.080547** -- wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 34c49a3b2a987cd56be507e91cb8289b
- **2026-06-13 22:44:13.160778** -- wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: d9fa9f74815716fd7bea9eb48d538427
- **2026-06-13 22:44:13.167044** -- wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 9f6501bf955989c60ce5add350e46762
