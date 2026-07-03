# lexsync run log: es_gender_repro

- Engine: R 4.6.0
- Started: 2026-07-03 10:37:01.780577
- Finished: 2026-07-03 10:37:02.357341

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 10:37:01.787156**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-07-03 10:37:01.953102**: lexicon loaded: 10185 words
    - words: 10185
- **2026-07-03 10:37:01.963972**: pool after filters: 9294 words
    - pool: 9294
- **2026-07-03 10:37:01.991913**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-07-03 10:37:02.012479**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-07-03 10:37:02.019298**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-07-03 10:37:02.026464**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-07-03 10:37:02.033052**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-07-03 10:37:02.06481**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: 2cdc3e69132c45f522d415092ca8873d
- **2026-07-03 10:37:02.086792**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-07-03 10:37:02.10882**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: ee84e946e3d532c0447f5e9dbd4b9adf
- **2026-07-03 10:37:02.202094**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 17a86ab092969e3a09eeb8c618b38db8
- **2026-07-03 10:37:02.21417**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: dfbc1ba1a041e115d4de5fd38e16486b
- **2026-07-03 10:37:02.227626**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: c049144db8d3d9ff31a62974763a54ee
- **2026-07-03 10:37:02.333344**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: 28ea823c02904f525cad3d202acbc6a2
- **2026-07-03 10:37:02.344597**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: 848bed84294e2717457973c05527a044
