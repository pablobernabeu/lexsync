# lexsync run log: zh_freqcontrast

- Engine: R 4.6.0
- Started: 2026-06-23 10:19:01.804626
- Finished: 2026-06-23 10:19:03.0567

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:19:01.811919**: loading lexicon 'corpora/derived/zh.csv'
- **2026-06-23 10:19:02.283847**: lexicon loaded: 20000 words
    - words: 20000
- **2026-06-23 10:19:02.298685**: pool after filters: 13613 words
    - pool: 13613
- **2026-06-23 10:19:02.621235**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-23 10:19:02.644446**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-06-23 10:19:02.65219**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:19:02.658701**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-06-23 10:19:02.665796**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-06-23 10:19:02.715085**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 09122d7d5b86f5e05be0f1905635291b
- **2026-06-23 10:19:02.739014**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-06-23 10:19:02.762536**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 1865ab1b5e96037795319fde3d0619e6
- **2026-06-23 10:19:02.89021**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: b6e12aaddc827bf21b3279f5f8727deb
- **2026-06-23 10:19:02.901614**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: ccda579609c93d507d1b2d7226d45db3
- **2026-06-23 10:19:02.915031**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 1f2d7a6495c1e2a75df3bfeab68d82ea
- **2026-06-23 10:19:03.023495**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 009d0365b9fd210e4b71a20a15a8dbc9
- **2026-06-23 10:19:03.03875**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: f71e6986082dc0ba71787f2900f3ed4c
