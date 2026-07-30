# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-30 15:21:05.379299
- Finished: 2026-07-30 15:21:07.209674

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:21:05.385506**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-30 15:21:05.936652**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-30 15:21:05.958172**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-30 15:21:06.50221**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-30 15:21:06.556227**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-07-30 15:21:06.571309**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:21:06.586868**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-07-30 15:21:06.599457**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-07-30 15:21:06.699313**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-07-30 15:21:06.728398**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-07-30 15:21:06.755217**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-07-30 15:21:06.968731**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-07-30 15:21:06.987782**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-07-30 15:21:07.001319**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: cb0cc9e8b19d99a209d9cb944f823a24
- **2026-07-30 15:21:07.175618**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: acb74dc17466320b7363b7b7c6b35904
- **2026-07-30 15:21:07.195202**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 941a9476662a3117ad5e94d53590b8ab
