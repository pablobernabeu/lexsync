# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-07-23T00:27:49
- Finished: 2026-07-23T00:27:51

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-23T00:27:49**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-23T00:27:50**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-23T00:27:50**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-23T00:27:50**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-23T00:27:50**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.0045 (equivalent)
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.0 (not shown equivalent)
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.0113 (equivalent)
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.0383 (equivalent)
- **2026-07-23T00:27:51**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.0041 (equivalent)
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: 074bccb5c87a0b7d97423bb7bb160e8c
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: 9871df69cf22314c6cb03c8bb543f333
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: 6bdc533352f8073af39378069edad031
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: c4f31d3faeadb3ede9ddd4c1a7328187
- **2026-07-23T00:27:51**: wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-07-23T00:27:51**: wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: 1444f879d6df642a99309de1d86fb6ec
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: b550fa59ded62571a99d1b0134125d98
- **2026-07-23T00:27:51**: wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: a3f020e5ee229f5bd658b5663048a5b7
