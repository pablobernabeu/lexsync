# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-13 18:21:19.32543
- Finished: 2026-06-13 18:21:19.945582

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 18:21:19.325856** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-13 18:21:19.488814** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 18:21:19.493608** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-13 18:21:19.778515** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13 18:21:19.788833** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:19.789132** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:19.789334** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:19.789515** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:19.825475** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 7394777ae5e0705cf2499a226e633451
- **2026-06-13 18:21:19.837258** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-06-13 18:21:19.849533** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: f05264def44245723768e6f42f9361c1
- **2026-06-13 18:21:19.931937** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: ac63a9c00186199963e2007eb134507d
- **2026-06-13 18:21:19.937367** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 23ed39b25c54c03959c8084708921cf4
