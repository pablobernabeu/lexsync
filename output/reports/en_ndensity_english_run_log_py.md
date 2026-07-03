# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-03T10:38:35
- Finished: 2026-07-03T10:38:36

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03T10:38:35**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03T10:38:35**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03T10:38:35**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-03T10:38:35**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-03T10:38:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-03T10:38:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-03T10:38:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-07-03T10:38:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 80f0176a9a0cd356d1db311b3b4e9474
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 8cc1ceef86f156a10f0505a97bd71783
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 8185f94fd6f61df894f2ea02372d1b2d
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: cd57e22a049650969a1295f634c3507a
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 31ddd059946537b3cf64de30861215f2
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: 3e1a78d741af5b546d7634330fd9d168
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: baf85914986afce1ffef88e1f5a056b3
- **2026-07-03T10:38:35**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: cad1bed66d4d2a67fccd5434f23695e7
