# lexsync run log: en_andrews_repro

- Engine: Python 3.13.7
- Started: 2026-06-13T23:55:16
- Finished: 2026-06-13T23:55:18

## Run metadata

- design: en_andrews_repro
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13T23:55:16** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13T23:55:17** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13T23:55:17** -- pool after filters: 7960 words
    - pool: 7960
- **2026-06-13T23:55:17** -- matched 72 items across 4 conditions
    - conditions: HF_largeN, HF_smallN, LF_largeN, LF_smallN
- **2026-06-13T23:55:18** -- equivalence HF_smallN vs HF_largeN on 'length': d = -0.21 [-0.77, 0.36], TOST p = 0.192 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence HF_smallN vs HF_largeN on 'frequency': d = -0.11 [-0.67, 0.46], TOST p = 0.1238 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence HF_smallN vs HF_largeN on 'n_density': d = 3.19 [2.63, 3.75], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence HF_smallN vs HF_largeN on 'old20': d = -5.76 [-6.32, -5.19], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_largeN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_largeN vs HF_largeN on 'frequency': d = 4.71 [4.15, 5.28], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_largeN vs HF_largeN on 'n_density': d = 0.10 [-0.46, 0.67], TOST p = 0.1208 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_largeN vs HF_largeN on 'old20': d = 0.10 [-0.46, 0.67], TOST p = 0.1218 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_smallN vs HF_largeN on 'length': d = 0.10 [-0.47, 0.66], TOST p = 0.1186 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_smallN vs HF_largeN on 'frequency': d = 5.18 [4.62, 5.75], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_smallN vs HF_largeN on 'n_density': d = 3.29 [2.73, 3.85], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- equivalence LF_smallN vs HF_largeN on 'old20': d = -5.91 [-6.48, -5.35], TOST p = 1.0 (not shown equivalent)
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_stimuli_py.csv'
    - path: output\stimuli\en_andrews_repro_english_stimuli_py.csv
    - rows: 72
    - md5: fdeabeedd9f42f75fd3e073309222f08
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_descriptives_py.csv'
    - path: output\reports\en_andrews_repro_english_descriptives_py.csv
    - rows: 16
    - md5: 727dcfa052cdbbb4e5cc3a9abe6d9449
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_comparisons_py.csv'
    - path: output\reports\en_andrews_repro_english_comparisons_py.csv
    - rows: 12
    - md5: b878d151ff18e059ac5cc2dd18bb9dcf
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_psychopy.py'
    - path: output\experiments\en_andrews_repro_english_psychopy.py
    - rows: None
    - md5: 478020bff693708ce535fdf7b9f0a5fd
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english.osexp'
    - path: output\experiments\en_andrews_repro_english.osexp
    - rows: None
    - md5: 5719ab9207e280638f2b39f4b8d43a71
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english.html'
    - path: output\experiments\en_andrews_repro_english.html
    - rows: None
    - md5: 6823ddb3aefa37e7c07df6849176ba02
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_datasheet_py.json'
    - path: output\reports\en_andrews_repro_english_datasheet_py.json
    - rows: None
    - md5: 85dfea0afecbb4ac581c2faedbe51e75
- **2026-06-13T23:55:18** -- wrote 'en_andrews_repro_english_datasheet_py.md'
    - path: output\reports\en_andrews_repro_english_datasheet_py.md
    - rows: None
    - md5: a8a9b531c5245ce3bcbe3d374b43d47a
