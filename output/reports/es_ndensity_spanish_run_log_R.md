# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-08 00:19:03.043067
- Finished: 2026-06-08 00:19:03.231706

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-08 00:19:03.043354** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-08 00:19:03.091509** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-08 00:19:03.094198** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-08 00:19:03.113408** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-08 00:19:03.11919** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.25, TOST p = 0.061 (not shown equivalent)
- **2026-06-08 00:19:03.119376** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.19, TOST p = 0.027 (equivalent)
- **2026-06-08 00:19:03.119541** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.22, TOST p = 1.000 (not shown equivalent)
- **2026-06-08 00:19:03.119688** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.63, TOST p = 1.000 (not shown equivalent)
- **2026-06-08 00:19:03.146584** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: b10f11fb440dfe22218e05f3856780dc
- **2026-06-08 00:19:03.156381** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 345664a5d93f3231587d1b0d867fc144
- **2026-06-08 00:19:03.164273** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 1f7219598e6561f3db655d6849cfbdc3
- **2026-06-08 00:19:03.222843** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 482de3cb5213508f64a112309b07a495
- **2026-06-08 00:19:03.227511** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5102b68feebf7692d9fc1bbe2097e5d5
