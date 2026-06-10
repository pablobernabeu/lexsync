# lexsync run log: zh_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-10 09:31:52.163936
- Finished: 2026-06-10 09:31:52.823862

## Run metadata

- design: zh_freqcontrast
- language: chinese
- lexicon: corpora/derived/zh.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10 09:31:52.164417** -- loading lexicon 'corpora/derived/zh.csv'
- **2026-06-10 09:31:52.241919** -- lexicon loaded: 20000 words
    - words: 20000
- **2026-06-10 09:31:52.26115** -- pool after filters: 13613 words
    - pool: 13613
- **2026-06-10 09:31:52.598434** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10 09:31:52.612813** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.000 (equivalent)
- **2026-06-10 09:31:52.61307** -- equivalence low_frequency vs high_frequency on 'frequency': d = 6.00, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:52.613226** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.07, TOST p = 0.004 (equivalent)
- **2026-06-10 09:31:52.613361** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.11, TOST p = 0.007 (equivalent)
- **2026-06-10 09:31:52.667066** -- wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: f7d55f5ebbee261c4de1f37803e06390
- **2026-06-10 09:31:52.679654** -- wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-06-10 09:31:52.690685** -- wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 089e4f3279c1c43fa17007e624eb196b
- **2026-06-10 09:31:52.811747** -- wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 6f15c58d8867967b660b08c4f7c22d50
- **2026-06-10 09:31:52.818161** -- wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 36c1242813023044f20c1633e5b280d5
