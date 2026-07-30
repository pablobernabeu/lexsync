# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-07-30 15:20:53.725134
- Finished: 2026-07-30 15:20:55.851943

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:20:53.733165**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-30 15:20:54.440228**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30 15:20:54.467855**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-30 15:20:55.154865**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-30 15:20:55.192064**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-07-30 15:20:55.197734**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:20:55.204118**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-07-30 15:20:55.219834**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-07-30 15:20:55.323354**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-07-30 15:20:55.352288**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-07-30 15:20:55.379566**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-07-30 15:20:55.61944**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 5dfa6ea79de17442db4c7c2c81e2e589
- **2026-07-30 15:20:55.638836**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-07-30 15:20:55.653983**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 4a037f8241168a110d06ea9ae3a0cf4d
- **2026-07-30 15:20:55.814651**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: d20aa4ae4ede53f9cebd84a3978875a2
- **2026-07-30 15:20:55.82821**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: c28a8e22c7960f3a60fe4abe8d29112b
