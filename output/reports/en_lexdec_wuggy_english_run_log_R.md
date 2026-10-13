# lexsync run log: en_lexdec_wuggy

- Engine: R 4.6.1
- Started: 2026-10-13 18:17:02.6166
- Finished: 2026-10-13 18:17:29.741562

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:17:02.624906**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 18:17:04.925659**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 18:17:05.268644**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 18:17:05.295851**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-13 18:17:06.255407**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-13 18:17:25.554942**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-10-13 18:17:27.711385**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-13 18:17:27.727931**: equivalence pseudoword vs word on 'bigram_freq': d = -1.04 [-1.36, -0.71], TOST p = 0.998 (not shown equivalent)
- **2026-10-13 18:17:27.735702**: equivalence pseudoword vs word on 'n_density': d = 0.77 [0.45, 1.08], TOST p = 0.926 (not shown equivalent)
- **2026-10-13 18:17:27.744662**: equivalence pseudoword vs word on 'old20': d = -0.81 [-1.13, -0.50], TOST p = 0.956 (not shown equivalent)
- **2026-10-13 18:17:27.875071**: wrote 'en_lexdec_wuggy_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_wuggy_english_stimuli_R.csv
    - rows: 120
    - md5: ee8cb48ab37e9e22472854cb6f8fbf9d
- **2026-10-13 18:17:27.911723**: wrote 'en_lexdec_wuggy_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_descriptives_R.csv
    - rows: 8
    - md5: 85bd7825d15c68f8bc7ad8de3b5895b1
- **2026-10-13 18:17:27.988046**: wrote 'en_lexdec_wuggy_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_comparisons_R.csv
    - rows: 4
    - md5: 08897c0a60cc9f96cead7bfb196a8277
- **2026-10-13 18:17:29.015457**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.py
    - rows: NA
    - md5: 01f432a18ae0de85e89d21c2b62674ff
- **2026-10-13 18:17:29.036494**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output/experiments/en_lexdec_wuggy_english.osexp
    - rows: NA
    - md5: 8dc71dfa635cfef42306864f7ea91d0b
- **2026-10-13 18:17:29.057696**: wrote 'en_lexdec_wuggy_english.html'
    - path: output/experiments/en_lexdec_wuggy_english.html
    - rows: NA
    - md5: 9835545d10cc6e565d01a545d5bdcaf1
- **2026-10-13 18:17:29.081316**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.csv
    - rows: NA
    - md5: 0de7b7f6581d5b70dbdc3900c1868ed0
- **2026-10-13 18:17:29.0987**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-13 18:17:29.118791**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame_text.csv
    - rows: NA
    - md5: e99b430bc4617d165f9ff00cd45d707f
- **2026-10-13 18:17:29.695736**: wrote 'en_lexdec_wuggy_english_datasheet_R.json'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.json
    - rows: NA
    - md5: 8a816a0d96390076a7a41bd8f18761d2
- **2026-10-13 18:17:29.719441**: wrote 'en_lexdec_wuggy_english_datasheet_R.md'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.md
    - rows: NA
    - md5: cf9404680c9fffbab4e2b8e04e47cd9a
