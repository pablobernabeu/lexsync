# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-13T18:36:39
- Finished: 2026-06-13T18:36:40

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13T18:36:39** -- loading lexicon 'corpora/derived/zh.csv'
- **2026-06-13T18:36:39** -- lexicon loaded: 20000 words
    - words: 20000
- **2026-06-13T18:36:39** -- pool after filters: 13613 words
    - pool: 13613
- **2026-06-13T18:36:40** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13T18:36:40** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-06-13T18:36:40** -- equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T18:36:40** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-06-13T18:36:40** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.0069 (equivalent)
- **2026-06-13T18:36:40** -- wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: a99e718d626a92068c3b67a0ce8d6395
- **2026-06-13T18:36:40** -- wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 8
    - md5: 2c285a990f8684b4fcfe0f333f2053ee
- **2026-06-13T18:36:40** -- wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 4
    - md5: 469b7abb6e8a751bcaa99702e8b414d3
- **2026-06-13T18:36:40** -- wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: 996c63c2c74960818869699d8bd1bf07
- **2026-06-13T18:36:40** -- wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 410251dd6b97b6ef49bd018f6999c1ee
