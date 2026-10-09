# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 09:53:16.597142
- Finished: 2026-10-09 09:53:19.003954

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:53:16.601627**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 09:53:17.244431**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:53:17.253189**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-09 09:53:17.989411**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 09:53:18.282476**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 09:53:18.287417**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 09:53:18.291484**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:53:18.295693**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:53:18.300023**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.29 [0.03, 0.55], TOST p = 0.092 (not shown equivalent)
- **2026-10-09 09:53:18.303862**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 1.01 [0.73, 1.28], TOST p = 0.999 (not shown equivalent)
- **2026-10-09 09:53:18.349539**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-09 09:53:18.365118**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa347d4ef35bb876f93a59963acaed19
- **2026-10-09 09:53:18.380118**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 19edacbbc030167b7652d6c458d41bc4
- **2026-10-09 09:53:18.681902**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-09 09:53:18.691195**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-09 09:53:18.700708**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: ece6948da11e16ff999eefd71d73eb9a
- **2026-10-09 09:53:18.712853**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 7c66adf7a1190b6ce863bc8d641af20d
- **2026-10-09 09:53:18.720702**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 09:53:18.728604**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: 779fb10b6d140096f8c3aa5ad6c0fe29
- **2026-10-09 09:53:18.981979**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 0b2159d0d81550a06e0d66c116787d80
- **2026-10-09 09:53:18.994725**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: ee15cb0722b535ea6c9cc6081ed935cd
