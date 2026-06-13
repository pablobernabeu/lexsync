# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-13 18:21:17.270575
- Finished: 2026-06-13 18:21:17.995431

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 18:21:17.270984** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 18:21:17.349773** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 18:21:17.355372** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-13 18:21:17.794288** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13 18:21:17.805124** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:17.805629** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:17.806104** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:17.806468** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:17.845954** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 6a066b5bbafd349e160d4397fc6712d3
- **2026-06-13 18:21:17.859923** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-06-13 18:21:17.873338** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 59a4472a0f4f6557e74f11ad3d087853
- **2026-06-13 18:21:17.981362** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 15e1d41909c5b072fe4ea4cc14faff0d
- **2026-06-13 18:21:17.989526** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 17b37538967b395adb7b014c4aeadf25
