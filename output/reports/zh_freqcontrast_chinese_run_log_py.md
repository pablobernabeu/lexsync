# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-09T11:51:28
- Finished: 2026-10-09T11:51:30

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T11:51:28**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-09T11:51:29**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-09T11:51:29**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-09T11:51:30**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09T11:51:30**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-10-09T11:51:30**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:30**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-10-09T11:51:30**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.0069 (equivalent)
- **2026-10-09T11:51:30**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.7585 (not shown equivalent)
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: 4f665f037c7d88a372192388610f272b
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 7e70d048990eff3922d9143958556f7d
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese.html'
    - path: output\experiments\zh_freqcontrast_chinese.html
    - rows: None
    - md5: c31f067f3ccd055c462d7b0a8f7a4801
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.csv
    - rows: None
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame_text.csv
    - rows: None
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: 0de3b9c220760626643efb7cb165ad9d
- **2026-10-09T11:51:30**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: ef585f4d4a57ee47156f7265ef223770
