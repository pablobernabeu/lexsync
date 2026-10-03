# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-03 09:50:39.740226
- Finished: 2026-10-03 09:51:06.300831

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 09:50:39.797388**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-03 09:50:43.114147**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 09:50:43.245464**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-03 09:50:45.573157**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-03 09:50:45.730313**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 09:50:45.812021**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 09:50:45.857042**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 09:50:45.926679**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 09:50:48.181689**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-03 09:50:49.264959**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-10-03 09:50:49.554212**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 70c9db12a708fc06bf941740f3107481
- **2026-10-03 09:51:03.544366**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: d330eb5c72303ea33b91e95699543464
- **2026-10-03 09:51:04.022016**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: b95c22b0f149eae2036eb64000c22376
- **2026-10-03 09:51:04.155536**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: e8e07c918578b4c676700dc457b00e8b
- **2026-10-03 09:51:06.020239**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 7e52267bb227918f3f6474e8fd365d7e
- **2026-10-03 09:51:06.119251**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: f3818a3ff3717a1f3c90f23ad56551b6
