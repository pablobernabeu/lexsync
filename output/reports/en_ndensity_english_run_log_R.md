# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-03 00:32:23.412077
- Finished: 2026-10-03 00:32:59.440297

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:32:23.419499**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:32:26.877406**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 00:32:26.97687**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-03 00:32:29.337525**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-03 00:32:29.695153**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 00:32:29.750091**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 00:32:29.802911**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:32:29.875412**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:32:32.346533**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-03 00:32:33.29537**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-03 00:32:33.851388**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-03 00:32:57.109687**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-10-03 00:32:57.303748**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 20eea6534281800fb670f1e595ca224b
- **2026-10-03 00:32:57.424397**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 088cf6eb4cbf699c316e3ee784cdd6fa
- **2026-10-03 00:32:58.988956**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 4132e4338a3050255662992de670317a
- **2026-10-03 00:32:59.367106**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 4822cfbc9db65cd043b68e40888928ef
