# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-15T03:30:58
- Finished: 2026-10-15T03:31:00

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15T03:30:58**: lexsync: the design gives no `instructions` and its language is 'chinese', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15T03:30:58**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15T03:30:58**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-15T03:30:59**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-15T03:30:59**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-15T03:31:00**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-15T03:31:00**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-10-15T03:31:00**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.0 (not shown equivalent)
- **2026-10-15T03:31:00**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-10-15T03:31:00**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.0069 (equivalent)
- **2026-10-15T03:31:00**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.7585 (not shown equivalent)
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: 3bb7858c089cba2f64d1d0cafa0b47ce
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: 34ba29f107e0f4abae9f9e1b38c5c801
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese.html'
    - path: output\experiments\zh_freqcontrast_chinese.html
    - rows: None
    - md5: 345a3d8c98e923f3a15084b32686e41b
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.csv
    - rows: None
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame_text.csv
    - rows: None
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: 0960071f389b10556c421ff11e54787a
- **2026-10-15T03:31:00**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: ef585f4d4a57ee47156f7265ef223770
