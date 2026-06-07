# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-07 14:11:48.628124
- Finished: 2026-06-07 14:11:49.012623

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-07 14:11:48.629271** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07 14:11:48.728175** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 14:11:48.73345** -- pool after filters: 3934 words
    - pool: 3934
- **2026-06-07 14:11:48.754909** -- matched 48 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-07 14:11:48.797726** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.06, TOST p = 0.069 (not shown equivalent)
- **2026-06-07 14:11:48.798272** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.12, TOST p = 0.100 (not shown equivalent)
- **2026-06-07 14:11:48.798805** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.31, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:48.799226** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.33, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:48.84446** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 48
    - md5: caebc912393e8d1fbae9e21059500fd5
- **2026-06-07 14:11:48.867607** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7843b28b5d799cda73baee05ac3ecba2
- **2026-06-07 14:11:48.89495** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 33bbc71d9559728f3b67ba6eaedbe757
- **2026-06-07 14:11:48.993217** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 482de3cb5213508f64a112309b07a495
- **2026-06-07 14:11:49.002477** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: b9d18212b9d82f1b58f14738e2aa5508
