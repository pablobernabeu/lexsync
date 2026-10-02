# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-10-03 00:24:05.78237
- Finished: 2026-10-03 00:25:21.058439

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:24:06.41877**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:24:27.831241**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 00:24:28.031868**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-03 00:24:28.78898**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-03 00:24:29.815959**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-03 00:24:29.891392**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-10-03 00:24:29.904376**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:30.02817**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:30.121025**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-03 00:24:30.158066**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:30.673489**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-10-03 00:24:30.902876**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-10-03 00:24:31.056291**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-03 00:24:31.226642**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:31.39061**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:31.814228**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 00:24:38.060945**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-03 00:24:40.44285**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-03 00:24:41.372938**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-03 00:25:15.812142**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: b7e7273ccd9753297f641c16c614c218
- **2026-10-03 00:25:16.078131**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 54937d8c37ac410d9f31640a26fe7f75
- **2026-10-03 00:25:16.471773**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: 46df0b0aa8f2f55c0a09986a14b0186b
- **2026-10-03 00:25:20.048531**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 603be5550dc1366d721b062e297ad93c
- **2026-10-03 00:25:20.611084**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 9184faaed16c771c6b02a22615fde694
