# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-03 09:50:28.252432
- Finished: 2026-10-03 09:50:39.498722

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 09:50:28.321287**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-03 09:50:29.668752**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-03 09:50:29.695165**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-03 09:50:29.976554**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-03 09:50:30.061078**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-03 09:50:30.096354**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-03 09:50:30.110899**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-10-03 09:50:30.130179**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-10-03 09:50:30.568811**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: b415e828f6a2dcff9ef0563c8cdc8cb0
- **2026-10-03 09:50:30.699387**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-10-03 09:50:30.864069**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: d88c76a973db00923cedb4b340978bc7
- **2026-10-03 09:50:38.3529**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 3d67e943357bbcaa45fb551904a24427
- **2026-10-03 09:50:38.450422**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: c574ab6331d7c6ddfd4fae05a62cb9a8
- **2026-10-03 09:50:38.599015**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 4cc7e83a7c772e0f32e078c6efb80a42
- **2026-10-03 09:50:39.260813**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: 7ef958e03e1697329571b8077742e157
- **2026-10-03 09:50:39.38729**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: 7dadb6f34efabe108b6e17cd5c2ca514
