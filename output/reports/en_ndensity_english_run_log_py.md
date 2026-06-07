# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-06-08T00:19:11
- Finished: 2026-06-08T00:19:11

## Run metadata

- design: en_ndensity
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, frequency

## Steps

- **2026-06-08T00:19:11** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-08T00:19:11** -- lexicon loaded: 29998 words
    - words: 29998
- **2026-06-08T00:19:11** -- pool after filters: 4557 words
    - pool: 4557
- **2026-06-08T00:19:11** -- matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = -0.25, TOST p = 0.056 (not shown equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.15, TOST p = 0.0142 (equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.11, TOST p = 1.0 (not shown equivalent)
- **2026-06-08T00:19:11** -- equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.89, TOST p = 1.0 (not shown equivalent)
- **2026-06-08T00:19:11** -- wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: fa7f35d4d7942e3c480d28c59d1fed8a
- **2026-06-08T00:19:11** -- wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 597818d81cfc62e8069f683aeb7fe68f
- **2026-06-08T00:19:11** -- wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 85b7a8f7e89f7aaa4cd415d25f30afee
- **2026-06-08T00:19:11** -- wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: c29db3b7a22197db8eec937979d8ce65
- **2026-06-08T00:19:11** -- wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 46c4ab4a2ff889255b59e7b04fc638c8
