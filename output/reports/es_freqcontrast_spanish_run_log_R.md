# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-13 18:18:00.959129
- Finished: 2026-10-13 18:18:06.148631

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:18:00.96723**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13 18:18:00.976095**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:18:00.982068**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-13 18:18:01.957511**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 18:18:01.986647**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-13 18:18:02.42894**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13 18:18:02.926004**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-13 18:18:03.087626**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 18:18:03.117478**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-13 18:18:03.123725**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-13 18:18:03.134639**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.001 (equivalent)
- **2026-10-13 18:18:03.144188**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.08, 0.61], TOST p = 0.169 (not shown equivalent)
- **2026-10-13 18:18:03.33814**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-13 18:18:03.412014**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-13 18:18:03.491905**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-13 18:18:05.680915**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: e1b1d9dbce2c66cf5aba192d2187b74c
- **2026-10-13 18:18:05.704893**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 490b236aa1916a12af83c6e6f39a7c73
- **2026-10-13 18:18:05.724572**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 358efbcde3d2fb04b67394a585d2aaa8
- **2026-10-13 18:18:05.74945**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-13 18:18:05.770844**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13 18:18:05.788596**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-13 18:18:06.102781**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 73159631d8d9a121e97c161c627c3500
- **2026-10-13 18:18:06.125563**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 97ec31cf90c34f785c1f5d32032bb7ba
