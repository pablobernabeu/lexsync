# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-13 22:14:43.44208
- Finished: 2026-06-13 22:14:44.832123

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:14:43.442593** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 22:14:44.004786** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:14:44.013271** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-13 22:14:44.536365** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13 22:14:44.54929** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:44.549666** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:44.549955** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:44.550224** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:44.591555** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 83ac260307e41472e1b694c80270a560
- **2026-06-13 22:14:44.605189** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-06-13 22:14:44.61956** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 59a4472a0f4f6557e74f11ad3d087853
- **2026-06-13 22:14:44.722506** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 15e1d41909c5b072fe4ea4cc14faff0d
- **2026-06-13 22:14:44.727817** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 17b37538967b395adb7b014c4aeadf25
- **2026-06-13 22:14:44.732893** -- wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 27205a06384e6eca771be3870e91053e
- **2026-06-13 22:14:44.822368** -- wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 1e1a2353a7c3252ecd761b5c199608d3
- **2026-06-13 22:14:44.827457** -- wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 70e9f00f74c49966e2e1595cb073f016
