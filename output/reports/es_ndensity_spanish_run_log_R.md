# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-10 09:31:51.280318
- Finished: 2026-06-10 09:31:52.145421

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-10 09:31:51.281004** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-10 09:31:51.415329** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 09:31:51.421664** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-10 09:31:51.907734** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-10 09:31:51.921701** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:51.922055** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:51.922306** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:51.922565** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:51.978077** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 7394777ae5e0705cf2499a226e633451
- **2026-06-10 09:31:51.995061** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-06-10 09:31:52.011482** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 501688eb2e02e16d387e0738e5c1eaa8
- **2026-06-10 09:31:52.1333** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 482de3cb5213508f64a112309b07a495
- **2026-06-10 09:31:52.139294** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5102b68feebf7692d9fc1bbe2097e5d5
