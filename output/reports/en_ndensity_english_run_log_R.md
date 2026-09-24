# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-09-24 17:00:07.953175
- Finished: 2026-09-24 17:00:10.590262

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 17:00:07.958563**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-24 17:00:08.512994**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-24 17:00:08.531556**: pool after filters: 4557 words
    - pool: 4557
- **2026-09-24 17:00:09.587527**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-09-24 17:00:09.621309**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-09-24 17:00:09.627541**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-09-24 17:00:09.637603**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 17:00:09.64787**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 17:00:09.737347**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-09-24 17:00:09.772415**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-09-24 17:00:09.798392**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-09-24 17:00:10.352936**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-09-24 17:00:10.367301**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-09-24 17:00:10.37716**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 088cf6eb4cbf699c316e3ee784cdd6fa
- **2026-09-24 17:00:10.55845**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 3322ba8c983d5a6d64fc503b470f793f
- **2026-09-24 17:00:10.574658**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 4072fb228bdd7cddc15a12655e028209
