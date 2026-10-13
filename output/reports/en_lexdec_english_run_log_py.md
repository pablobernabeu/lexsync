# lexsync run log: en_lexdec

- Engine: Python 3.13.7
- Started: 2026-10-13T22:49:29
- Finished: 2026-10-13T22:49:36

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T22:49:29**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13T22:49:31**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T22:49:31**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13T22:49:31**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-13T22:49:33**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-13T22:49:34**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-13T22:49:35**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-13T22:49:35**: equivalence pseudoword vs word on 'bigram_freq': d = -0.97 [-1.29, -0.65], TOST p = 0.9941 (not shown equivalent)
- **2026-10-13T22:49:35**: equivalence pseudoword vs word on 'n_density': d = 0.01 [-0.30, 0.31], TOST p = 0.0039 (equivalent)
- **2026-10-13T22:49:35**: equivalence pseudoword vs word on 'old20': d = -0.04 [-0.34, 0.27], TOST p = 0.0063 (equivalent)
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_stimuli_py.csv'
    - path: output\stimuli\en_lexdec_english_stimuli_py.csv
    - rows: 120
    - md5: 904a03751c491ba9979823cf6ad1aca4
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_descriptives_py.csv'
    - path: output\reports\en_lexdec_english_descriptives_py.csv
    - rows: 8
    - md5: f703a5d9fc95ab14d7c8b7b81238ee62
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_comparisons_py.csv'
    - path: output\reports\en_lexdec_english_comparisons_py.csv
    - rows: 4
    - md5: 1351a5c0c730e41e247d8ee90369ac23
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_psychopy.py'
    - path: output\experiments\en_lexdec_english_psychopy.py
    - rows: None
    - md5: bef9cd62bd66ea210882be90cb4fb6e0
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english.osexp'
    - path: output\experiments\en_lexdec_english.osexp
    - rows: None
    - md5: e9510b64bc1edd26aa644f36b9bcd7c1
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english.html'
    - path: output\experiments\en_lexdec_english.html
    - rows: None
    - md5: d443889251ce38aa0b34726c10b78e70
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output\experiments\en_lexdec_english_psychopy.csv
    - rows: None
    - md5: 5ad87de0d5fb738c0c4b1217a34e2bed
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output\experiments\en_lexdec_english_opensesame.csv
    - rows: None
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-13T22:49:35**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output\experiments\en_lexdec_english_opensesame_text.csv
    - rows: None
    - md5: 850a6fc2a8c8cccde050f67c41e70fa7
- **2026-10-13T22:49:36**: wrote 'en_lexdec_english_datasheet_py.json'
    - path: output\reports\en_lexdec_english_datasheet_py.json
    - rows: None
    - md5: 2279f652ae0b8d58e42a6ef49dd811e4
- **2026-10-13T22:49:36**: wrote 'en_lexdec_english_datasheet_py.md'
    - path: output\reports\en_lexdec_english_datasheet_py.md
    - rows: None
    - md5: b7ab35d9884af7fa75101638e64c6608
