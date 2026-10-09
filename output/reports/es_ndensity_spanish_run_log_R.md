# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 07:51:08.038006
- Finished: 2026-10-09 07:51:10.207799

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:51:08.042768**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 07:51:08.644381**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:51:08.654827**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09 07:51:09.295538**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 07:51:09.570773**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:51:09.575935**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:51:09.581886**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:51:09.587654**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:51:09.594019**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.29 [0.03, 0.55], TOST p = 0.092 (not shown equivalent)
- **2026-10-09 07:51:09.599627**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 1.01 [0.73, 1.28], TOST p = 0.999 (not shown equivalent)
- **2026-10-09 07:51:09.644775**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-09 07:51:09.665247**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa347d4ef35bb876f93a59963acaed19
- **2026-10-09 07:51:09.682102**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 19edacbbc030167b7652d6c458d41bc4
- **2026-10-09 07:51:10.001004**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-09 07:51:10.01013**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-09 07:51:10.019393**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: ece6948da11e16ff999eefd71d73eb9a
- **2026-10-09 07:51:10.030888**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 7c66adf7a1190b6ce863bc8d641af20d
- **2026-10-09 07:51:10.037142**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 07:51:10.043974**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: 779fb10b6d140096f8c3aa5ad6c0fe29
- **2026-10-09 07:51:10.187154**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 75a709a4c290630ae9e4253592c60d2a
- **2026-10-09 07:51:10.199002**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: e550c993a6f4690b488d8f5f31f0229a
