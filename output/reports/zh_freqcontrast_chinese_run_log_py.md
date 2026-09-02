# lexsync run log: zh_freqcontrast

- Engine: Python 3.11.15
- Started: 2026-09-02T19:25:45
- Finished: 2026-09-02T19:25:46

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02T19:25:45**: loading lexicon 'corpora/derived/zh.csv'
- **2026-09-02T19:25:45**: lexicon loaded: 20000 words
    - words: 20000
- **2026-09-02T19:25:45**: pool after filters: 13613 words
    - pool: 13613
- **2026-09-02T19:25:46**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02T19:25:46**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0000 (equivalent)
- **2026-09-02T19:25:46**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02T19:25:46**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-09-02T19:25:46**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.0069 (equivalent)
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: c7ba62668b013e8705048f015e694f86
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: None
    - md5: 0ad2a8ba376cfe37545113b2c24e5b7f
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: bcfe04f9c15e6ca4087bcde45a764a6f
- **2026-09-02T19:25:46**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: ce78fa15509dfed58625a9170f459f7f
