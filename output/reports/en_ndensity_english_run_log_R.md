# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-02 16:44:23.462684
- Finished: 2026-10-02 16:44:39.996917

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:44:23.507557**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 16:44:25.138158**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:44:25.221028**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-02 16:44:26.687043**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-02 16:44:27.144461**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-02 16:44:27.183808**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-02 16:44:27.220391**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:44:27.285219**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:44:29.641204**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-02 16:44:30.488615**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-02 16:44:31.389282**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-02 16:44:36.681386**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-10-02 16:44:36.790822**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 20eea6534281800fb670f1e595ca224b
- **2026-10-02 16:44:36.966504**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 088cf6eb4cbf699c316e3ee784cdd6fa
- **2026-10-02 16:44:38.932816**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 0f15c929851e649622a27b00d052c6ae
- **2026-10-02 16:44:38.964714**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 4398cd1201e2a71aef304e2f2b2f5c78
