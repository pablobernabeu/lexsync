# lexsync run log: zh_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-10 10:16:47.454108
- Finished: 2026-06-10 10:16:48.178969

## Run metadata

- design: zh_freqcontrast
- language: chinese
- lexicon: corpora/derived/zh.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10 10:16:47.454758** -- loading lexicon 'corpora/derived/zh.csv'
- **2026-06-10 10:16:47.542007** -- lexicon loaded: 20000 words
    - words: 20000
- **2026-06-10 10:16:47.56162** -- pool after filters: 13613 words
    - pool: 13613
- **2026-06-10 10:16:47.946976** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10 10:16:47.970166** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-06-10 10:16:47.970724** -- equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-06-10 10:16:47.971148** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-06-10 10:16:47.971509** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-06-10 10:16:48.021424** -- wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: f7d55f5ebbee261c4de1f37803e06390
- **2026-06-10 10:16:48.035946** -- wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-06-10 10:16:48.049125** -- wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 1865ab1b5e96037795319fde3d0619e6
- **2026-06-10 10:16:48.165683** -- wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 6f15c58d8867967b660b08c4f7c22d50
- **2026-06-10 10:16:48.172652** -- wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 36c1242813023044f20c1633e5b280d5
