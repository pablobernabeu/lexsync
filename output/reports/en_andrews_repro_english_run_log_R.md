# lexsync run log: en_andrews_repro

- Engine: R 4.3.3
- Started: 2026-09-02 19:24:52.176578
- Finished: 2026-09-02 19:24:53.824889

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:24:52.177101**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:24:52.84855**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:24:52.892773**: pool after filters: 7960 words
    - pool: 7960
- **2026-09-02 19:24:53.060227**: matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-09-02 19:24:53.175947**: equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.1920 (not shown equivalent)
- **2026-09-02 19:24:53.176192**: equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.1238 (not shown equivalent)
- **2026-09-02 19:24:53.176333**: equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.176459**: equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.176579**: equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-09-02 19:24:53.17672**: equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.176861**: equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.1208 (not shown equivalent)
- **2026-09-02 19:24:53.176992**: equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.1218 (not shown equivalent)
- **2026-09-02 19:24:53.177146**: equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-09-02 19:24:53.177278**: equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.177413**: equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.177536**: equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:53.278418**: wrote 'en_andrews_repro_english_stimuli_R.csv'
    - path: output/stimuli/en_andrews_repro_english_stimuli_R.csv
    - rows: 72
    - md5: c4650ff6811e6808f2346b86b33e163a
- **2026-09-02 19:24:53.28519**: wrote 'en_andrews_repro_english_descriptives_R.csv'
    - path: output/reports/en_andrews_repro_english_descriptives_R.csv
    - rows: 16
    - md5: 674de8c9ac2bda476b3d4d489c2a42e2
- **2026-09-02 19:24:53.288985**: wrote 'en_andrews_repro_english_comparisons_R.csv'
    - path: output/reports/en_andrews_repro_english_comparisons_R.csv
    - rows: 12
    - md5: 390f721f1b9fa3432c142dc7fb2fca65
- **2026-09-02 19:24:53.532763**: wrote 'en_andrews_repro_english_psychopy.py'
    - path: output/experiments/en_andrews_repro_english_psychopy.py
    - rows: NA
    - md5: 70f5c625bd6fc89617fa16767b10cab3
- **2026-09-02 19:24:53.532998**: wrote 'en_andrews_repro_english.osexp'
    - path: output/experiments/en_andrews_repro_english.osexp
    - rows: NA
    - md5: 9955679f812b23c39e8cf678aa78bbf3
- **2026-09-02 19:24:53.533087**: wrote 'en_andrews_repro_english.html'
    - path: output/experiments/en_andrews_repro_english.html
    - rows: NA
    - md5: aa1ac1d2b8b7482a560ab08023c76f94
- **2026-09-02 19:24:53.806893**: wrote 'en_andrews_repro_english_datasheet_R.json'
    - path: output/reports/en_andrews_repro_english_datasheet_R.json
    - rows: NA
    - md5: e0c41540f5714049de1889967aeb18cc
- **2026-09-02 19:24:53.807209**: wrote 'en_andrews_repro_english_datasheet_R.md'
    - path: output/reports/en_andrews_repro_english_datasheet_R.md
    - rows: NA
    - md5: e981abef43daa5dbf04446247e531454
