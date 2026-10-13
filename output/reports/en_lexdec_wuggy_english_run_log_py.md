# lexsync run log: en_lexdec_wuggy

- Engine: Python 3.13.7
- Started: 2026-10-13T14:33:05
- Finished: 2026-10-13T14:33:15

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T14:33:05**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13T14:33:07**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T14:33:07**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13T14:33:07**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-13T14:33:11**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-13T14:33:13**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-10-13T14:33:14**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-13T14:33:14**: equivalence pseudoword vs word on 'bigram_freq': d = -1.04 [-1.36, -0.71], TOST p = 0.998 (not shown equivalent)
- **2026-10-13T14:33:14**: equivalence pseudoword vs word on 'n_density': d = 0.77 [0.45, 1.08], TOST p = 0.9258 (not shown equivalent)
- **2026-10-13T14:33:14**: equivalence pseudoword vs word on 'old20': d = -0.81 [-1.13, -0.50], TOST p = 0.9561 (not shown equivalent)
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_stimuli_py.csv'
    - path: output\stimuli\en_lexdec_wuggy_english_stimuli_py.csv
    - rows: 120
    - md5: ee8cb48ab37e9e22472854cb6f8fbf9d
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_descriptives_py.csv'
    - path: output\reports\en_lexdec_wuggy_english_descriptives_py.csv
    - rows: 8
    - md5: 85bd7825d15c68f8bc7ad8de3b5895b1
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_comparisons_py.csv'
    - path: output\reports\en_lexdec_wuggy_english_comparisons_py.csv
    - rows: 4
    - md5: 08897c0a60cc9f96cead7bfb196a8277
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output\experiments\en_lexdec_wuggy_english_psychopy.py
    - rows: None
    - md5: ea0c5c48e3e6274f3f12683dc2434809
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output\experiments\en_lexdec_wuggy_english.osexp
    - rows: None
    - md5: 469e39d61647c8f3f7256dee61682eeb
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english.html'
    - path: output\experiments\en_lexdec_wuggy_english.html
    - rows: None
    - md5: 22e8c2f98bd36420d52577f8c6e22c60
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output\experiments\en_lexdec_wuggy_english_psychopy.csv
    - rows: None
    - md5: f1ea635b0b98dfda8ca574e5e78e9d97
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output\experiments\en_lexdec_wuggy_english_opensesame.csv
    - rows: None
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output\experiments\en_lexdec_wuggy_english_opensesame_text.csv
    - rows: None
    - md5: 184d94f259c829775dc1dcaf38852fc6
- **2026-10-13T14:33:14**: wrote 'en_lexdec_wuggy_english_datasheet_py.json'
    - path: output\reports\en_lexdec_wuggy_english_datasheet_py.json
    - rows: None
    - md5: b166dc11c93eb4167bb921b94435b0b9
- **2026-10-13T14:33:15**: wrote 'en_lexdec_wuggy_english_datasheet_py.md'
    - path: output\reports\en_lexdec_wuggy_english_datasheet_py.md
    - rows: None
    - md5: fa4a2e9241b225768e0f63e68929fc82
