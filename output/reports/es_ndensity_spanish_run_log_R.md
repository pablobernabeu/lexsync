# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-13 22:14:47.983906
- Finished: 2026-06-13 22:14:49.42699

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:14:47.984361** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-13 22:14:48.563936** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:14:48.571211** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-13 22:14:49.111579** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13 22:14:49.124655** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:49.125022** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:49.125318** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:49.125573** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:49.163911** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: e83015fd5f924a081e6f9b38c5b353ef
- **2026-06-13 22:14:49.178933** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-06-13 22:14:49.196405** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: f05264def44245723768e6f42f9361c1
- **2026-06-13 22:14:49.309713** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: ac63a9c00186199963e2007eb134507d
- **2026-06-13 22:14:49.314811** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 23ed39b25c54c03959c8084708921cf4
- **2026-06-13 22:14:49.318997** -- wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: 358ba05052798cc77355c65d5f2a665f
- **2026-06-13 22:14:49.415722** -- wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: d4401d31a83f85e73775f95e04b3c636
- **2026-06-13 22:14:49.421103** -- wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 5610127f1f6f1856eec3abdf27059bc9
