# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 07:16:26.280914
- Finished: 2026-10-09 07:16:28.019866

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:16:26.285762**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 07:16:27.003087**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:16:27.031594**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-09 07:16:27.291038**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 07:16:27.319873**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-09 07:16:27.324283**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:16:27.329062**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-09 07:16:27.332914**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 07:16:27.381362**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-09 07:16:27.397711**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-10-09 07:16:27.414082**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-10-09 07:16:27.776516**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-09 07:16:27.787216**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-09 07:16:27.796166**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 438e0d467a4a4f72d4d18925c53e511e
- **2026-10-09 07:16:27.809256**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: 630290868a6a4a77aa25b6ca1b303f1d
- **2026-10-09 07:16:27.818028**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 07:16:27.826182**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 1d4555119c5865cce1ed2d8e06b6b1e9
- **2026-10-09 07:16:27.999697**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: f45d94613bca91274fd7cb1f53b56d3d
- **2026-10-09 07:16:28.010572**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 9f8419536b8ee16b17340d091799333e
