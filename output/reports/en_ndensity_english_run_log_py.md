# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-08-01T14:40:33
- Finished: 2026-08-01T14:40:34

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01T14:40:33**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-01T14:40:33**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-01T14:40:33**: pool after filters: 4557 words
    - pool: 4557
- **2026-08-01T14:40:34**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-08-01T14:40:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-08-01T14:40:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-08-01T14:40:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0 (not shown equivalent)
- **2026-08-01T14:40:34**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0 (not shown equivalent)
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: 088cf6eb4cbf699c316e3ee784cdd6fa
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: 4076b521841cea60b0c3674c740117ac
- **2026-08-01T14:40:34**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: f2d0bb5321b442e67755d65788279135
