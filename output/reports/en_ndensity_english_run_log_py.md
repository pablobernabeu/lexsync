# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-15T10:11:52
- Finished: 2026-07-15T10:11:53

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15T10:11:52**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15T10:11:52**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15T10:11:52**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-15T10:11:53**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-15T10:11:53**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-15T10:11:53**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-15T10:11:53**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-07-15T10:11:53**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: c917860561f7c765fe6d10483e99790b
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: f3bd8cddc47162cab263b21e5eeddb9c
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 68ec43e5757f427f79d80bf4a1475cd9
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: d54af56ff89843712b990f0ad0ca7d80
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: 8515e368444670a7923a1b676740acb2
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: e76fbd0419448242e0c064b81135fd1b
- **2026-07-15T10:11:53**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: cad1bed66d4d2a67fccd5434f23695e7
