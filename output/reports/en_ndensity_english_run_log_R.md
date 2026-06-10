# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-10 09:31:49.601042
- Finished: 2026-06-10 09:31:50.659932

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-10 09:31:49.601703** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-10 09:31:49.743449** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 09:31:49.753508** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-10 09:31:50.367263** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-10 09:31:50.385997** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:50.386557** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:50.387002** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:50.387294** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:50.455075** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 6a066b5bbafd349e160d4397fc6712d3
- **2026-06-10 09:31:50.471832** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-06-10 09:31:50.486225** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 2857481af5ebfa4b40328466c16555fe
- **2026-06-10 09:31:50.646662** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 081a9d25566a6b6214a0b2d805550491
- **2026-06-10 09:31:50.65368** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: b820f21fbc33e250cd8a8fd9c1c628ee
