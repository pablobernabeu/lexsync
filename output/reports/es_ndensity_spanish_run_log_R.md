# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-13 11:12:29.764103
- Finished: 2026-10-13 11:12:43.810172

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:12:29.783195**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-13 11:12:34.427802**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 11:12:34.620189**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-13 11:12:39.494607**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-13 11:12:40.637962**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-13 11:12:40.654259**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-13 11:12:40.676216**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 11:12:40.686694**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 11:12:40.696652**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-13 11:12:40.712672**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.997 (not shown equivalent)
- **2026-10-13 11:12:41.023354**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-10-13 11:12:41.10898**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-10-13 11:12:41.170046**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-10-13 11:12:43.107442**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 8368664e29077204584521967ad227e8
- **2026-10-13 11:12:43.136003**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5519f4520615820332b38a942cb91ae3
- **2026-10-13 11:12:43.161409**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: a9407b2cd3eb015b7a9245b5584e98e7
- **2026-10-13 11:12:43.184336**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-10-13 11:12:43.202987**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-13 11:12:43.221675**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-10-13 11:12:43.717505**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: a8aa1b9821a34c43c6d2db0667408535
- **2026-10-13 11:12:43.762017**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 17e92edfab098ad5430ffde259fc981f
