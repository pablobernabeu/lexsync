# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-07-03T00:10:11
- Finished: 2026-07-03T00:10:12

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03T00:10:11**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03T00:10:11**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03T00:10:11**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-03T00:10:11**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-03T00:10:12**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.0 (not shown equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.0113 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: b59ec17fabec7b0ad558c41d7a6f4839
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: a7878942ac61b677b087914065acaeb1
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: f6fec342b0640996bac522238b06bf60
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: 8957f80a723b0122e441a5b7dfe9e941
- **2026-07-03T00:10:12**: wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: 6e171082bb99c5729670146a45a993d3
- **2026-07-03T00:10:12**: wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: 4774b8531e5a9b61d75aedfd8c3f1473
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: be68a01d5a410ceaa019ee108205515d
- **2026-07-03T00:10:12**: wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: 86bf8dca5b8a646289532f60f46f57cc
