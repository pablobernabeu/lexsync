# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-13 11:12:43.976819
- Finished: 2026-10-13 11:12:49.685002

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:12:43.993172**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-13 11:12:44.912943**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-13 11:12:45.008756**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-13 11:12:46.804815**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13 11:12:47.821291**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-10-13 11:12:47.832722**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 11:12:47.84527**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-10-13 11:12:47.857212**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-10-13 11:12:47.867416**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.758 (not shown equivalent)
- **2026-10-13 11:12:48.010366**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-10-13 11:12:48.049919**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-10-13 11:12:48.086795**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-10-13 11:12:49.153512**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 4f665f037c7d88a372192388610f272b
- **2026-10-13 11:12:49.182208**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 7e70d048990eff3922d9143958556f7d
- **2026-10-13 11:12:49.202567**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: c31f067f3ccd055c462d7b0a8f7a4801
- **2026-10-13 11:12:49.232476**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.csv
    - rows: NA
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-10-13 11:12:49.252832**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13 11:12:49.271513**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame_text.csv
    - rows: NA
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-10-13 11:12:49.637899**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: d70b387f38c56aff586ed6af5483b6cc
- **2026-10-13 11:12:49.660556**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: f4f20e8c45b9aafcd6a2e2194abc8cac
