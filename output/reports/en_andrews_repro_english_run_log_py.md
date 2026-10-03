# lexsync run log: en_andrews_repro

- Engine: Python 3.13.7
- Started: 2026-10-03T11:30:34
- Finished: 2026-10-03T11:30:38

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03T11:30:34**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03T11:30:35**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03T11:30:35**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-03T11:30:35**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-03T11:30:35**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.1238 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.1208 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.1218 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:35**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english_stimuli_py.csv'
    - path: output\stimuli\en_andrews_repro_english_stimuli_py.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english_descriptives_py.csv'
    - path: output\reports\en_andrews_repro_english_descriptives_py.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english_comparisons_py.csv'
    - path: output\reports\en_andrews_repro_english_comparisons_py.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output\experiments\en_andrews_repro_english_psychopy.py
    - rows: None
    - md5: e2ba954eb1fe649bfac0a1834e575f9f
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english.osexp'
    - path: output\experiments\en_andrews_repro_english.osexp
    - rows: None
    - md5: 54937d8c37ac410d9f31640a26fe7f75
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english.html'
    - path: output\experiments\en_andrews_repro_english.html
    - rows: None
    - md5: f924d6c7a0c47fa4ff57e91beab8c893
- **2026-10-03T11:30:36**: wrote 'en_andrews_repro_english_psychopy.csv'
    - path: output\experiments\en_andrews_repro_english_psychopy.csv
    - rows: None
    - md5: 8710243cdf6f49100dc6e5d8efd7e03c
- **2026-10-03T11:30:37**: wrote 'en_andrews_repro_english_opensesame.csv'
    - path: output\experiments\en_andrews_repro_english_opensesame.csv
    - rows: None
    - md5: 8ed2d40076b9d193c0ae26c859cee534
- **2026-10-03T11:30:37**: wrote 'en_andrews_repro_english_opensesame_text.csv'
    - path: output\experiments\en_andrews_repro_english_opensesame_text.csv
    - rows: None
    - md5: a26002517937b93ffbb6efd2433cd3d3
- **2026-10-03T11:30:38**: wrote 'en_andrews_repro_english_datasheet_py.json'
    - path: output\reports\en_andrews_repro_english_datasheet_py.json
    - rows: None
    - md5: bcc35a435a7433194b91a57be1750fd0
- **2026-10-03T11:30:38**: wrote 'en_andrews_repro_english_datasheet_py.md'
    - path: output\reports\en_andrews_repro_english_datasheet_py.md
    - rows: None
    - md5: bc76709414d909bd0821a2f199e4bcbd
