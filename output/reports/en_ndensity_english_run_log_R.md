# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-07 13:15:17.686269
- Finished: 2026-06-07 13:15:17.83445

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-07 13:15:17.686644** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-07 13:15:17.719854** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 13:15:17.721203** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-07 13:15:17.727994** -- matched 48 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-07 13:15:17.734765** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.05, TOST p = 0.063 (not shown equivalent)
- **2026-06-07 13:15:17.734956** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.23, TOST p = 0.174 (not shown equivalent)
- **2026-06-07 13:15:17.752045** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 48
    - md5: 66b4d76170f877eef760ceb2678a7f4f
- **2026-06-07 13:15:17.762574** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 4
    - md5: 42c7583f92a2dc7889e4306cc88612e8
- **2026-06-07 13:15:17.771884** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 2
    - md5: a325395f83b1297a74619abe0270b854
- **2026-06-07 13:15:17.824895** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 081a9d25566a6b6214a0b2d805550491
- **2026-06-07 13:15:17.829616** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 84b49dec9c68c80ff9ac8a5cf4c169e4
