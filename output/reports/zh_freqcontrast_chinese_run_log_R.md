# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-13 18:18:14.733518
- Finished: 2026-10-13 18:18:19.250609

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:18:14.750525**: lexsync: the design gives no `instructions` and its language is 'chinese', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13 18:18:14.766217**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:18:14.776133**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-13 18:18:15.582986**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-13 18:18:15.605477**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-13 18:18:17.126286**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13 18:18:17.807099**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-10-13 18:18:17.81427**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 18:18:17.820433**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-10-13 18:18:17.826451**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-10-13 18:18:17.833603**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.758 (not shown equivalent)
- **2026-10-13 18:18:17.939614**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-10-13 18:18:17.976906**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-10-13 18:18:18.006717**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-10-13 18:18:18.861561**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: a6a7f3386f85d5b659706cd875258521
- **2026-10-13 18:18:18.891229**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 602393415338ef783b675bbff7896f30
- **2026-10-13 18:18:18.916332**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: bf72a1fbc85c13445bc83ac78f30a4e4
- **2026-10-13 18:18:18.937571**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.csv
    - rows: NA
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-10-13 18:18:18.951178**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13 18:18:18.963935**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame_text.csv
    - rows: NA
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-10-13 18:18:19.21605**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 51faba5bf99d2d5661d0a55ad66326e7
- **2026-10-13 18:18:19.233635**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: f4f20e8c45b9aafcd6a2e2194abc8cac
