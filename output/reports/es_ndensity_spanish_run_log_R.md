# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:32.024563
- Finished: 2026-07-31 21:48:32.981908

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:32.028283**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-31 21:48:32.329988**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:32.336972**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-31 21:48:32.65537**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-31 21:48:32.671797**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-31 21:48:32.676581**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-31 21:48:32.679395**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:32.683362**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:32.729187**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-07-31 21:48:32.745771**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-07-31 21:48:32.760939**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 22bd30d78a773f54309f14192f0f5b07
- **2026-07-31 21:48:32.862259**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: d330eb5c72303ea33b91e95699543464
- **2026-07-31 21:48:32.871251**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: c31a6676121785fe10445abaaa379216
- **2026-07-31 21:48:32.880894**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: 6d1f21aa99f63ea669b37dffba15c71c
- **2026-07-31 21:48:32.966667**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 0107a7c0c7815ca5e35fc762b0ae44e2
- **2026-07-31 21:48:32.974358**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: b3aab70848c1ac934f6caf9fe82362a0
