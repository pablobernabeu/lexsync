# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-13 18:18:06.208749
- Finished: 2026-10-13 18:18:09.312942

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:18:06.221612**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13 18:18:06.2272**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:18:06.235408**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-13 18:18:06.78252**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-13 18:18:06.799605**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-13 18:18:07.005384**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-13 18:18:07.234907**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-13 18:18:07.251617**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-13 18:18:07.262058**: equivalence masculine vs feminine on 'n_density': d = 0.15 [-0.19, 0.49], TOST p = 0.043 (equivalent)
- **2026-10-13 18:18:07.276406**: equivalence masculine vs feminine on 'old20': d = -0.01 [-0.35, 0.32], TOST p = 0.010 (equivalent)
- **2026-10-13 18:18:07.288168**: equivalence masculine vs feminine on 'n_syllables': d = 0.13 [-0.21, 0.47], TOST p = 0.036 (equivalent)
- **2026-10-13 18:18:07.296479**: equivalence masculine vs feminine on 'bigram_freq': d = 0.23 [-0.10, 0.57], TOST p = 0.099 (not shown equivalent)
- **2026-10-13 18:18:07.41278**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: fb913d59159b8ff0f28e2500e37293cc
- **2026-10-13 18:18:07.47598**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 12
    - md5: 6a7606491f66d8e7edc9d01c9c68d60c
- **2026-10-13 18:18:07.59505**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 6
    - md5: 616802681caa63a66084ad9584dbc44c
- **2026-10-13 18:18:08.479499**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: d4cc3efc1bcd9586e9cdcb236e0be590
- **2026-10-13 18:18:08.501473**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: 323ed16d2fcc3f38fe1674013797dca8
- **2026-10-13 18:18:08.52042**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 7ecc281200a561998193ee32d018ef14
- **2026-10-13 18:18:08.55165**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output/experiments/es_gender_repro_spanish_psychopy.csv
    - rows: NA
    - md5: 0eb63319194528c0c179c3b153236aa8
- **2026-10-13 18:18:08.568604**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame.csv
    - rows: NA
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-13 18:18:08.601432**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame_text.csv
    - rows: NA
    - md5: 6e3f3663c8f25af2fba15f45cb5c3ccc
- **2026-10-13 18:18:09.198658**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: b6bab7878530ffc70ad262ce532081f3
- **2026-10-13 18:18:09.281912**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: d88b234afee65401295bde269d91e4ed
