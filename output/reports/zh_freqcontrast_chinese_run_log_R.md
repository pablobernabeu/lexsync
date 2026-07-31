# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:32.999966
- Finished: 2026-07-31 21:48:33.919641

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:33.002696**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-31 21:48:33.268067**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-31 21:48:33.277892**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-31 21:48:33.506563**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 21:48:33.521265**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-07-31 21:48:33.526951**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:33.531393**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-07-31 21:48:33.535469**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-07-31 21:48:33.581934**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-07-31 21:48:33.599448**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-07-31 21:48:33.618209**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-07-31 21:48:33.744062**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-07-31 21:48:33.765223**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-07-31 21:48:33.778753**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: cb0cc9e8b19d99a209d9cb944f823a24
- **2026-07-31 21:48:33.896818**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 2b17b994bae0b85a945e181cd16793d8
- **2026-07-31 21:48:33.911951**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 941a9476662a3117ad5e94d53590b8ab
