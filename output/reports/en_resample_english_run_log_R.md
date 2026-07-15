# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-07-15 10:09:57.401055
- Finished: 2026-07-15 10:09:59.33944

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15 10:09:57.405425**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15 10:09:58.091922**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15 10:09:58.126423**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-15 10:09:58.673369**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-15 10:09:58.762631**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-07-15 10:09:58.770419**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-07-15 10:09:58.775501**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-07-15 10:09:58.780112**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-07-15 10:09:58.836533**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 6da44764e555ff3b46aa170645468254
- **2026-07-15 10:09:58.968433**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-07-15 10:09:58.995882**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-07-15 10:09:59.113634**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 432c4e76e3c3af46c95d2713a738bb6b
- **2026-07-15 10:09:59.126836**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: fd435f746afa9f39c0d6bb6c923fefd9
- **2026-07-15 10:09:59.143675**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 16a3a0841c634c55072377e8e62e6794
- **2026-07-15 10:09:59.30787**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 24b29730afe7fdfd4a4d79fd32130109
- **2026-07-15 10:09:59.325507**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: a6d8ab6e108a868bd02d1e3ef2bec9a1
