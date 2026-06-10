# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-10T09:34:22
- Finished: 2026-06-10T09:34:23

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-10T09:34:22** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-10T09:34:22** -- lexicon loaded: 29999 words
    - words: 29999
- **2026-06-10T09:34:22** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-10T09:34:23** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-10T09:34:23** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00, TOST p = 0.0009 (equivalent)
- **2026-06-10T09:34:23** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00, TOST p = 0.0009 (equivalent)
- **2026-06-10T09:34:23** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11, TOST p = 1.0 (not shown equivalent)
- **2026-06-10T09:34:23** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30, TOST p = 1.0 (not shown equivalent)
- **2026-06-10T09:34:23** -- wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 0d28c958b33f6c231b3fb9f643719c33
- **2026-06-10T09:34:23** -- wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 8cc1ceef86f156a10f0505a97bd71783
- **2026-06-10T09:34:23** -- wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 54ab26b0b53c83ab7d6cf11f40dff52c
- **2026-06-10T09:34:23** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: c29db3b7a22197db8eec937979d8ce65
- **2026-06-10T09:34:23** -- wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 46c4ab4a2ff889255b59e7b04fc638c8
