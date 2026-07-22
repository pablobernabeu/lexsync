# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-07-23T00:27:46
- Finished: 2026-07-23T00:27:47

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-23T00:27:46**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-23T00:27:46**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-23T00:27:46**: pool after filters: 4002 words
    - pool: 4002
- **2026-07-23T00:27:47**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-23T00:27:47**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-23T00:27:47**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-07-23T00:27:47**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.87, 2.39], TOST p = 1.0 (not shown equivalent)
- **2026-07-23T00:27:47**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.68, -2.16], TOST p = 1.0 (not shown equivalent)
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: 2a768da8477792ab93fd1762379c8a70
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 8
    - md5: ce8b393459ad6150dda6585e1fda6baa
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 4
    - md5: fcbb11893b565a5259b3df2c0c414317
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 459468586284d7a299fc36abd9cd75e4
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: c31a6676121785fe10445abaaa379216
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: b3340b7f3285279632c59bc1b1c2cb7e
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: e776534f2f004f33bd73af2212dec3a9
- **2026-07-23T00:27:47**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: 9301bfba109e9aaeef3ad482f8931cc5
