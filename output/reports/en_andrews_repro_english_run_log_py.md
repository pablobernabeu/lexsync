# lexsync run log: en_andrews_repro

- Engine: Python 3.13.7
- Started: 2026-07-31T22:42:01
- Finished: 2026-07-31T22:42:02

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31T22:42:01**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31T22:42:02**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31T22:42:02**: pool after filters: 7960 words
    - pool: 7960
- **2026-07-31T22:42:02**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-07-31T22:42:02**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.1238 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.1208 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.1218 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.0 (not shown equivalent)
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_stimuli_py.csv'
    - path: output\stimuli\en_andrews_repro_english_stimuli_py.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_descriptives_py.csv'
    - path: output\reports\en_andrews_repro_english_descriptives_py.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_comparisons_py.csv'
    - path: output\reports\en_andrews_repro_english_comparisons_py.csv
    - rows: 12
    - md5: 390f721f1b9fa3432c142dc7fb2fca65
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output\experiments\en_andrews_repro_english_psychopy.py
    - rows: None
    - md5: b7e7273ccd9753297f641c16c614c218
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english.osexp'
    - path: output\experiments\en_andrews_repro_english.osexp
    - rows: None
    - md5: 9955679f812b23c39e8cf678aa78bbf3
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english.html'
    - path: output\experiments\en_andrews_repro_english.html
    - rows: None
    - md5: f153f52ed10b8d97ae42de5b9a310b07
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_datasheet_py.json'
    - path: output\reports\en_andrews_repro_english_datasheet_py.json
    - rows: None
    - md5: 102cf9bdc2f387a299c54f0dd661a184
- **2026-07-31T22:42:02**: wrote 'en_andrews_repro_english_datasheet_py.md'
    - path: output\reports\en_andrews_repro_english_datasheet_py.md
    - rows: None
    - md5: f666f7cf1a3cdc81f674ca47520ed2fc
