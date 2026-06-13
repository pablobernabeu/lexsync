# lexsync run log: en_ndensity

- Engine: R 4.5.1
- Started: 2026-06-13 22:44:09.851275
- Finished: 2026-06-13 22:44:10.893279

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:44:09.851654** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 22:44:10.254188** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:44:10.259293** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-13 22:44:10.654916** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-13 22:44:10.663456** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:44:10.663717** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-13 22:44:10.663908** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:44:10.664082** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:44:10.696884** -- wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 83ac260307e41472e1b694c80270a560
- **2026-06-13 22:44:10.707616** -- wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-06-13 22:44:10.718309** -- wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 59a4472a0f4f6557e74f11ad3d087853
- **2026-06-13 22:44:10.798023** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 15e1d41909c5b072fe4ea4cc14faff0d
- **2026-06-13 22:44:10.802862** -- wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 17b37538967b395adb7b014c4aeadf25
- **2026-06-13 22:44:10.807124** -- wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 27205a06384e6eca771be3870e91053e
- **2026-06-13 22:44:10.881247** -- wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 4426a4778351e82c1e01eb55a4803404
- **2026-06-13 22:44:10.887521** -- wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 70e9f00f74c49966e2e1595cb073f016
