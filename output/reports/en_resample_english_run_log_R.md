# lexsync run log: en_resample

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:01.97149
- Finished: 2026-09-02 19:25:02.599936

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:01.97175**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:25:02.193583**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:25:02.199406**: pool after filters: 10205 words
    - pool: 10205
- **2026-09-02 19:25:02.529031**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:25:02.539431**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.0002 (equivalent)
- **2026-09-02 19:25:02.539657**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:02.53985**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.0002 (equivalent)
- **2026-09-02 19:25:02.540002**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.0001 (equivalent)
- **2026-09-02 19:25:02.55388**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-09-02 19:25:02.556353**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-09-02 19:25:02.558218**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-09-02 19:25:02.581899**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: feeddd0552d7fc9d304bd46e6c977f99
- **2026-09-02 19:25:02.582123**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-09-02 19:25:02.582227**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: b359dd820965bdd0cd83ac90cd2fa25c
- **2026-09-02 19:25:02.599593**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: efd9815734fa8466abffcec90c179afe
- **2026-09-02 19:25:02.599776**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: f1199b4387b58852a6c08cba47782b55
