# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-08 00:19:02.551446
- Finished: 2026-06-08 00:19:02.7558

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-08 00:19:02.551685** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-08 00:19:02.606703** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-08 00:19:02.610534** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-08 00:19:02.623609** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-08 00:19:02.629347** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.25, TOST p = 0.056 (not shown equivalent)
- **2026-06-08 00:19:02.629516** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.15, TOST p = 0.014 (equivalent)
- **2026-06-08 00:19:02.62968** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.11, TOST p = 1.000 (not shown equivalent)
- **2026-06-08 00:19:02.629809** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.89, TOST p = 1.000 (not shown equivalent)
- **2026-06-08 00:19:02.655211** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 21063b06cf3544a8193879f817f76e73
- **2026-06-08 00:19:02.664061** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: d719dfe8e47e7e6954316402202f6d90
- **2026-06-08 00:19:02.672516** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: b74f22403369f7cbd2751f9410e57b04
- **2026-06-08 00:19:02.744461** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 081a9d25566a6b6214a0b2d805550491
- **2026-06-08 00:19:02.750599** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: b820f21fbc33e250cd8a8fd9c1c628ee
