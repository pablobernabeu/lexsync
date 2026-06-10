# lexsync run log: es_ndensity

- Engine: R 4.5.1
- Started: 2026-06-10 10:16:46.52674
- Finished: 2026-06-10 10:16:47.435459

## Run metadata

- design: es_ndensity
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-10 10:16:46.527422** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-10 10:16:46.688212** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 10:16:46.695206** -- pool after filters: 4002 words
    - pool: 4002
- **2026-06-10 10:16:47.204747** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-10 10:16:47.221572** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-10 10:16:47.221956** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-10 10:16:47.222271** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.000 (not shown equivalent)
- **2026-06-10 10:16:47.222528** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.000 (not shown equivalent)
- **2026-06-10 10:16:47.2783** -- wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 7394777ae5e0705cf2499a226e633451
- **2026-06-10 10:16:47.292453** -- wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 9fc1bba7309f3a8ec77099714b0eab0e
- **2026-06-10 10:16:47.305319** -- wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: f05264def44245723768e6f42f9361c1
- **2026-06-10 10:16:47.422696** -- wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 482de3cb5213508f64a112309b07a495
- **2026-06-10 10:16:47.428979** -- wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 5102b68feebf7692d9fc1bbe2097e5d5
