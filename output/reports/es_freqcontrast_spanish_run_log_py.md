# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-24T09:01:34
- Finished: 2026-06-24T09:01:35

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-24T09:01:34**: loading lexicon 'corpora/derived/es.csv'
- **2026-06-24T09:01:34**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-24T09:01:34**: pool after filters: 7172 words
    - pool: 7172
- **2026-06-24T09:01:35**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-24T09:01:35**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-06-24T09:01:35**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.0 (not shown equivalent)
- **2026-06-24T09:01:35**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-06-24T09:01:35**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: 99cb8a7c11731730a4f516f07dee932b
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 8
    - md5: 39ab32df0422848e430490693e909303
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 4
    - md5: 080825223c6c60489cad313d8cf88a46
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: 6cdee30fd7faa7ca2dcf1576696daa55
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: 5fcc2c64c3a9bb725a4b8e1b2565d493
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish.html'
    - path: output\experiments\es_freqcontrast_spanish.html
    - rows: None
    - md5: f7784cdcf794ae96fedf2e3f7877b673
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_datasheet_py.json'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.json
    - rows: None
    - md5: a96a647f18e9449835d7096b273fef67
- **2026-06-24T09:01:35**: wrote 'es_freqcontrast_spanish_datasheet_py.md'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.md
    - rows: None
    - md5: f3d9e926b13effa3f93042bafe0aba01
