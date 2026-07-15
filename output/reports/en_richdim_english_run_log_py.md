# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-07-15T10:11:57
- Finished: 2026-07-15T10:11:58

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15T10:11:57**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15T10:11:57**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15T10:11:57**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-15T10:11:57**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-15T10:11:57**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.0 (not shown equivalent)
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.0113 (equivalent)
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-07-15T10:11:57**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-07-15T10:11:57**: wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: 24138763235d096d4c4f4252352a9b56
- **2026-07-15T10:11:57**: wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: 9871df69cf22314c6cb03c8bb543f333
- **2026-07-15T10:11:57**: wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: 6bdc533352f8073af39378069edad031
- **2026-07-15T10:11:57**: wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: 3813dea43daedb4dc4001e8a9b195876
- **2026-07-15T10:11:57**: wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-07-15T10:11:57**: wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: d72b4b0bd04268f5d9ca38f6b03186e8
- **2026-07-15T10:11:58**: wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: 761ad3bd13ceea449eb88f5b9291156d
- **2026-07-15T10:11:58**: wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: fbd1601fb311dd9f530159569c28fb23
