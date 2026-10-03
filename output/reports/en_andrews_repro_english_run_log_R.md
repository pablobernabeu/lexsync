# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-10-03 13:08:10.795246
- Finished: 2026-10-03 13:08:32.519451

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 13:08:11.182964**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 13:08:17.503989**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 13:08:17.598703**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-03 13:08:18.094019**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-03 13:08:18.605625**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-03 13:08:18.661277**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-10-03 13:08:18.695496**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:18.71957**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:18.736207**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-03 13:08:18.76002**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:18.796681**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-10-03 13:08:18.831673**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-10-03 13:08:18.841757**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-03 13:08:18.927859**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:18.938567**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:18.956738**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:08:20.643217**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-03 13:08:21.224141**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-03 13:08:21.79978**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-03 13:08:30.36241**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: e2ba954eb1fe649bfac0a1834e575f9f
- **2026-10-03 13:08:30.450719**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 54937d8c37ac410d9f31640a26fe7f75
- **2026-10-03 13:08:30.498231**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: f924d6c7a0c47fa4ff57e91beab8c893
- **2026-10-03 13:08:30.672439**: wrote 'en_andrews_repro_english_psychopy.csv'
    - path: output/experiments/en_andrews_repro_english_psychopy.csv
    - rows: NA
    - md5: 8710243cdf6f49100dc6e5d8efd7e03c
- **2026-10-03 13:08:30.922674**: wrote 'en_andrews_repro_english_opensesame.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame.csv
    - rows: NA
    - md5: 8ed2d40076b9d193c0ae26c859cee534
- **2026-10-03 13:08:31.10425**: wrote 'en_andrews_repro_english_opensesame_text.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame_text.csv
    - rows: NA
    - md5: a26002517937b93ffbb6efd2433cd3d3
- **2026-10-03 13:08:32.365767**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: f0bb78ae5bab76a249cb8957727b88b6
- **2026-10-03 13:08:32.455688**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 9184faaed16c771c6b02a22615fde694
