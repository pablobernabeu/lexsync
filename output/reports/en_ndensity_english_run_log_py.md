# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-09T09:53:38
- Finished: 2026-10-09T09:53:40

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T09:53:38**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09T09:53:39**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T09:53:39**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-09T09:53:39**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = -0.83 [-1.10, -0.56], TOST p = 0.9802 (not shown equivalent)
- **2026-10-09T09:53:39**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.13 [-0.13, 0.39], TOST p = 0.0101 (equivalent)
- **2026-10-09T09:53:39**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-09T09:53:39**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 12
    - md5: 2b6ccf7a1eaef3521f22084cfa042738
- **2026-10-09T09:53:39**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 6
    - md5: a41c6f1d22cdfbf077198045ace08eb5
- **2026-10-09T09:53:39**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 644b7f22a01b99b7ca0d94c040cf0be5
- **2026-10-09T09:53:39**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: a9903c46919cefb72c1a564b6407ba91
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: e1c3bc4d5c84b8de9ec8aa08b25c677e
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output\experiments\en_ndensity_english_psychopy.csv
    - rows: None
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output\experiments\en_ndensity_english_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output\experiments\en_ndensity_english_opensesame_text.csv
    - rows: None
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: fba286f38220e8b123d2bdbc569e57da
- **2026-10-09T09:53:40**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: 0ba9b9eadc4fd7615dd794e83b6f71f5
