# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-08T00:19:11
- Finished: 2026-06-08T00:19:11

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-08T00:19:11** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-08T00:19:11** -- lexicon loaded: 29999 words
    - words: 29999
- **2026-06-08T00:19:11** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-08T00:19:11** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.25, TOST p = 0.0607 (not shown equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.19, TOST p = 0.0269 (equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.22, TOST p = 1.0 (not shown equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.63, TOST p = 1.0 (not shown equivalent)
- **2026-06-08T00:19:11** -- wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: dd1116a39435888f49cb88ca44715365
- **2026-06-08T00:19:11** -- wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: 7b3ec4a48f2e73d4b99117c67bca0b30
- **2026-06-08T00:19:11** -- wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 04dd73bf68c6996586864faf12612f24
- **2026-06-08T00:19:11** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: a83459a46cac838bccc771f99fde5463
- **2026-06-08T00:19:11** -- wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: ef620a171ab3433402fb2cf75fdadcb3
