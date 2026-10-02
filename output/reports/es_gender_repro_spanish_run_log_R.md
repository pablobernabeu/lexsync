# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-02 16:47:19.628426
- Finished: 2026-10-02 16:47:40.548771

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:47:19.727968**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-02 16:47:20.704905**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-02 16:47:20.976819**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-02 16:47:21.25747**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-02 16:47:21.403811**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-02 16:47:21.758546**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-02 16:47:21.779036**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-10-02 16:47:21.857755**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-10-02 16:47:23.163138**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: b415e828f6a2dcff9ef0563c8cdc8cb0
- **2026-10-02 16:47:24.315973**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-10-02 16:47:25.508095**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: d88c76a973db00923cedb4b340978bc7
- **2026-10-02 16:47:37.978471**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 3d67e943357bbcaa45fb551904a24427
- **2026-10-02 16:47:38.109127**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: c574ab6331d7c6ddfd4fae05a62cb9a8
- **2026-10-02 16:47:38.192999**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 4cc7e83a7c772e0f32e078c6efb80a42
- **2026-10-02 16:47:39.845112**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: a9d1939f1c536a4b2be9293b61e68a80
- **2026-10-02 16:47:40.04402**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: a2f7b38d22fb245cedd459f29aad7fd4
