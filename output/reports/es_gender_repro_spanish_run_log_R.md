# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-09 07:16:28.042145
- Finished: 2026-10-09 07:16:28.999748

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:16:28.045753**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-09 07:16:28.324576**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-09 07:16:28.332104**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-09 07:16:28.409498**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-09 07:16:28.445454**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-09 07:16:28.45004**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-09 07:16:28.45394**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-10-09 07:16:28.45771**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-10-09 07:16:28.491591**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: b415e828f6a2dcff9ef0563c8cdc8cb0
- **2026-10-09 07:16:28.507512**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 8
    - md5: be7ae753395f531c36d15adb38e8057f
- **2026-10-09 07:16:28.523422**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 4
    - md5: d88c76a973db00923cedb4b340978bc7
- **2026-10-09 07:16:28.762408**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: bbf6d33f78dd86bb674cd4a56c83b523
- **2026-10-09 07:16:28.772175**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: 27783330583f1bce440e91e202377908
- **2026-10-09 07:16:28.781244**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 5b7525052e5edf0c002ed324b14703a3
- **2026-10-09 07:16:28.795467**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output/experiments/es_gender_repro_spanish_psychopy.csv
    - rows: NA
    - md5: cd45866303f43f56da2d18ffd8d1cab9
- **2026-10-09 07:16:28.80354**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame.csv
    - rows: NA
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-09 07:16:28.811536**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame_text.csv
    - rows: NA
    - md5: 0b036507adb99c2f18095ebcfb384c4b
- **2026-10-09 07:16:28.978306**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: 3e864c9c8bb018936a9b1c18531bfc70
- **2026-10-09 07:16:28.989536**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: c5fadaf85687e0c309aa951df5d3b12e
