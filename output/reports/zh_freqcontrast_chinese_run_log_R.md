# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-03 00:41:08.196558
- Finished: 2026-10-03 00:42:31.534939

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:41:08.778944**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-03 00:41:14.690224**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-03 00:41:14.811241**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-03 00:41:17.081968**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03 00:41:17.585511**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-10-03 00:41:18.014187**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.39, 6.62], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:41:18.034321**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-10-03 00:41:18.158694**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-10-03 00:41:26.489686**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-10-03 00:41:27.807321**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-10-03 00:41:28.312688**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 9823b728460d1fa1069400ef92b274d5
- **2026-10-03 00:42:26.89195**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-10-03 00:42:27.07107**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 3ecf66dcf5b8337c44c7d36fe85756ec
- **2026-10-03 00:42:27.190199**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 04f5aba638eeed04e20d12e5763d50a7
- **2026-10-03 00:42:30.203776**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: d9be5c08a8093e57ca05e47a6ec8281f
- **2026-10-03 00:42:30.956258**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: e95bd51ea7d3aa93e0a346d000fb877d
