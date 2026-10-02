# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 07:16:29.026105
- Finished: 2026-10-09 07:16:31.514873

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:16:29.030841**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 07:16:29.759045**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:16:29.768308**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09 07:16:30.441629**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 07:16:30.475024**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:16:30.480634**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:16:30.485229**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:16:30.489355**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:16:30.534716**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-09 07:16:30.548705**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-10-09 07:16:30.566234**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 70c9db12a708fc06bf941740f3107481
- **2026-10-09 07:16:30.911197**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-09 07:16:30.922421**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-09 07:16:30.932252**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: ece6948da11e16ff999eefd71d73eb9a
- **2026-10-09 07:16:30.947159**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 7c66adf7a1190b6ce863bc8d641af20d
- **2026-10-09 07:16:30.955718**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 07:16:30.963906**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: 779fb10b6d140096f8c3aa5ad6c0fe29
- **2026-10-09 07:16:31.492533**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 92c6e6a207bb8ed9394bed7cef7de078
- **2026-10-09 07:16:31.504293**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 45c20cbd087efc8ef1724f322672708e
