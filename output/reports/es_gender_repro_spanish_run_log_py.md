# lexsync run log: es_gender_repro

- Engine: Python 3.13.7
- Started: 2026-10-13T22:50:13
- Finished: 2026-10-13T22:50:15

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T22:50:13**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13T22:50:13**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13T22:50:13**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-13T22:50:14**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-13T22:50:14**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-13T22:50:14**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.0081 (equivalent)
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.0105 (equivalent)
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'n_density': d = 0.15 [-0.19, 0.49], TOST p = 0.0433 (equivalent)
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'old20': d = -0.01 [-0.35, 0.32], TOST p = 0.0098 (equivalent)
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'n_syllables': d = 0.13 [-0.21, 0.47], TOST p = 0.0361 (equivalent)
- **2026-10-13T22:50:14**: equivalence masculine vs feminine on 'bigram_freq': d = 0.23 [-0.10, 0.57], TOST p = 0.0987 (not shown equivalent)
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_stimuli_py.csv'
    - path: output\stimuli\es_gender_repro_spanish_stimuli_py.csv
    - rows: 96
    - md5: fb913d59159b8ff0f28e2500e37293cc
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_descriptives_py.csv'
    - path: output\reports\es_gender_repro_spanish_descriptives_py.csv
    - rows: 12
    - md5: 6a7606491f66d8e7edc9d01c9c68d60c
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_comparisons_py.csv'
    - path: output\reports\es_gender_repro_spanish_comparisons_py.csv
    - rows: 6
    - md5: 616802681caa63a66084ad9584dbc44c
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output\experiments\es_gender_repro_spanish_psychopy.py
    - rows: None
    - md5: 34d0b69da2902f1bad7b05da02b41611
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish.osexp'
    - path: output\experiments\es_gender_repro_spanish.osexp
    - rows: None
    - md5: 4f68010226d44bcbe08ed1d9293f2715
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish.html'
    - path: output\experiments\es_gender_repro_spanish.html
    - rows: None
    - md5: 7ecc281200a561998193ee32d018ef14
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output\experiments\es_gender_repro_spanish_psychopy.csv
    - rows: None
    - md5: 0eb63319194528c0c179c3b153236aa8
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output\experiments\es_gender_repro_spanish_opensesame.csv
    - rows: None
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output\experiments\es_gender_repro_spanish_opensesame_text.csv
    - rows: None
    - md5: 6e3f3663c8f25af2fba15f45cb5c3ccc
- **2026-10-13T22:50:14**: wrote 'es_gender_repro_spanish_datasheet_py.json'
    - path: output\reports\es_gender_repro_spanish_datasheet_py.json
    - rows: None
    - md5: c267bff85d80a34ea5c4c0dc86b11880
- **2026-10-13T22:50:15**: wrote 'es_gender_repro_spanish_datasheet_py.md'
    - path: output\reports\es_gender_repro_spanish_datasheet_py.md
    - rows: None
    - md5: 6efbad244b38cd3dbd3cd6694173faef
