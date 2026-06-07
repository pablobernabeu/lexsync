# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-07 13:15:18.001665
- Finished: 2026-06-07 13:15:18.122142

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-07 13:15:18.001925** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07 13:15:18.026167** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 13:15:18.027855** -- pool after filters: 3934 words
    - pool: 3934
- **2026-06-07 13:15:18.035034** -- matched 48 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-07 13:15:18.038327** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.06, TOST p = 0.069 (not shown equivalent)
- **2026-06-07 13:15:18.038482** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.12, TOST p = 0.100 (not shown equivalent)
- **2026-06-07 13:15:18.053758** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 48
    - md5: caebc912393e8d1fbae9e21059500fd5
- **2026-06-07 13:15:18.063794** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 4
    - md5: 26db1ca5bc4968a20b2cac4ff76a8fb2
- **2026-06-07 13:15:18.07259** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 2
    - md5: 3390192feefd1195dc979d0003bfa40b
- **2026-06-07 13:15:18.112478** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 482de3cb5213508f64a112309b07a495
- **2026-06-07 13:15:18.117146** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: b9d18212b9d82f1b58f14738e2aa5508
