# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-07-30 15:21:03.038868
- Finished: 2026-07-30 15:21:05.330772

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:21:03.044758**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-30 15:21:03.867412**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30 15:21:03.905201**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-30 15:21:04.674615**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-30 15:21:04.723837**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-30 15:21:04.748507**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-30 15:21:04.769688**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:21:04.779522**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:21:04.860175**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-07-30 15:21:04.883159**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-07-30 15:21:04.907359**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 22bd30d78a773f54309f14192f0f5b07
- **2026-07-30 15:21:05.114858**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: d330eb5c72303ea33b91e95699543464
- **2026-07-30 15:21:05.134277**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: c31a6676121785fe10445abaaa379216
- **2026-07-30 15:21:05.149308**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: 6d1f21aa99f63ea669b37dffba15c71c
- **2026-07-30 15:21:05.305519**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 5c74980bfee5ddaa70491a3b435a8a61
- **2026-07-30 15:21:05.320015**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: b3aab70848c1ac934f6caf9fe82362a0
