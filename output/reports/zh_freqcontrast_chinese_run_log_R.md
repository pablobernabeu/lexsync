# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 09:53:19.029421
- Finished: 2026-10-09 09:53:21.077751

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:53:19.033317**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-09 09:53:19.475856**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-09 09:53:19.488696**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-09 09:53:20.09621**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 09:53:20.475317**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-10-09 09:53:20.47977**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.39, 6.62], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:53:20.483415**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-10-09 09:53:20.486428**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-10-09 09:53:20.489916**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.77 [0.50, 1.04], TOST p = 0.956 (not shown equivalent)
- **2026-10-09 09:53:20.531388**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 49c657a97d85cb1a62290b4e17832dc3
- **2026-10-09 09:53:20.547678**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 10
    - md5: 43d9d4593c5a75d46f6b9219adcb9bec
- **2026-10-09 09:53:20.562007**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 5
    - md5: e4bf90986a8e3baea3634feb339d8829
- **2026-10-09 09:53:20.873833**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 4f665f037c7d88a372192388610f272b
- **2026-10-09 09:53:20.883997**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 7e70d048990eff3922d9143958556f7d
- **2026-10-09 09:53:20.893899**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 06b83f235c74aa4cf7d427e0610a37ce
- **2026-10-09 09:53:20.90607**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.csv
    - rows: NA
    - md5: 9cd7729198f7d3ad0f8c0c1f06721b41
- **2026-10-09 09:53:20.914509**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 09:53:20.922266**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame_text.csv
    - rows: NA
    - md5: aff6c7fdc794765e18681f29e25b1fa3
- **2026-10-09 09:53:21.055794**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 9540e88accf3cc539f684da9bba72701
- **2026-10-09 09:53:21.068266**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 605eb7e54f149e2c1c4d5fea9e905ec4
