# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-16 16:37:46.500994
- Finished: 2026-07-16 16:37:49.353397

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16 16:37:46.510881**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-16 16:37:47.605368**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-16 16:37:47.642024**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-16 16:37:48.443738**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-16 16:37:48.484939**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-07-16 16:37:48.498522**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-07-16 16:37:48.507165**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-07-16 16:37:48.519063**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-07-16 16:37:48.635746**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 09122d7d5b86f5e05be0f1905635291b
- **2026-07-16 16:37:48.677819**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-07-16 16:37:48.723453**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-07-16 16:37:49.028241**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 60ea532ad24287d81409a84e2dacb461
- **2026-07-16 16:37:49.050776**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-07-16 16:37:49.069069**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: de261923c2a64fbde3f5c82684472693
- **2026-07-16 16:37:49.305866**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 1617f0835965ebb5466f132689a58a83
- **2026-07-16 16:37:49.330539**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 56394a12354e596a3eb0fc377df4e3dd
