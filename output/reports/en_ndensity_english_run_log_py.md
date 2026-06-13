# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-13T18:36:36
- Finished: 2026-06-13T18:36:37

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13T18:36:36** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13T18:36:36** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13T18:36:36** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-13T18:36:37** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13T18:36:37** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-06-13T18:36:37** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-06-13T18:36:37** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T18:36:37** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T18:36:37** -- wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: b8542de0e4688c9b4246fd0f5b875f9d
- **2026-06-13T18:36:37** -- wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 8cc1ceef86f156a10f0505a97bd71783
- **2026-06-13T18:36:37** -- wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 7a93f04c80a5e54f609193e3843fc637
- **2026-06-13T18:36:37** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 8b254968619c4889327672536fff0ad7
- **2026-06-13T18:36:37** -- wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 31ddd059946537b3cf64de30861215f2
