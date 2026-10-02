# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 07:16:12.289448
- Finished: 2026-10-09 07:16:15.123352

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:16:12.294892**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:16:13.086208**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:16:13.101629**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-09 07:16:14.090205**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 07:16:14.132232**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:16:14.138384**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:16:14.143178**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:16:14.148989**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:16:14.218805**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-09 07:16:14.247052**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-09 07:16:14.270433**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-09 07:16:14.793256**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 644b7f22a01b99b7ca0d94c040cf0be5
- **2026-10-09 07:16:14.806605**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: a9903c46919cefb72c1a564b6407ba91
- **2026-10-09 07:16:14.821316**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: e1c3bc4d5c84b8de9ec8aa08b25c677e
- **2026-10-09 07:16:14.842678**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-09 07:16:14.852686**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 07:16:14.862713**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-09 07:16:15.098073**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 290093b42bf967717710817a113f8660
- **2026-10-09 07:16:15.110932**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 9e6c3979d58e3551bf37f82c2abac9e7
