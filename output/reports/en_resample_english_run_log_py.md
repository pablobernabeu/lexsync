# lexsync run log: en_resample

- Engine: Python 3.13.7
- Started: 2026-08-01T11:51:59
- Finished: 2026-08-01T11:52:01

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01T11:51:59**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-01T11:52:00**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-01T11:52:00**: pool after filters: 10205 words
    - pool: 10205
- **2026-08-01T11:52:01**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-08-01T11:52:01**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.0002 (equivalent)
- **2026-08-01T11:52:01**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.0 (not shown equivalent)
- **2026-08-01T11:52:01**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.0002 (equivalent)
- **2026-08-01T11:52:01**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.0001 (equivalent)
- **2026-08-01T11:52:01**: wrote 'en_resample_english_stimuli_py.csv'
    - path: output\stimuli\en_resample_english_stimuli_py.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-08-01T11:52:01**: wrote 'en_resample_english_descriptives_py.csv'
    - path: output\reports\en_resample_english_descriptives_py.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-08-01T11:52:01**: wrote 'en_resample_english_comparisons_py.csv'
    - path: output\reports\en_resample_english_comparisons_py.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-08-01T11:52:01**: wrote 'en_resample_english_psychopy.py'
    - path: output\experiments\en_resample_english_psychopy.py
    - rows: None
    - md5: 5dfa6ea79de17442db4c7c2c81e2e589
- **2026-08-01T11:52:01**: wrote 'en_resample_english.osexp'
    - path: output\experiments\en_resample_english.osexp
    - rows: None
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-08-01T11:52:01**: wrote 'en_resample_english.html'
    - path: output\experiments\en_resample_english.html
    - rows: None
    - md5: 78009137a81b18cf1a670265f0087d0d
- **2026-08-01T11:52:01**: wrote 'en_resample_english_datasheet_py.json'
    - path: output\reports\en_resample_english_datasheet_py.json
    - rows: None
    - md5: 6da4e1b50ba32b7cd021ac76fae0b25e
- **2026-08-01T11:52:01**: wrote 'en_resample_english_datasheet_py.md'
    - path: output\reports\en_resample_english_datasheet_py.md
    - rows: None
    - md5: c4c1628686654fcc75938ad66e2fe93f
