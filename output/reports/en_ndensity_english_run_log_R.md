# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 05:23:26.922093
- Finished: 2026-10-09 05:23:30.131586

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:23:26.928003**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 05:23:27.813171**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 05:23:27.829817**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-09 05:23:28.886783**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 05:23:28.93824**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 05:23:28.945191**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 05:23:28.951159**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:23:28.962735**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:23:29.062962**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-09 05:23:29.095371**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-09 05:23:29.125728**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-09 05:23:29.669417**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 644b7f22a01b99b7ca0d94c040cf0be5
- **2026-10-09 05:23:29.683176**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: a9903c46919cefb72c1a564b6407ba91
- **2026-10-09 05:23:29.694075**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: e1c3bc4d5c84b8de9ec8aa08b25c677e
- **2026-10-09 05:23:29.710188**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-09 05:23:29.720093**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 05:23:29.7308**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-09 05:23:30.10535**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 10e42ceb45d500eccced70f087819502
- **2026-10-09 05:23:30.119618**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 9e6c3979d58e3551bf37f82c2abac9e7
