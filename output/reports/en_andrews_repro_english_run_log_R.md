# lexsync run log: en_andrews_repro

- Engine: R 4.6.0
- Started: 2026-07-06 08:56:31.528133
- Finished: 2026-07-06 08:56:33.191469

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06 08:56:31.538894**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-06 08:56:32.591689**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-06 08:56:32.607701**: pool after filters: 7960 words
    - pool: 7960
- **2026-07-06 08:56:32.661759**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-07-06 08:56:32.702349**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-07-06 08:56:32.710751**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-07-06 08:56:32.718963**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.725199**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.732526**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-07-06 08:56:32.737752**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.744853**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-07-06 08:56:32.752214**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-07-06 08:56:32.758359**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-07-06 08:56:32.765207**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.770986**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.777246**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 08:56:32.807273**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: 0873c199e387e0ea14a76a9f76f2fbf8
- **2026-07-06 08:56:32.833621**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-07-06 08:56:32.858977**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: 390f721f1b9fa3432c142dc7fb2fca65
- **2026-07-06 08:56:32.988868**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: 5b8af261f516b709efca22d693597741
- **2026-07-06 08:56:33.004118**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 0ead8815382a5ac245b9c92cbe0e5060
- **2026-07-06 08:56:33.016939**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: abb241e34288e1adc3a34613228d34e5
- **2026-07-06 08:56:33.164592**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 9549a51ba5bb769a5f01e0a913a44799
- **2026-07-06 08:56:33.17761**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 671ef852fe6ef163e8607c926c9d6b7b
