# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-06T10:27:46
- Finished: 2026-07-06T10:27:46

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06T10:27:46**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-06T10:27:46**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-06T10:27:46**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-06T10:27:46**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-06T10:27:46**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-06T10:27:46**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-06T10:27:46**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.0 (not shown equivalent)
- **2026-07-06T10:27:46**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.0 (not shown equivalent)
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: 5d60acdf7e9b5593bfc3d6b180659a28
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: d797c20f2b17b2271741a28db09ba76a
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 876473de3640908cf2c1c22a691229e6
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 782ae8cff904875836e322ed55a554b7
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: 302cdcbd39cf74931699cfd33d4d784d
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: f9f2ebcd39ea47c8fb08da1d44f61bf8
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: 8a65fd71cf527c855371a911c314fce0
- **2026-07-06T10:27:46**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: f360050e50fe1289212985d75d223f35
