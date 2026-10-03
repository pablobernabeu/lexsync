# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 03:41:43.880622
- Finished: 2026-10-09 03:41:49.854059

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 03:41:43.887987**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 03:41:45.576834**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 03:41:45.607045**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09 03:41:46.685419**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 03:41:46.752067**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 03:41:46.768043**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 03:41:46.775506**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 03:41:46.784428**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 03:41:46.896151**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-09 03:41:47.211645**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-10-09 03:41:47.287567**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 70c9db12a708fc06bf941740f3107481
- **2026-10-09 03:41:49.453713**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 10bac8b45fb858a2bc6ab572079f446c
- **2026-10-09 03:41:49.470229**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: b95c22b0f149eae2036eb64000c22376
- **2026-10-09 03:41:49.482195**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: a45625215256acadbf73fd3ab63ccba0
- **2026-10-09 03:41:49.499847**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 7c66adf7a1190b6ce863bc8d641af20d
- **2026-10-09 03:41:49.509977**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 03:41:49.520767**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: 779fb10b6d140096f8c3aa5ad6c0fe29
- **2026-10-09 03:41:49.801691**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 1c415d84b6b6b52997ccc4766ba2e801
- **2026-10-09 03:41:49.825514**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 25c5768a884d57305ad4a63d9a9c4c7a
