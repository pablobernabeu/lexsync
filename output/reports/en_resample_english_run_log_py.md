# lexsync run log: en_resample

- Engine: Python 3.11.15
- Started: 2026-09-02T19:25:44
- Finished: 2026-09-02T19:25:44

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02T19:25:44**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02T19:25:44**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02T19:25:44**: pool after filters: 10205 words
    - pool: 10205
- **2026-09-02T19:25:44**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-09-02T19:25:44**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.0002 (equivalent)
- **2026-09-02T19:25:44**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02T19:25:44**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.0002 (equivalent)
- **2026-09-02T19:25:44**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.0001 (equivalent)
- **2026-09-02T19:25:44**: wrote 'en_resample_english_stimuli_py.csv'
    - path: output/stimuli/en_resample_english_stimuli_py.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-09-02T19:25:44**: wrote 'en_resample_english_descriptives_py.csv'
    - path: output/reports/en_resample_english_descriptives_py.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-09-02T19:25:44**: wrote 'en_resample_english_comparisons_py.csv'
    - path: output/reports/en_resample_english_comparisons_py.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-09-02T19:25:44**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: None
    - md5: feeddd0552d7fc9d304bd46e6c977f99
- **2026-09-02T19:25:44**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: None
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-09-02T19:25:44**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: None
    - md5: b359dd820965bdd0cd83ac90cd2fa25c
- **2026-09-02T19:25:44**: wrote 'en_resample_english_datasheet_py.json'
    - path: output/reports/en_resample_english_datasheet_py.json
    - rows: None
    - md5: 3d1adeb56cb66db9665d79e54a32ce2d
- **2026-09-02T19:25:44**: wrote 'en_resample_english_datasheet_py.md'
    - path: output/reports/en_resample_english_datasheet_py.md
    - rows: None
    - md5: 7dbbe81478bc217b22e5c6c86a594c5a
