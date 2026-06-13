# lexsync run log: es_gender_repro

- Engine: R 4.5.1
- Started: 2026-06-13 23:47:55.106476
- Finished: 2026-06-13 23:47:58.315131

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 23:47:55.132544** -- loading lexicon 'corpora/derived/es_gender.csv'
- **2026-06-13 23:47:57.360573** -- lexicon loaded: 10185 words
    - words: 10185
- **2026-06-13 23:47:57.376502** -- pool after filters: 9294 words
    - pool: 9294
- **2026-06-13 23:47:57.468771** -- matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-06-13 23:47:57.585464** -- equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-06-13 23:47:57.585744** -- equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-06-13 23:47:57.585931** -- equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-06-13 23:47:57.586201** -- equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-06-13 23:47:57.628989** -- wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: 2cdc3e69132c45f522d415092ca8873d
- **2026-06-13 23:47:57.647338** -- wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-06-13 23:47:57.660324** -- wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: 02eb506d5f1c59856d9eb8d680d511a4
- **2026-06-13 23:47:58.012091** -- wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 246394b6683d8ae0145908c036e3f0fa
- **2026-06-13 23:47:58.018681** -- wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: dfbc1ba1a041e115d4de5fd38e16486b
- **2026-06-13 23:47:58.026496** -- wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 27594fcc3f12e76e982bcb94b4980bb2
- **2026-06-13 23:47:58.277474** -- wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: ac11bb88c9747f31574ae027c016d689
- **2026-06-13 23:47:58.282564** -- wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: 7933263fca2d0c4bad350976cbcf0d0d
