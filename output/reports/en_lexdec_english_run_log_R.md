# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-11-02 21:28:32.615382
- Finished: 2026-11-02 21:28:36.606653

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-11-02 21:28:32.616344**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-11-02 21:28:33.392088**: lexicon loaded: 30000 words
    - words: 30000
- **2026-11-02 21:28:33.402064**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-11-02 21:28:33.408775**: pool after filters: 6767 words
    - pool: 6767
- **2026-11-02 21:28:33.701831**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-11-02 21:28:35.182113**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-11-02 21:28:35.965794**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-11-02 21:28:35.966177**: equivalence pseudoword vs word on 'bigram_freq': d = -0.97 [-1.29, -0.65], TOST p = 0.994 (not shown equivalent)
- **2026-11-02 21:28:35.966521**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.31], TOST p = 0.004 (equivalent)
- **2026-11-02 21:28:35.96684**: equivalence pseudoword vs word on 'old20': d = -0.04 [-0.34, 0.26], TOST p = 0.006 (equivalent)
- **2026-11-02 21:28:35.998082**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: 904a03751c491ba9979823cf6ad1aca4
- **2026-11-02 21:28:36.001767**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: f703a5d9fc95ab14d7c8b7b81238ee62
- **2026-11-02 21:28:36.004711**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 1351a5c0c730e41e247d8ee90369ac23
- **2026-11-02 21:28:36.248934**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 75f1ad736fd76023d869da69e2889305
- **2026-11-02 21:28:36.249428**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: ed6151bea7c9f36e9dfa191b63af35ac
- **2026-11-02 21:28:36.249814**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 473b53d1f524a0747214c1e6fb4eecb1
- **2026-11-02 21:28:36.250207**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 5ad87de0d5fb738c0c4b1217a34e2bed
- **2026-11-02 21:28:36.250544**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-11-02 21:28:36.250894**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 850a6fc2a8c8cccde050f67c41e70fa7
- **2026-11-02 21:28:36.605507**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 5054a6c241f48c3c6f0185f4ef5182a2
- **2026-11-02 21:28:36.605871**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: ac27d33651da0c7dbe8472f0f13d88e3
