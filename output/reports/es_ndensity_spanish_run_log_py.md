# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-09T07:17:03
- Finished: 2026-10-09T07:17:04

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T07:17:03**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09T07:17:03**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T07:17:03**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09T07:17:04**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09T07:17:04**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T07:17:04**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T07:17:04**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T07:17:04**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 70c9db12a708fc06bf941740f3107481
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: ece6948da11e16ff999eefd71d73eb9a
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output\experiments\es_ndensity_spanish_psychopy.csv
    - rows: None
    - md5: 7c66adf7a1190b6ce863bc8d641af20d
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame_text.csv
    - rows: None
    - md5: 779fb10b6d140096f8c3aa5ad6c0fe29
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: 79f67a693569cb55bcec5bee14d3ff80
- **2026-10-09T07:17:04**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: 785178a08db4f6951eaa9b9ea492b49f
