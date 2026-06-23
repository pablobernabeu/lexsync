# lexsync run log: en_ndensity

- Engine: R 4.6.0
- Started: 2026-06-23 10:18:51.216809
- Finished: 2026-06-23 10:18:52.844789

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:18:51.223949**: loading lexicon 'corpora/derived/en.csv'
- **2026-06-23 10:18:51.817346**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-23 10:18:51.842161**: pool after filters: 4557 words
    - pool: 4557
- **2026-06-23 10:18:52.375615**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-23 10:18:52.403568**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-23 10:18:52.411931**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-06-23 10:18:52.419766**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:52.425541**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:52.478152**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 83ac260307e41472e1b694c80270a560
- **2026-06-23 10:18:52.500752**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-06-23 10:18:52.523034**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 59a4472a0f4f6557e74f11ad3d087853
- **2026-06-23 10:18:52.664261**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 9eeaa09c594db721be6eebd5eeb01f63
- **2026-06-23 10:18:52.675563**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 17b37538967b395adb7b014c4aeadf25
- **2026-06-23 10:18:52.686688**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 27205a06384e6eca771be3870e91053e
- **2026-06-23 10:18:52.814047**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: d6687188cbf231996826964e82782cad
- **2026-06-23 10:18:52.827227**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 59273025b8594332110c60b99c7c8a12
