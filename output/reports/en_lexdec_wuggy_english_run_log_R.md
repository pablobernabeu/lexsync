# lexsync run log: en_lexdec_wuggy

- Engine: R 4.6.1
- Started: 2026-10-14 22:40:33.465122
- Finished: 2026-10-14 22:41:16.252135

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 22:40:33.567361**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-14 22:40:36.797566**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 22:40:36.978473**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-14 22:40:37.073335**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-14 22:40:38.366144**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-14 22:41:06.215038**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-10-14 22:41:10.417593**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-14 22:41:10.522616**: equivalence pseudoword vs word on 'bigram_freq': d = -1.04 [-1.36, -0.71], TOST p = 0.998 (not shown equivalent)
- **2026-10-14 22:41:10.538744**: equivalence pseudoword vs word on 'n_density': d = 0.77 [0.45, 1.08], TOST p = 0.926 (not shown equivalent)
- **2026-10-14 22:41:10.551969**: equivalence pseudoword vs word on 'old20': d = -0.81 [-1.13, -0.50], TOST p = 0.956 (not shown equivalent)
- **2026-10-14 22:41:11.473587**: wrote 'en_lexdec_wuggy_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_wuggy_english_stimuli_R.csv
    - rows: 120
    - md5: ee8cb48ab37e9e22472854cb6f8fbf9d
- **2026-10-14 22:41:11.629549**: wrote 'en_lexdec_wuggy_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_descriptives_R.csv
    - rows: 8
    - md5: 85bd7825d15c68f8bc7ad8de3b5895b1
- **2026-10-14 22:41:11.84991**: wrote 'en_lexdec_wuggy_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_comparisons_R.csv
    - rows: 4
    - md5: 08897c0a60cc9f96cead7bfb196a8277
- **2026-10-14 22:41:15.313642**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.py
    - rows: NA
    - md5: 75928f519cf74589a0f486adbcb8ea16
- **2026-10-14 22:41:15.349056**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output/experiments/en_lexdec_wuggy_english.osexp
    - rows: NA
    - md5: 5ac7d322afad8801139d2b37078c4b3b
- **2026-10-14 22:41:15.397284**: wrote 'en_lexdec_wuggy_english.html'
    - path: output/experiments/en_lexdec_wuggy_english.html
    - rows: NA
    - md5: 6f180d88cf2dc143d1fe2e63d347045e
- **2026-10-14 22:41:15.432391**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.csv
    - rows: NA
    - md5: 0de7b7f6581d5b70dbdc3900c1868ed0
- **2026-10-14 22:41:15.477112**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-14 22:41:15.519242**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame_text.csv
    - rows: NA
    - md5: e99b430bc4617d165f9ff00cd45d707f
- **2026-10-14 22:41:16.198047**: wrote 'en_lexdec_wuggy_english_datasheet_R.json'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.json
    - rows: NA
    - md5: ae8d529ca72fdd302d94c844de212ac5
- **2026-10-14 22:41:16.227493**: wrote 'en_lexdec_wuggy_english_datasheet_R.md'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.md
    - rows: NA
    - md5: cf9404680c9fffbab4e2b8e04e47cd9a
