# lexsync run log: zh_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-06 08:56:48.917244
- Finished: 2026-07-06 08:56:50.198503

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06 08:56:48.924883**: loading lexicon 'corpora/derived/zh.csv'
- **2026-07-06 08:56:49.37629**: lexicon loaded: 20000 words
    - words: 20000
- **2026-07-06 08:56:49.398531**: pool after filters: 13613 words
    - pool: 13613
- **2026-07-06 08:56:49.757593**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-06 08:56:49.78701**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-07-06 08:56:49.796673**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:49.804224**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-07-06 08:56:49.810708**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-07-06 08:56:49.856446**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 09122d7d5b86f5e05be0f1905635291b
- **2026-07-06 08:56:49.882577**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-07-06 08:56:49.907697**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-07-06 08:56:50.036366**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: b6e12aaddc827bf21b3279f5f8727deb
- **2026-07-06 08:56:50.050518**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: ccda579609c93d507d1b2d7226d45db3
- **2026-07-06 08:56:50.063586**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 3833d4df4562048915729a5138a40c3e
- **2026-07-06 08:56:50.1738**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: d8ca9cbfa5aca36fec3de0c8933aa414
- **2026-07-06 08:56:50.186926**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 39a168d0b664da3a5a599ab511e12b90
