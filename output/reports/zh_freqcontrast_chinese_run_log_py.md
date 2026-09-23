# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-09-23T23:15:00
- Finished: 2026-09-23T23:15:03

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-23T23:15:00**: loading lexicon 'corpora/derived/zh.csv'
- **2026-09-23T23:15:01**: lexicon loaded: 20000 words
    - words: 20000
- **2026-09-23T23:15:01**: pool after filters: 13613 words
    - pool: 13613
- **2026-09-23T23:15:02**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-23T23:15:02**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-09-23T23:15:02**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.39, 6.62], TOST p = 1.0 (not shown equivalent)
- **2026-09-23T23:15:02**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-09-23T23:15:02**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.0069 (equivalent)
- **2026-09-23T23:15:02**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-09-23T23:15:02**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-09-23T23:15:02**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 4
    - md5: 9823b728460d1fa1069400ef92b274d5
- **2026-09-23T23:15:03**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-09-23T23:15:03**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-09-23T23:15:03**: wrote 'zh_freqcontrast_chinese.html'
    - path: output\experiments\zh_freqcontrast_chinese.html
    - rows: None
    - md5: 04f5aba638eeed04e20d12e5763d50a7
- **2026-09-23T23:15:03**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: 436233af5bde2842ea06ba7a411f79e6
- **2026-09-23T23:15:03**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: d97d8ddc6ac2211283f1a1c8863e6346
