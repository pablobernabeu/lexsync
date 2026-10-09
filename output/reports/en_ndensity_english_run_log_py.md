# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-09T11:51:13
- Finished: 2026-10-09T11:51:15

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T11:51:13**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-09T11:51:14**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T11:51:14**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-09T11:51:14**: pool after filters: 3879 words
    - pool: 3879
- **2026-10-09T11:51:15**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.49 [3.07, 3.90], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.39 [-2.73, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = -0.53 [-0.79, -0.26], TOST p = 0.5696 (not shown equivalent)
- **2026-10-09T11:51:15**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.45 [0.19, 0.72], TOST p = 0.3838 (not shown equivalent)
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: f93d1fb38f57713595f4140a1ce50d8a
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 12
    - md5: b3045466f75245c03cff89c9dde23793
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 6
    - md5: ec31d63368d293ae676bedfc812c07de
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 644b7f22a01b99b7ca0d94c040cf0be5
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: a9903c46919cefb72c1a564b6407ba91
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: be0efe99ba18175afad64e4cd658120b
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output\experiments\en_ndensity_english_psychopy.csv
    - rows: None
    - md5: 5ed720a934953a338c93dd23c9d32689
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output\experiments\en_ndensity_english_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output\experiments\en_ndensity_english_opensesame_text.csv
    - rows: None
    - md5: 6f2a183b8e1278ecd633f1443ed1c20f
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: ddb2002f806b80d0e80f23c732954a45
- **2026-10-09T11:51:15**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: 1d894d3525835cdac0c72f1f1f8b2da7
