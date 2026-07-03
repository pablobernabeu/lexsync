# lexsync run log: es_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-03 10:37:00.760735
- Finished: 2026-07-03 10:37:01.752193

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 10:37:00.764797**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-03 10:37:01.222667**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 10:37:01.233537**: pool after filters: 7172 words
    - pool: 7172
- **2026-07-03 10:37:01.374488**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-03 10:37:01.391074**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-07-03 10:37:01.396015**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 10:37:01.3998**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-07-03 10:37:01.404074**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-03 10:37:01.443841**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: d143dcfc416f330eee0f4eab44b3b212
- **2026-07-03 10:37:01.462512**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-07-03 10:37:01.481231**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: b2dd610e72f3335fc3c6c01ff1bfa950
- **2026-07-03 10:37:01.597492**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: a02d2d6ff1b4f5f18f59dbea69c039a4
- **2026-07-03 10:37:01.61151**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: f89b9471ee7659ef78f20606c0526071
- **2026-07-03 10:37:01.623787**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 3274154276f3c731e7c1965299702598
- **2026-07-03 10:37:01.725004**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 8dad0565aa790c91247f2981beda76a8
- **2026-07-03 10:37:01.739047**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 5e14a70852e09f44656e434c17a2c542
