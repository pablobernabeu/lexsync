# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-11-02 21:29:11.889894
- Finished: 2026-11-02 21:29:13.391333

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-11-02 21:29:11.890841**: lexsync: the design gives no `instructions` and its language is 'chinese', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-11-02 21:29:11.890997**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-11-02 21:29:11.891201**: loading lexicon 'corpora/derived/zh.csv'
- **2026-11-02 21:29:12.205119**: lexicon loaded: 20000 words
    - words: 20000
- **2026-11-02 21:29:12.209134**: pool after filters: 13613 words
    - pool: 13613
- **2026-11-02 21:29:12.78624**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-11-02 21:29:13.004729**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-11-02 21:29:13.005189**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.11 [5.49, 6.73], TOST p = 1.000 (not shown equivalent)
- **2026-11-02 21:29:13.00555**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-11-02 21:29:13.005881**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-11-02 21:29:13.006205**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.61 [0.34, 0.88], TOST p = 0.758 (not shown equivalent)
- **2026-11-02 21:29:13.046784**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 4a1365f005dca09f61342d15f42c1d24
- **2026-11-02 21:29:13.051046**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 10
    - md5: f3a421f38ccaaf0fed543e9ccff884fb
- **2026-11-02 21:29:13.054424**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 5
    - md5: 3f255a12031364bf20836d42096d6b12
- **2026-11-02 21:29:13.337188**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: 09bc0f8ee0c1455a605dfe8d504051e8
- **2026-11-02 21:29:13.337604**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 34ba29f107e0f4abae9f9e1b38c5c801
- **2026-11-02 21:29:13.337936**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 022f07eb1c5bd8b38c1a7b643de49591
- **2026-11-02 21:29:13.338342**: wrote 'zh_freqcontrast_chinese_psychopy.csv'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.csv
    - rows: NA
    - md5: 0bdeeed7b653a0a854572711cb3daef9
- **2026-11-02 21:29:13.338658**: wrote 'zh_freqcontrast_chinese_opensesame.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-11-02 21:29:13.33899**: wrote 'zh_freqcontrast_chinese_opensesame_text.csv'
    - path: output/experiments/zh_freqcontrast_chinese_opensesame_text.csv
    - rows: NA
    - md5: cb48f54cc0bad839e8a2503b476e528a
- **2026-11-02 21:29:13.390418**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: c0ee1b6d0aafa43d8e3af2edee2fb10b
- **2026-11-02 21:29:13.390809**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: fc284cc0db8f14628cc7d7cc413f41d2
