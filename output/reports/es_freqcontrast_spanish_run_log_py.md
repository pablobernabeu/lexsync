# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-13T14:33:45
- Finished: 2026-10-13T14:33:50

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T14:33:45**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-13T14:33:47**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T14:33:47**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-13T14:33:48**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.0 (not shown equivalent)
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.0014 (equivalent)
- **2026-10-13T14:33:48**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.09, 0.61], TOST p = 0.1692 (not shown equivalent)
- **2026-10-13T14:33:48**: wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-13T14:33:48**: wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish.html'
    - path: output\experiments\es_freqcontrast_spanish.html
    - rows: None
    - md5: b7eaa56fe32f20601b1eda0717cc032e
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.csv
    - rows: None
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output\experiments\es_freqcontrast_spanish_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13T14:33:49**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output\experiments\es_freqcontrast_spanish_opensesame_text.csv
    - rows: None
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-13T14:33:50**: wrote 'es_freqcontrast_spanish_datasheet_py.json'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.json
    - rows: None
    - md5: 06289974b93b16aef4b846d8015f5732
- **2026-10-13T14:33:50**: wrote 'es_freqcontrast_spanish_datasheet_py.md'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.md
    - rows: None
    - md5: 080eed74fc51c1a51c822b8ed164c8ab
