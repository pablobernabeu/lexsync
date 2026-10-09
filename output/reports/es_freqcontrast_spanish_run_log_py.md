# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-09T09:53:44
- Finished: 2026-10-09T09:53:45

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T09:53:44**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09T09:53:45**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T09:53:45**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-09T09:53:45**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.16 [-0.42, 0.10], TOST p = 0.0165 (equivalent)
- **2026-10-09T09:53:45**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.08 [-0.18, 0.34], TOST p = 0.0046 (equivalent)
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 12
    - md5: 6cf5b5443b50a10c486c3724f7b3da48
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 6
    - md5: 71061c6c3844d0a30717678fe82c7c9f
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish.html'
    - path: output\experiments\es_freqcontrast_spanish.html
    - rows: None
    - md5: 438e0d467a4a4f72d4d18925c53e511e
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.csv
    - rows: None
    - md5: 630290868a6a4a77aa25b6ca1b303f1d
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output\experiments\es_freqcontrast_spanish_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output\experiments\es_freqcontrast_spanish_opensesame_text.csv
    - rows: None
    - md5: 1d4555119c5865cce1ed2d8e06b6b1e9
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_datasheet_py.json'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.json
    - rows: None
    - md5: dd402541e7964f38eaed4d83b3b1430e
- **2026-10-09T09:53:45**: wrote 'es_freqcontrast_spanish_datasheet_py.md'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.md
    - rows: None
    - md5: 1d412b6480baf6a7ad3d6a4856da9875
