# lexsync run log: zh_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-13T22:50:18
- Finished: 2026-10-13T22:50:22

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T22:50:18**: lexsync: the design gives no `instructions` and its language is 'chinese', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13T22:50:18**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13T22:50:18**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-13T22:50:19**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-13T22:50:19**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-13T22:50:21**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13T22:50:21**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0 (equivalent)
- **2026-10-13T22:50:21**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.0 (not shown equivalent)
- **2026-10-13T22:50:21**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-10-13T22:50:21**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.0069 (equivalent)
- **2026-10-13T22:50:21**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.7585 (not shown equivalent)
- **2026-10-13T22:50:21**: wrote 'zh_freqcontrast_chinese_stimuli_py.csv'
    - path: output\stimuli\zh_freqcontrast_chinese_stimuli_py.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_descriptives_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_descriptives_py.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_comparisons_py.csv'
    - path: output\reports\zh_freqcontrast_chinese_comparisons_py.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.py
    - rows: None
    - md5: e6fae025dc3718992d9fb8a497338b66
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output\experiments\zh_freqcontrast_chinese.osexp
    - rows: None
    - md5: b6494c11b740285fc9f2f6766921efde
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese.html'
    - path: output\experiments\zh_freqcontrast_chinese.html
    - rows: None
    - md5: bf72a1fbc85c13445bc83ac78f30a4e4
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output\experiments\zh_freqcontrast_chinese_psychopy.csv
    - rows: None
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output\experiments\zh_freqcontrast_chinese_opensesame_text.csv
    - rows: None
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_datasheet_py.json'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.json
    - rows: None
    - md5: a15197f1e55f4c9dfc26f108c1731888
- **2026-10-13T22:50:22**: wrote 'zh_freqcontrast_chinese_datasheet_py.md'
    - path: output\reports\zh_freqcontrast_chinese_datasheet_py.md
    - rows: None
    - md5: ef585f4d4a57ee47156f7265ef223770
