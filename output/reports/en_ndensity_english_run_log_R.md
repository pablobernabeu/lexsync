# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-13 18:17:29.841616
- Finished: 2026-10-13 18:17:38.019286

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:17:29.857179**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:17:29.864897**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 18:17:32.506586**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 18:17:32.917986**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 18:17:32.945083**: pool after filters: 3879 words
    - pool: 3879
- **2026-10-13 18:17:35.687602**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-13 18:17:36.068251**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-13 18:17:36.075884**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-13 18:17:36.082664**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.49 [3.07, 3.90], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 18:17:36.088365**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.39 [-2.73, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 18:17:36.094773**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = -0.53 [-0.79, -0.26], TOST p = 0.570 (not shown equivalent)
- **2026-10-13 18:17:36.102651**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.45 [0.19, 0.72], TOST p = 0.384 (not shown equivalent)
- **2026-10-13 18:17:36.607009**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: f93d1fb38f57713595f4140a1ce50d8a
- **2026-10-13 18:17:36.648609**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 12
    - md5: b3045466f75245c03cff89c9dde23793
- **2026-10-13 18:17:36.687705**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 6
    - md5: ec31d63368d293ae676bedfc812c07de
- **2026-10-13 18:17:37.545106**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 03786742d2fec69c8aa6ea5164c02f31
- **2026-10-13 18:17:37.567538**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: d97b29297419238e41781b88f30783c2
- **2026-10-13 18:17:37.581415**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 9db137ddf5beab175c3064dedddbce79
- **2026-10-13 18:17:37.603726**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 5ed720a934953a338c93dd23c9d32689
- **2026-10-13 18:17:37.61711**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-13 18:17:37.635876**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: 6f2a183b8e1278ecd633f1443ed1c20f
- **2026-10-13 18:17:37.98841**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 7029e1f99785ffbc2043955ed4612916
- **2026-10-13 18:17:38.005252**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: b456206dc70fce0b5e62a191b4e3a2e3
