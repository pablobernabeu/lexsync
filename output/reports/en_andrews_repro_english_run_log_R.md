# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-09-24 16:59:43.270155
- Finished: 2026-09-24 16:59:45.056688

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 16:59:43.289595**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-24 16:59:44.410019**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-24 16:59:44.424008**: pool after filters: 7960 words
    - pool: 7960
- **2026-09-24 16:59:44.494695**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-09-24 16:59:44.546465**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-09-24 16:59:44.554535**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-09-24 16:59:44.558034**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.563161**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.568144**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-09-24 16:59:44.571987**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.577051**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-09-24 16:59:44.581225**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-09-24 16:59:44.586212**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-09-24 16:59:44.590629**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.594361**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.599709**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:44.640229**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-09-24 16:59:44.662998**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-09-24 16:59:44.683025**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-09-24 16:59:44.834833**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: b7e7273ccd9753297f641c16c614c218
- **2026-09-24 16:59:44.84579**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 9955679f812b23c39e8cf678aa78bbf3
- **2026-09-24 16:59:44.856945**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: 46df0b0aa8f2f55c0a09986a14b0186b
- **2026-09-24 16:59:45.032952**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: e6fde688965065422e88c308af02d7bd
- **2026-09-24 16:59:45.045015**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 4b69668c6880dd4b77c5c7fe0e22cba4
