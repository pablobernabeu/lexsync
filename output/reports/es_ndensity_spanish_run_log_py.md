# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-09T11:51:26
- Finished: 2026-10-09T11:51:28

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T11:51:26**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09T11:51:27**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T11:51:27**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09T11:51:28**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.0025 (equivalent)
- **2026-10-09T11:51:28**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.9971 (not shown equivalent)
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: a9407b2cd3eb015b7a9245b5584e98e7
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output\experiments\es_ndensity_spanish_psychopy.csv
    - rows: None
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame_text.csv
    - rows: None
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: 707931637cd98f704969f1fdc87b267e
- **2026-10-09T11:51:28**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: 50b0ec6156f881f005f534c40856259a
