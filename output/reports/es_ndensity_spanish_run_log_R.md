# lexsync run log: es_ndensity

- Engine: R 4.6.0
- Started: 2026-07-03 10:37:02.384581
- Finished: 2026-07-03 10:37:03.734584

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 10:37:02.392004**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-03 10:37:02.893708**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 10:37:02.903337**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-03 10:37:03.320988**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-03 10:37:03.338236**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-03 10:37:03.343586**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-03 10:37:03.348122**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 10:37:03.35286**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 10:37:03.4019**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: e83015fd5f924a081e6f9b38c5b353ef
- **2026-07-03 10:37:03.423529**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-07-03 10:37:03.442949**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 22bd30d78a773f54309f14192f0f5b07
- **2026-07-03 10:37:03.575297**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: cb6952b0f8ca30cdbfbf85a98749fbe3
- **2026-07-03 10:37:03.587452**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 23ed39b25c54c03959c8084708921cf4
- **2026-07-03 10:37:03.602182**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: 1eaf6555a8ed9a387a842cb5d07acaf4
- **2026-07-03 10:37:03.709911**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 8d98c73465c1b7a6c8f6bc1c3678e7ef
- **2026-07-03 10:37:03.723339**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 96d02188b01574510982f512bc266892
