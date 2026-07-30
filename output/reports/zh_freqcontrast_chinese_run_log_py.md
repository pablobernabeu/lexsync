# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-07-30T15:23:35
- Finished: 2026-07-30T15:23:36

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30T15:23:35**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-30T15:23:35**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-30T15:23:35**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-30T15:23:36**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-30T15:23:36**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-07-30T15:23:36**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.0 (not shown equivalent)
- **2026-07-30T15:23:36**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-07-30T15:23:36**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.0069 (equivalent)
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese.html'
    - path: output\experiments\zh_freqcontrast_chinese.html
    - rows: None
    - md5: cb0cc9e8b19d99a209d9cb944f823a24
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: c7fb406099ec3f8e38d51be86e889575
- **2026-07-30T15:23:36**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: cd1c03e1999b1d86f52e12cf5748016c
