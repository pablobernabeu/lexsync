# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-13T23:55:07
- Finished: 2026-06-13T23:55:09

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13T23:55:07** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-13T23:55:08** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13T23:55:08** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-13T23:55:08** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13T23:55:09** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-06-13T23:55:09** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-06-13T23:55:09** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:09** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: 5d60acdf7e9b5593bfc3d6b180659a28
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: d797c20f2b17b2271741a28db09ba76a
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 3ce43f2e73c39a9bab95b1313b78cb1d
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 0101bfb866cceb95d53ff128448e76fd
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: 302cdcbd39cf74931699cfd33d4d784d
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: 65d08f391bb0a73c4df6a9bdfe6f164a
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: 0265e3fdd7f59fc8bd5c1207bcea0478
- **2026-06-13T23:55:09** -- wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: 9ee507839eea6d166b280dac80e7cc41
