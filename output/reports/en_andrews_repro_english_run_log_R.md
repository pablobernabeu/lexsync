# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:27.594731
- Finished: 2026-08-01 00:33:28.573978

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01 00:33:27.597697**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-01 00:33:28.228136**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-01 00:33:28.234934**: pool after filters: 7960 words
    - pool: 7960
- **2026-08-01 00:33:28.268225**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-08-01 00:33:28.295729**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-08-01 00:33:28.299753**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-08-01 00:33:28.303145**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.306004**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.308776**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-08-01 00:33:28.311734**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.314501**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-08-01 00:33:28.316811**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-08-01 00:33:28.319115**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-08-01 00:33:28.321784**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.324532**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.327647**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:28.357634**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-08-01 00:33:28.373392**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-08-01 00:33:28.388571**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: 390f721f1b9fa3432c142dc7fb2fca65
- **2026-08-01 00:33:28.464201**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: b7e7273ccd9753297f641c16c614c218
- **2026-08-01 00:33:28.471533**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 9955679f812b23c39e8cf678aa78bbf3
- **2026-08-01 00:33:28.480868**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: f153f52ed10b8d97ae42de5b9a310b07
- **2026-08-01 00:33:28.556883**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 8d94188afcebe0bb75c6e605eaca6fb3
- **2026-08-01 00:33:28.565685**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 00cb01bc736c1e2f8bef5255854d8cc5
