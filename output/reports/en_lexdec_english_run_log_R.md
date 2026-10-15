# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-15 04:44:33.229194
- Finished: 2026-10-15 04:44:42.906481

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 04:44:33.23686**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-15 04:44:35.320573**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 04:44:35.34443**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-15 04:44:35.36266**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-15 04:44:36.225846**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-15 04:44:40.540219**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-15 04:44:41.770625**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-15 04:44:41.776832**: equivalence pseudoword vs word on 'bigram_freq': d = -0.97 [-1.29, -0.65], TOST p = 0.994 (not shown equivalent)
- **2026-10-15 04:44:41.782101**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-15 04:44:41.787223**: equivalence pseudoword vs word on 'old20': d = -0.04 [-0.34, 0.26], TOST p = 0.006 (equivalent)
- **2026-10-15 04:44:41.849234**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: 904a03751c491ba9979823cf6ad1aca4
- **2026-10-15 04:44:41.873022**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: f703a5d9fc95ab14d7c8b7b81238ee62
- **2026-10-15 04:44:41.894704**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 1351a5c0c730e41e247d8ee90369ac23
- **2026-10-15 04:44:42.31216**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: ef7254ee2533e807c7042528071ad314
- **2026-10-15 04:44:42.324319**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: ed6151bea7c9f36e9dfa191b63af35ac
- **2026-10-15 04:44:42.336894**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: a7709adeb91431c3b303eab03fddb131
- **2026-10-15 04:44:42.352261**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 5ad87de0d5fb738c0c4b1217a34e2bed
- **2026-10-15 04:44:42.362777**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-15 04:44:42.37208**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 850a6fc2a8c8cccde050f67c41e70fa7
- **2026-10-15 04:44:42.88426**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: c69f060ff690b9336ffa7d0c621e002f
- **2026-10-15 04:44:42.89663**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 2bd1258e250949aab3323563408db510
