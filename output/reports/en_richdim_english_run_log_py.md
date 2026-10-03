# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-10-03T09:52:47
- Finished: 2026-10-03T09:52:51

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03T09:52:47**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03T09:52:48**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03T09:52:48**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-03T09:52:48**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-03T09:52:50**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [4.90, 6.24], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.23, 0.38], TOST p = 0.0113 (equivalent)
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-10-03T09:52:50**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-10-03T09:52:50**: wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-10-03T09:52:50**: wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-10-03T09:52:50**: wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: c6e0f0a19b0b176fdd5a9ad80946e658
- **2026-10-03T09:52:51**: wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: ef7ebc10229e3d031c02ea4ae56b8fc1
- **2026-10-03T09:52:51**: wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: ff4c4663416e45f9cbb882d29f4b1fc3
- **2026-10-03T09:52:51**: wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: 6886e9083af3453ef3c5f23124bcadcd
- **2026-10-03T09:52:51**: wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: 788579f7b7fbc4b14f3cb9cd4072d032
- **2026-10-03T09:52:51**: wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: e64b00089df3b7bef68b219811542b92
