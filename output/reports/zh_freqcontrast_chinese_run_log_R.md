# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-08-07 22:50:12.252355
- Finished: 2026-08-07 22:50:13.169475

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-07 22:50:12.256112**: loading lexicon 'corpora/derived/zh.csv'
- **2026-08-07 22:50:12.467659**: lexicon loaded: 20000 words
    - words: 20000
- **2026-08-07 22:50:12.476666**: pool after filters: 13613 words
    - pool: 13613
- **2026-08-07 22:50:12.831146**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-08-07 22:50:12.845494**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-08-07 22:50:12.849991**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-08-07 22:50:12.854049**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-08-07 22:50:12.858074**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-08-07 22:50:12.899101**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-08-07 22:50:12.916239**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-08-07 22:50:12.933172**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-08-07 22:50:13.03644**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-08-07 22:50:13.044089**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-08-07 22:50:13.050619**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 08eabfab828b19451270da1b3305b34a
- **2026-08-07 22:50:13.151301**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: d4c9c788db60e42472908bf5074047e7
- **2026-08-07 22:50:13.160319**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 8800091020a88b19e478efbd9581a5ac
