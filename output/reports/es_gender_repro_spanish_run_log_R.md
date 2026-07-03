# lexsync run log: es_gender_repro

- Engine: R 4.6.0
- Started: 2026-07-03 00:09:01.988522
- Finished: 2026-07-03 00:09:02.363612

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 00:09:01.993787**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-07-03 00:09:02.10425**: lexicon loaded: 10185 words
    - words: 10185
- **2026-07-03 00:09:02.110382**: pool after filters: 9294 words
    - pool: 9294
- **2026-07-03 00:09:02.122273**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-07-03 00:09:02.137485**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-07-03 00:09:02.142463**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-07-03 00:09:02.146668**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-07-03 00:09:02.150819**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-07-03 00:09:02.171989**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: 2cdc3e69132c45f522d415092ca8873d
- **2026-07-03 00:09:02.187012**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-07-03 00:09:02.199041**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: 02eb506d5f1c59856d9eb8d680d511a4
- **2026-07-03 00:09:02.261579**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 17a86ab092969e3a09eeb8c618b38db8
- **2026-07-03 00:09:02.271014**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: dfbc1ba1a041e115d4de5fd38e16486b
- **2026-07-03 00:09:02.279562**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: c049144db8d3d9ff31a62974763a54ee
- **2026-07-03 00:09:02.345067**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: b7e621caf41a200f9e2d09d883e06527
- **2026-07-03 00:09:02.354901**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: 1e88f5bade1adfce078f11474603423d
