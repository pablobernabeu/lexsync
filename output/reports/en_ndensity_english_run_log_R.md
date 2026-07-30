# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-07-30 15:20:49.307672
- Finished: 2026-07-30 15:20:51.171543

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:20:49.315522**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-30 15:20:50.030925**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30 15:20:50.04861**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-30 15:20:50.695759**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-30 15:20:50.721895**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-30 15:20:50.726268**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-30 15:20:50.730003**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:20:50.734797**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:20:50.778736**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-07-30 15:20:50.79658**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-07-30 15:20:50.811448**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-07-30 15:20:51.025214**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-07-30 15:20:51.036677**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-07-30 15:20:51.043246**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 6d7cb383cfc3114c18f7f1499950ac35
- **2026-07-30 15:20:51.15229**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 350424bf8ba18880054566c8e48dfa89
- **2026-07-30 15:20:51.163286**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 80e0f0ceb2d8eda22cad2f536a918189
