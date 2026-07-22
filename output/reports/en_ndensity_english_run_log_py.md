# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-23T00:27:44
- Finished: 2026-07-23T00:27:45

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-23T00:27:44**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-23T00:27:44**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-23T00:27:44**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-23T00:27:45**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-23T00:27:45**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-23T00:27:45**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-23T00:27:45**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-07-23T00:27:45**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 493eec358180c6baead5f2153a90408c
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: f3bd8cddc47162cab263b21e5eeddb9c
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 68ec43e5757f427f79d80bf4a1475cd9
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 1b2335442a591af3fb649c384dc85bb3
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: da5fb6bf30a7a519623937134a6e89e2
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: 06e6c9a754ca792a992ad05a7ec394df
- **2026-07-23T00:27:45**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: 65c4c43874cc29e66899f14901c37ddc
