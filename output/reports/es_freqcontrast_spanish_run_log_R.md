# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 09:53:13.411216
- Finished: 2026-10-09 09:53:15.458456

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:53:13.417922**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 09:53:14.120051**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:53:14.146151**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-09 09:53:14.41291**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 09:53:14.746524**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-09 09:53:14.753402**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:53:14.75949**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-09 09:53:14.76524**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 09:53:14.769576**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.16 [-0.42, 0.10], TOST p = 0.016 (equivalent)
- **2026-10-09 09:53:14.773877**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.08 [-0.18, 0.34], TOST p = 0.005 (equivalent)
- **2026-10-09 09:53:14.83154**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-09 09:53:14.848106**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: 6cf5b5443b50a10c486c3724f7b3da48
- **2026-10-09 09:53:14.865395**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 71061c6c3844d0a30717678fe82c7c9f
- **2026-10-09 09:53:15.206023**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-09 09:53:15.217001**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-09 09:53:15.226989**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 438e0d467a4a4f72d4d18925c53e511e
- **2026-10-09 09:53:15.242156**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: 630290868a6a4a77aa25b6ca1b303f1d
- **2026-10-09 09:53:15.250207**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 09:53:15.258646**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 1d4555119c5865cce1ed2d8e06b6b1e9
- **2026-10-09 09:53:15.435211**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 6a33b17d088e6ee892e5daf98242ef7c
- **2026-10-09 09:53:15.448277**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 2fd845355844468c9dddab0c08ea76a1
