# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-15 03:29:40.696271
- Finished: 2026-10-15 03:29:43.703131

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 03:29:40.708882**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15 03:29:40.716505**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15 03:29:40.725408**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-15 03:29:41.742355**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 03:29:41.773047**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-15 03:29:42.383967**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-15 03:29:42.894045**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-15 03:29:42.899279**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.39 [4.83, 5.95], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 03:29:42.905861**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-15 03:29:42.910904**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-15 03:29:42.91651**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.24, 0.28], TOST p = 0.001 (equivalent)
- **2026-10-15 03:29:42.921807**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.35 [0.08, 0.61], TOST p = 0.169 (not shown equivalent)
- **2026-10-15 03:29:42.982799**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 817324e156de4da0ea8e4a8518c13197
- **2026-10-15 03:29:43.005832**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 12
    - md5: fa8ad452d8561f61cf719be63ac70a0e
- **2026-10-15 03:29:43.026875**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 6
    - md5: 7b2f2ef77c780892ce33c363d380d6fc
- **2026-10-15 03:29:43.409536**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: f33b0cf3fcf9e81f548c94d27efb6770
- **2026-10-15 03:29:43.420567**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: e13867db93fecccf01b36bff974ce686
- **2026-10-15 03:29:43.431**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 81e37e734412182ded6676b0df8a3306
- **2026-10-15 03:29:43.446132**: wrote 'es_freqcontrast_spanish_psychopy.csv'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.csv
    - rows: NA
    - md5: b314fe13029b2aa8fc712238fbf0c65a
- **2026-10-15 03:29:43.455877**: wrote 'es_freqcontrast_spanish_opensesame.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-15 03:29:43.466678**: wrote 'es_freqcontrast_spanish_opensesame_text.csv'
    - path: output/experiments/es_freqcontrast_spanish_opensesame_text.csv
    - rows: NA
    - md5: 29a387c11a553fc5bc875d7cbe0b9f29
- **2026-10-15 03:29:43.674351**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: ca86774d9026e6185ecad01b58f4f3da
- **2026-10-15 03:29:43.693285**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 97ec31cf90c34f785c1f5d32032bb7ba
