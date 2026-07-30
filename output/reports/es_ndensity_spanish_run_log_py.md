# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-30T15:23:34
- Finished: 2026-07-30T15:23:35

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30T15:23:34**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-30T15:23:35**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30T15:23:35**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-30T15:23:35**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-30T15:23:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-30T15:23:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-30T15:23:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.0 (not shown equivalent)
- **2026-07-30T15:23:35**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.0 (not shown equivalent)
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: 22bd30d78a773f54309f14192f0f5b07
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: d330eb5c72303ea33b91e95699543464
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: c31a6676121785fe10445abaaa379216
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: 6d1f21aa99f63ea669b37dffba15c71c
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: c8cd75021cee0d91ca209d096c4dd976
- **2026-07-30T15:23:35**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: f23cb7f6bb3e12757d448d0a5dcdb6b9
