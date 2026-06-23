# lexsync run log: en_andrews_repro

- Engine: R 4.6.0
- Started: 2026-06-23 10:18:47.787069
- Finished: 2026-06-23 10:18:48.982994

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:18:47.794505**: loading lexicon 'corpora/derived/en.csv'
- **2026-06-23 10:18:48.663253**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-23 10:18:48.670528**: pool after filters: 7960 words
    - pool: 7960
- **2026-06-23 10:18:48.694881**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-06-23 10:18:48.716318**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-06-23 10:18:48.721255**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.124 (not shown equivalent)
- **2026-06-23 10:18:48.725844**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.730011**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.734424**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-06-23 10:18:48.73836**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.74313**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.121 (not shown equivalent)
- **2026-06-23 10:18:48.746731**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.122 (not shown equivalent)
- **2026-06-23 10:18:48.750592**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.46, 0.66], TOST p = 0.119 (not shown equivalent)
- **2026-06-23 10:18:48.754376**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.757702**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.760791**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:48.779719**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: 0873c199e387e0ea14a76a9f76f2fbf8
- **2026-06-23 10:18:48.797276**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-06-23 10:18:48.810935**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: d6a7c6a341f8ae7e17fa1b8782996acd
- **2026-06-23 10:18:48.888696**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: 5b8af261f516b709efca22d693597741
- **2026-06-23 10:18:48.898171**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 0ead8815382a5ac245b9c92cbe0e5060
- **2026-06-23 10:18:48.904817**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: bfca933513b556bf1c6f8a1b573ae512
- **2026-06-23 10:18:48.966075**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: 7b76774ac55b724ac53d14337a99d916
- **2026-06-23 10:18:48.974384**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: 007e186f3c880700f442de78e738d7c1
