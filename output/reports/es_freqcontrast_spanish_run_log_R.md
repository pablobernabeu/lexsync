# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-13 11:12:16.709095
- Finished: 2026-10-13 11:12:22.685395

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:12:16.717224**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-13 11:12:18.196665**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 11:12:18.234104**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-13 11:12:18.946437**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13 11:12:19.684035**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-13 11:12:19.697215**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 11:12:19.708659**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-13 11:12:19.720809**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-13 11:12:19.730759**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.001 (equivalent)
- **2026-10-13 11:12:19.74256**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.08, 0.61], TOST p = 0.169 (not shown equivalent)
- **2026-10-13 11:12:19.96276**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-13 11:12:20.025173**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-13 11:12:20.085792**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-13 11:12:21.871697**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-13 11:12:21.908765**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-13 11:12:21.947986**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: b7eaa56fe32f20601b1eda0717cc032e
- **2026-10-13 11:12:21.982139**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-13 11:12:22.021118**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13 11:12:22.053913**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-13 11:12:22.599313**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 6c08d9589d8e7c7fa028501b4d98fff7
- **2026-10-13 11:12:22.652424**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 97ec31cf90c34f785c1f5d32032bb7ba
