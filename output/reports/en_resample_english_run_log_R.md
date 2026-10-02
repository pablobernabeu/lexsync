# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-10-03 00:34:08.94895
- Finished: 2026-10-03 00:35:41.017582

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:34:09.169529**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:34:16.093545**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 00:34:16.868693**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-03 00:34:19.632721**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-10-03 00:34:20.019373**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-10-03 00:34:20.117609**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [4.92, 5.84], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:34:20.512238**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-10-03 00:34:20.572984**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-10-03 00:34:29.842072**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-10-03 00:34:31.118806**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-10-03 00:34:31.894993**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 70cb67a8e7d4f1d34dc1c7d4d2c6f28e
- **2026-10-03 00:35:37.224808**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 5dfa6ea79de17442db4c7c2c81e2e589
- **2026-10-03 00:35:37.443108**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2360ba020d77d5201e9ff5b680606e1
- **2026-10-03 00:35:37.811206**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 0bbb5250caae16e7265d68ddeee31041
- **2026-10-03 00:35:40.204216**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 35042572343901522c6c781119b89caf
- **2026-10-03 00:35:40.711327**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: 4bf9b74c52a340fedba451ee59092428
