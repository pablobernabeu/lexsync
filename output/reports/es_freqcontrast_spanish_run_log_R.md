# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-15 04:45:38.025208
- Finished: 2026-10-15 04:45:40.564518

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 04:45:38.03099**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15 04:45:38.035947**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15 04:45:38.041925**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-15 04:45:38.750137**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 04:45:38.769192**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-15 04:45:39.234087**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-15 04:45:39.667116**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-15 04:45:39.677015**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 04:45:39.688164**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-15 04:45:39.695597**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-15 04:45:39.704033**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.001 (equivalent)
- **2026-10-15 04:45:39.716059**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.08, 0.61], TOST p = 0.169 (not shown equivalent)
- **2026-10-15 04:45:39.775052**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-15 04:45:39.802467**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-15 04:45:39.827412**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-15 04:45:40.232344**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: f33b0cf3fcf9e81f548c94d27efb6770
- **2026-10-15 04:45:40.244404**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: e13867db93fecccf01b36bff974ce686
- **2026-10-15 04:45:40.254198**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 81e37e734412182ded6676b0df8a3306
- **2026-10-15 04:45:40.271538**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-15 04:45:40.284108**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-15 04:45:40.301623**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-15 04:45:40.541127**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 2769c7de7fa6a318990086e919014b9f
- **2026-10-15 04:45:40.552808**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 97ec31cf90c34f785c1f5d32032bb7ba
