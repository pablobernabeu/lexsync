# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-03 14:25:00.16348
- Finished: 2026-10-03 14:25:23.516966

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 14:25:00.361959**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-03 14:25:03.781882**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 14:25:03.937619**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-03 14:25:04.600646**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03 14:25:04.714332**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-03 14:25:04.74941**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 14:25:04.773483**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-03 14:25:04.781128**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-03 14:25:06.441135**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-03 14:25:06.858163**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-10-03 14:25:07.167508**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-10-03 14:25:22.037513**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: 25ac249ec19404ec5212cb2c41cfc348
- **2026-10-03 14:25:22.107104**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 77125398dc3b65a41cd504d5005526fc
- **2026-10-03 14:25:22.240449**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 0408a54545c9e24a43530a75b7f7ec7d
- **2026-10-03 14:25:22.383255**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: 630290868a6a4a77aa25b6ca1b303f1d
- **2026-10-03 14:25:22.510839**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-03 14:25:22.613718**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 1d4555119c5865cce1ed2d8e06b6b1e9
- **2026-10-03 14:25:23.338731**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 81364e3e6431edfe289e37e2c34bc1e4
- **2026-10-03 14:25:23.40312**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 8ac8408d5fc18dfeb8ff9e92573bda4c
