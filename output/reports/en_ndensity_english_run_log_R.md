# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-14 01:25:09.259378
- Finished: 2026-10-14 01:25:12.625673

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 01:25:09.263417**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 01:25:09.267601**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-14 01:25:10.384217**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 01:25:10.395881**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-14 01:25:10.441045**: pool after filters: 3879 words
    - pool: 3879
- **2026-10-14 01:25:11.573279**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-14 01:25:11.985345**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-14 01:25:11.98988**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-14 01:25:11.993053**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.49 [3.07, 3.90], TOST p = 1.000 (not shown equivalent)
- **2026-10-14 01:25:11.997769**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.39 [-2.73, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-14 01:25:12.001925**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = -0.53 [-0.79, -0.26], TOST p = 0.570 (not shown equivalent)
- **2026-10-14 01:25:12.006364**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.45 [0.19, 0.72], TOST p = 0.384 (not shown equivalent)
- **2026-10-14 01:25:12.044402**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: f93d1fb38f57713595f4140a1ce50d8a
- **2026-10-14 01:25:12.060087**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 12
    - md5: b3045466f75245c03cff89c9dde23793
- **2026-10-14 01:25:12.076061**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 6
    - md5: ec31d63368d293ae676bedfc812c07de
- **2026-10-14 01:25:12.360875**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 24d3714296a80e8434bc94e15d8eb9ba
- **2026-10-14 01:25:12.371952**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 7e6996f72bdb0ac1b6b8907896ec6521
- **2026-10-14 01:25:12.379981**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 3cd72f2f2a052836cffa0ee34972fa4c
- **2026-10-14 01:25:12.39391**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 5ed720a934953a338c93dd23c9d32689
- **2026-10-14 01:25:12.403822**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-14 01:25:12.412813**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: 6f2a183b8e1278ecd633f1443ed1c20f
- **2026-10-14 01:25:12.594707**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: b94b7f428c6b7672490d9233f1c5170b
- **2026-10-14 01:25:12.611716**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: b456206dc70fce0b5e62a191b4e3a2e3
