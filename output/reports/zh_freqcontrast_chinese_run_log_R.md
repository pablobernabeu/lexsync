# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:48.130607
- Finished: 2026-08-01 00:33:48.782574

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01 00:33:48.133111**: loading lexicon 'corpora/derived/zh.csv'
- **2026-08-01 00:33:48.322827**: lexicon loaded: 20000 words
    - words: 20000
- **2026-08-01 00:33:48.331422**: pool after filters: 13613 words
    - pool: 13613
- **2026-08-01 00:33:48.512626**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-08-01 00:33:48.524448**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-08-01 00:33:48.527999**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:48.530333**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-08-01 00:33:48.532541**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-08-01 00:33:48.564329**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-08-01 00:33:48.575589**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-08-01 00:33:48.586898**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-08-01 00:33:48.674276**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-08-01 00:33:48.683767**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-08-01 00:33:48.691352**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 08eabfab828b19451270da1b3305b34a
- **2026-08-01 00:33:48.765375**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: f63006715b1a2d709a2a56d1ce75e65b
- **2026-08-01 00:33:48.774307**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 03c06a65d465f3c4788af374cc84fcae
