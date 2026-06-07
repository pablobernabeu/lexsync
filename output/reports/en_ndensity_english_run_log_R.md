# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-07 14:11:47.397323
- Finished: 2026-06-07 14:11:47.85795

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-07 14:11:47.399047** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-07 14:11:47.499854** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 14:11:47.505159** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-07 14:11:47.530186** -- matched 48 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-07 14:11:47.561611** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.05, TOST p = 0.063 (not shown equivalent)
- **2026-06-07 14:11:47.562557** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.23, TOST p = 0.174 (not shown equivalent)
- **2026-06-07 14:11:47.562832** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.71, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:47.56303** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.13, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:47.638398** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 48
    - md5: 66b4d76170f877eef760ceb2678a7f4f
- **2026-06-07 14:11:47.656482** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 636b6c1c44463cfd197adaf9d3c0afc5
- **2026-06-07 14:11:47.679127** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 64cd5280712d59352add2d3a67a7c211
- **2026-06-07 14:11:47.834186** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 081a9d25566a6b6214a0b2d805550491
- **2026-06-07 14:11:47.84678** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 84b49dec9c68c80ff9ac8a5cf4c169e4
