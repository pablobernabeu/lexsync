# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-30T15:23:33
- Finished: 2026-07-30T15:23:34

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30T15:23:33**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-30T15:23:33**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30T15:23:33**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-30T15:23:34**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-30T15:23:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-30T15:23:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-30T15:23:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-07-30T15:23:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: 6d7cb383cfc3114c18f7f1499950ac35
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: af9e23c7d79b8059df29a709a4ad40e6
- **2026-07-30T15:23:34**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: 7b8f3afa9d02e4e7330290c32806d49a
