# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-10-02 16:40:12.333704
- Finished: 2026-10-02 16:41:23.759432

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:40:12.526857**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 16:40:35.078133**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:40:35.53989**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-02 16:40:39.196144**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-02 16:40:42.38863**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-02 16:40:42.518771**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-10-02 16:40:42.891125**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:43.020436**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:43.128865**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-02 16:40:43.307545**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:43.486351**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-10-02 16:40:43.677196**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-10-02 16:40:43.851812**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-02 16:40:44.123113**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:44.508234**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:44.693357**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:40:48.9244**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-02 16:40:51.264962**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-02 16:40:52.542507**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-02 16:41:19.752876**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: b7e7273ccd9753297f641c16c614c218
- **2026-10-02 16:41:19.832857**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 54937d8c37ac410d9f31640a26fe7f75
- **2026-10-02 16:41:20.006303**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: 46df0b0aa8f2f55c0a09986a14b0186b
- **2026-10-02 16:41:23.286605**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 20089405e6186de3f674187ff416ea0f
- **2026-10-02 16:41:23.531549**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 00f591865431ab9b589494ac83f0cd4e
