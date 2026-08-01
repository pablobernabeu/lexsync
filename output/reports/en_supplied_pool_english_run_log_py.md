# lexsync run log: en_supplied_pool

- Engine: Python 3.13.7
- Started: 2026-08-01T14:40:47
- Finished: 2026-08-01T14:40:47

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01T14:40:47**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-08-01T14:40:47**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-08-01T14:40:47**: pool after filters: 131 words
    - pool: 131
- **2026-08-01T14:40:47**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-08-01T14:40:47**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.1121 (not shown equivalent)
- **2026-08-01T14:40:47**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [3.00, 4.06], TOST p = 1.0 (not shown equivalent)
- **2026-08-01T14:40:47**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.1245 (not shown equivalent)
- **2026-08-01T14:40:47**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.2093 (not shown equivalent)
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_stimuli_py.csv'
    - path: output\stimuli\en_supplied_pool_english_stimuli_py.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_descriptives_py.csv'
    - path: output\reports\en_supplied_pool_english_descriptives_py.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_comparisons_py.csv'
    - path: output\reports\en_supplied_pool_english_comparisons_py.csv
    - rows: 4
    - md5: a6ed40f01c6a55726fccd8f520ab8333
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output\experiments\en_supplied_pool_english_psychopy.py
    - rows: None
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english.osexp'
    - path: output\experiments\en_supplied_pool_english.osexp
    - rows: None
    - md5: 4bfa2f18cc3a5e7ef39a9f140aa6154e
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english.html'
    - path: output\experiments\en_supplied_pool_english.html
    - rows: None
    - md5: 049942042c0f160bef7a4b9b3a37b7ae
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_datasheet_py.json'
    - path: output\reports\en_supplied_pool_english_datasheet_py.json
    - rows: None
    - md5: a1e7870926c5a8c97b3dcb0ded36ca78
- **2026-08-01T14:40:47**: wrote 'en_supplied_pool_english_datasheet_py.md'
    - path: output\reports\en_supplied_pool_english_datasheet_py.md
    - rows: None
    - md5: e5b2e628681180db7a75646077fc7824
