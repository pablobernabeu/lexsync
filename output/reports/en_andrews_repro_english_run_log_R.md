# lexsync run log: en_andrews_repro

- Engine: R 4.6.1
- Started: 2026-10-09 05:57:29.372414
- Finished: 2026-10-09 05:57:33.177132

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:57:29.381193**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 05:57:31.023665**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 05:57:31.107834**: pool after filters: 7960 words
    - pool: 7960
- **2026-10-09 05:57:31.299754**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-10-09 05:57:31.505226**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-10-09 05:57:31.513528**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-10-09 05:57:31.520941**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.34, 4.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.527902**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-7.03, -4.48], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.534151**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-09 05:57:31.539713**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [3.62, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.546001**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-10-09 05:57:31.55447**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-10-09 05:57:31.560365**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-10-09 05:57:31.565684**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.01, 6.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.577057**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.42, 4.15], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.585179**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-7.22, -4.61], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:57:31.657963**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-10-09 05:57:31.721439**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-10-09 05:57:31.74716**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: a1969f7e75fed9153a321076b3f170f5
- **2026-10-09 05:57:32.569365**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: 8d500634ba47e885e9fcfd83ea095be9
- **2026-10-09 05:57:32.58702**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: fe2721ed0fbebd52ce1a466df4d04b40
- **2026-10-09 05:57:32.625347**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: ed45b8bfaf0adc7e5cb6398f3304c573
- **2026-10-09 05:57:32.648949**: wrote 'en_andrews_repro_english_psychopy.csv'
    - path: output/experiments/en_andrews_repro_english_psychopy.csv
    - rows: NA
    - md5: 8710243cdf6f49100dc6e5d8efd7e03c
- **2026-10-09 05:57:32.659076**: wrote 'en_andrews_repro_english_opensesame.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame.csv
    - rows: NA
    - md5: 8ed2d40076b9d193c0ae26c859cee534
- **2026-10-09 05:57:32.672131**: wrote 'en_andrews_repro_english_opensesame_text.csv'
    - path: output/experiments/en_andrews_repro_english_opensesame_text.csv
    - rows: NA
    - md5: a26002517937b93ffbb6efd2433cd3d3
- **2026-10-09 05:57:33.152897**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: dd42daf02074d35fae4f9766bb76bd9d
- **2026-10-09 05:57:33.166492**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: c07afea55f2a6509a15a13c9edf72b91
