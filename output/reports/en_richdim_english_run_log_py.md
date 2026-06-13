# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-06-13T22:46:05
- Finished: 2026-06-13T22:46:06

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13T22:46:05** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13T22:46:05** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13T22:46:05** -- pool after filters: 10205 words
    - pool: 10205
- **2026-06-13T22:46:05** -- computing bigram frequency (phonotactic-probability proxy)
- **2026-06-13T22:46:06** -- matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.0113 (equivalent)
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-06-13T22:46:06** -- equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: b59ec17fabec7b0ad558c41d7a6f4839
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: a7878942ac61b677b087914065acaeb1
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: f6fec342b0640996bac522238b06bf60
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: f5b5dd847a144a890393740815da1456
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: 6e171082bb99c5729670146a45a993d3
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: bd4e0073fe54d42f5688e271683b6000
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: 91a2bd709f8f642ee919eb61f6c52bc8
- **2026-06-13T22:46:06** -- wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: 7609bd1fd194b836c656cf379e9d814d
