# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-10-09 05:22:44.36748
- Finished: 2026-10-09 05:22:50.362664

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:22:44.385019**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 05:22:46.077006**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 05:22:46.177283**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-09 05:22:46.363636**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-09 05:22:46.592408**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-09 05:22:46.604629**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-10-09 05:22:46.621623**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.649839**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.66482**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-09 05:22:46.673428**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.683566**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-10-09 05:22:46.694297**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-10-09 05:22:46.70043**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-09 05:22:46.715344**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.732374**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.749364**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:22:46.880276**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-09 05:22:47.006234**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-09 05:22:47.055507**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-09 05:22:49.407564**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: 8d500634ba47e885e9fcfd83ea095be9
- **2026-10-09 05:22:49.437399**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: fe2721ed0fbebd52ce1a466df4d04b40
- **2026-10-09 05:22:49.463469**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: ed45b8bfaf0adc7e5cb6398f3304c573
- **2026-10-09 05:22:49.487739**: wrote 'en_andrews_repro_english_psychopy.csv'
    - path: output/experiments/en_andrews_repro_english_psychopy.csv
    - rows: NA
    - md5: 8710243cdf6f49100dc6e5d8efd7e03c
- **2026-10-09 05:22:49.505596**: wrote 'en_andrews_repro_english_opensesame.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame.csv
    - rows: NA
    - md5: 8ed2d40076b9d193c0ae26c859cee534
- **2026-10-09 05:22:49.534044**: wrote 'en_andrews_repro_english_opensesame_text.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame_text.csv
    - rows: NA
    - md5: a26002517937b93ffbb6efd2433cd3d3
- **2026-10-09 05:22:50.208695**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 3a865c21afb64d4e5354aac936e5e22d
- **2026-10-09 05:22:50.264316**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 3277680c9865b666df434bd9fdf89cf6
