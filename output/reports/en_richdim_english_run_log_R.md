# lexsync run log: en_richdim

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:02.604734
- Finished: 2026-09-02 19:25:03.333107

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:02.605014**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:25:02.825639**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:25:02.831416**: pool after filters: 10205 words
    - pool: 10205
- **2026-09-02 19:25:02.831671**: computing bigram frequency (phonotactic-probability proxy)
- **2026-09-02 19:25:03.262393**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:25:03.27539**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-09-02 19:25:03.275638**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:03.27582**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.0110 (equivalent)
- **2026-09-02 19:25:03.276007**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.0113 (equivalent)
- **2026-09-02 19:25:03.276134**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-09-02 19:25:03.276253**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-09-02 19:25:03.285306**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-09-02 19:25:03.28785**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-09-02 19:25:03.296191**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-09-02 19:25:03.313076**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: e6de3c3e8c705de36f74898fbc51ce28
- **2026-09-02 19:25:03.31334**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-09-02 19:25:03.313458**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 0b2ff69af1a01d76e455f899e2c0809c
- **2026-09-02 19:25:03.332669**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: ab432deca720a0bfc48a542229aaf47a
- **2026-09-02 19:25:03.332936**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 72badf0fb8e71e8235b87085af1f8a55
