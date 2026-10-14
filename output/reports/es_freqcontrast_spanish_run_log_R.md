# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-14 22:43:46.529338
- Finished: 2026-10-14 22:44:03.486946

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 22:43:46.651606**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-14 22:43:46.815805**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 22:43:46.894121**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-14 22:43:48.83723**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 22:43:49.255808**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-14 22:43:50.24482**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-14 22:43:51.030467**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-14 22:43:51.076403**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.000 (not shown equivalent)
- **2026-10-14 22:43:51.090638**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-14 22:43:51.12507**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-14 22:43:51.14986**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.001 (equivalent)
- **2026-10-14 22:43:51.227737**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.08, 0.61], TOST p = 0.169 (not shown equivalent)
- **2026-10-14 22:43:52.807853**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-14 22:43:53.085662**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-14 22:43:53.303388**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-14 22:44:01.922923**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: c2a06dd1cb6308c8db1c84f7f452b093
- **2026-10-14 22:44:01.975433**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: e13867db93fecccf01b36bff974ce686
- **2026-10-14 22:44:02.027672**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: d47a39252c7bb43a94943b42fac75199
- **2026-10-14 22:44:02.16306**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-14 22:44:02.214773**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-14 22:44:02.235677**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-14 22:44:03.307408**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 15e9c61cc68b5e9a5ad4aafff2dd033f
- **2026-10-14 22:44:03.369197**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 97ec31cf90c34f785c1f5d32032bb7ba
