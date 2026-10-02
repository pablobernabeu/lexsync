# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 05:58:28.167402
- Finished: 2026-10-09 05:58:31.257601

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:58:28.175315**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-09 05:58:29.261785**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 05:58:29.280561**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-09 05:58:29.702486**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 05:58:29.753459**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-09 05:58:29.761369**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:58:29.767446**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-09 05:58:29.773616**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 05:58:29.924829**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-09 05:58:29.955927**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-10-09 05:58:29.97705**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-10-09 05:58:30.851885**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff38f1bf04fab14a443529573a88d1f2
- **2026-10-09 05:58:30.898361**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 19deb3af454ce0433f85da463e87ea10
- **2026-10-09 05:58:30.918223**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 438e0d467a4a4f72d4d18925c53e511e
- **2026-10-09 05:58:30.944486**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: 630290868a6a4a77aa25b6ca1b303f1d
- **2026-10-09 05:58:30.959814**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 05:58:30.974217**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 1d4555119c5865cce1ed2d8e06b6b1e9
- **2026-10-09 05:58:31.226588**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: bd226ade5c14fb91c718f28172d160c7
- **2026-10-09 05:58:31.241611**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 9f8419536b8ee16b17340d091799333e
