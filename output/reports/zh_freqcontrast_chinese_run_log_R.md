# lexsync run log: zh_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-03 08:07:56.36589
- Finished: 2026-07-03 08:07:57.106539

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 08:07:56.374085**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-03 08:07:56.587572**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-03 08:07:56.596798**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-03 08:07:56.82568**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-03 08:07:56.838808**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-07-03 08:07:56.843925**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 08:07:56.848782**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-07-03 08:07:56.853381**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-07-03 08:07:56.881698**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 09122d7d5b86f5e05be0f1905635291b
- **2026-07-03 08:07:56.898666**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-07-03 08:07:56.915946**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 1865ab1b5e96037795319fde3d0619e6
- **2026-07-03 08:07:56.99882**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: b6e12aaddc827bf21b3279f5f8727deb
- **2026-07-03 08:07:57.007562**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: ccda579609c93d507d1b2d7226d45db3
- **2026-07-03 08:07:57.017525**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 3833d4df4562048915729a5138a40c3e
- **2026-07-03 08:07:57.086246**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 7fa8639c37f031f5c851a5c3ba5acf6e
- **2026-07-03 08:07:57.095117**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: ac5364f97b6e85aee24d9605e1352ab7
