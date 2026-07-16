# lexsync run log: en_resample

- Engine: Python 3.13.7
- Started: 2026-07-17T01:54:56
- Finished: 2026-07-17T01:54:57

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-17T01:54:56**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-17T01:54:56**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-17T01:54:56**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-17T01:54:57**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-17T01:54:57**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.0002 (equivalent)
- **2026-07-17T01:54:57**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.0 (not shown equivalent)
- **2026-07-17T01:54:57**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.0002 (equivalent)
- **2026-07-17T01:54:57**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.0001 (equivalent)
- **2026-07-17T01:54:57**: wrote 'en_resample_english_stimuli_py.csv'
    - path: output\stimuli\en_resample_english_stimuli_py.csv
    - rows: 240
    - md5: 784e863afc8432fe95365c3a890fde07
- **2026-07-17T01:54:57**: wrote 'en_resample_english_descriptives_py.csv'
    - path: output\reports\en_resample_english_descriptives_py.csv
    - rows: 8
    - md5: 0860358d6084790a5d1a100a83dc59d7
- **2026-07-17T01:54:57**: wrote 'en_resample_english_comparisons_py.csv'
    - path: output\reports\en_resample_english_comparisons_py.csv
    - rows: 4
    - md5: 59422ca1f0326e0697837c92bc0b7ca2
- **2026-07-17T01:54:57**: wrote 'en_resample_english_psychopy.py'
    - path: output\experiments\en_resample_english_psychopy.py
    - rows: None
    - md5: 2eb83593c4677cf94ebff2c15223bce5
- **2026-07-17T01:54:57**: wrote 'en_resample_english.osexp'
    - path: output\experiments\en_resample_english.osexp
    - rows: None
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-07-17T01:54:57**: wrote 'en_resample_english.html'
    - path: output\experiments\en_resample_english.html
    - rows: None
    - md5: 49ac85e23221649870bb780ab2f53410
- **2026-07-17T01:54:57**: wrote 'en_resample_english_datasheet_py.json'
    - path: output\reports\en_resample_english_datasheet_py.json
    - rows: None
    - md5: b512b2c890b732b3e8d6eb17bb5f3c3f
- **2026-07-17T01:54:57**: wrote 'en_resample_english_datasheet_py.md'
    - path: output\reports\en_resample_english_datasheet_py.md
    - rows: None
    - md5: 0c380c9175d1644a1ba5cdf4c487372f
