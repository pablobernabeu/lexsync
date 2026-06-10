# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-10T09:34:24
- Finished: 2026-06-10T09:34:25

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-10T09:34:24** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-10T09:34:24** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10T09:34:24** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-10T09:34:25** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-10T09:34:25** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00, TOST p = 0.0009 (equivalent)
- **2026-06-10T09:34:25** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00, TOST p = 0.0009 (equivalent)
- **2026-06-10T09:34:25** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13, TOST p = 1.0 (not shown equivalent)
- **2026-06-10T09:34:25** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42, TOST p = 1.0 (not shown equivalent)
- **2026-06-10T09:34:25** -- wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: e629acd14fa20381f57222aa4400596e
- **2026-06-10T09:34:25** -- wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: d797c20f2b17b2271741a28db09ba76a
- **2026-06-10T09:34:25** -- wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 7093a053198d4ca1b497d281c0b82a5f
- **2026-06-10T09:34:25** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: a83459a46cac838bccc771f99fde5463
- **2026-06-10T09:34:25** -- wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: ef620a171ab3433402fb2cf75fdadcb3
