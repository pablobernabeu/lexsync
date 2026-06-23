# lexsync run log: es_ndensity

- Engine: R 4.6.0
- Started: 2026-06-23 10:19:00.282221
- Finished: 2026-06-23 10:19:01.782482

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:19:00.288887**: loading lexicon 'corpora/derived/es.csv'
- **2026-06-23 10:19:00.987328**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-23 10:19:00.999984**: pool after filters: 4002 words
    - pool: 4002
- **2026-06-23 10:19:01.374602**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-23 10:19:01.394749**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-23 10:19:01.402227**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-23 10:19:01.407463**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:19:01.413151**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:19:01.458464**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: e83015fd5f924a081e6f9b38c5b353ef
- **2026-06-23 10:19:01.479891**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-06-23 10:19:01.498956**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: f05264def44245723768e6f42f9361c1
- **2026-06-23 10:19:01.625867**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: cb6952b0f8ca30cdbfbf85a98749fbe3
- **2026-06-23 10:19:01.637526**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 23ed39b25c54c03959c8084708921cf4
- **2026-06-23 10:19:01.646788**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: 358ba05052798cc77355c65d5f2a665f
- **2026-06-23 10:19:01.758124**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 3edbd845ab432197fe72749a57596c47
- **2026-06-23 10:19:01.770406**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 3c497e8a9695a124f82f46ea51e31127
