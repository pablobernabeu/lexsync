# lexsync run log: es_ndensity

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:04.326179
- Finished: 2026-09-02 19:25:05.088762

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:04.326437**: loading lexicon 'corpora/derived/es.csv'
- **2026-09-02 19:25:04.556776**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:25:04.560516**: pool after filters: 4002 words
    - pool: 4002
- **2026-09-02 19:25:05.018887**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-09-02 19:25:05.030342**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-09-02 19:25:05.030629**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-09-02 19:25:05.030931**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:05.031117**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:05.042325**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-09-02 19:25:05.044727**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-09-02 19:25:05.046923**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 22bd30d78a773f54309f14192f0f5b07
- **2026-09-02 19:25:05.068939**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: f10d243175e5b7a05becd4aec0be8009
- **2026-09-02 19:25:05.069148**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: c31a6676121785fe10445abaaa379216
- **2026-09-02 19:25:05.069266**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: a1302c8abf7209e7cf4f2efaa170c6e4
- **2026-09-02 19:25:05.088342**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: db74baf6d2d9b22b615c40472300756e
- **2026-09-02 19:25:05.088542**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: a770310e6bd4a1a7dda07c628bb6e667
