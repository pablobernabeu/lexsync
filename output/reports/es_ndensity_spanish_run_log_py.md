# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-07T13:33:57
- Finished: 2026-06-07T13:33:57

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-07T13:33:57** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07T13:33:57** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07T13:33:57** -- pool after filters: 3934 words
    - pool: 3934
- **2026-06-07T13:33:57** -- matched 48 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-07T13:33:57** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.06, TOST p = 0.0686 (not shown equivalent)
- **2026-06-07T13:33:57** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.12, TOST p = 0.1001 (not shown equivalent)
- **2026-06-07T13:33:57** -- wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 48
    - md5: 75f3bb3ea4aad70f140a27954773a604
- **2026-06-07T13:33:57** -- wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 4
    - md5: 6e69a782cd9be1c7a8b273edc2c59eee
- **2026-06-07T13:33:57** -- wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 2
    - md5: cb10684325469e1af178e0923bb5bfeb
- **2026-06-07T13:33:57** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: a83459a46cac838bccc771f99fde5463
- **2026-06-07T13:33:57** -- wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: bf92c6d68f3fc94289816de61b635ce8
