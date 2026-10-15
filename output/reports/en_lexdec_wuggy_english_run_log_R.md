# lexsync run log: en_lexdec_wuggy

- Engine: R 4.6.1
- Started: 2026-10-15 03:28:45.077337
- Finished: 2026-10-15 03:29:13.136013

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 03:28:45.087404**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-15 03:28:47.073183**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 03:28:47.090717**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-15 03:28:47.107949**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-15 03:28:47.788993**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-15 03:29:10.442847**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-10-15 03:29:11.844537**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-15 03:29:11.854851**: equivalence pseudoword vs word on 'bigram_freq': d = -1.04 [-1.36, -0.71], TOST p = 0.998 (not shown equivalent)
- **2026-10-15 03:29:11.86782**: equivalence pseudoword vs word on 'n_density': d = 0.77 [0.45, 1.08], TOST p = 0.926 (not shown equivalent)
- **2026-10-15 03:29:11.876918**: equivalence pseudoword vs word on 'old20': d = -0.81 [-1.13, -0.50], TOST p = 0.956 (not shown equivalent)
- **2026-10-15 03:29:11.957422**: wrote 'en_lexdec_wuggy_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_wuggy_english_stimuli_R.csv
    - rows: 120
    - md5: ee8cb48ab37e9e22472854cb6f8fbf9d
- **2026-10-15 03:29:11.989402**: wrote 'en_lexdec_wuggy_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_descriptives_R.csv
    - rows: 8
    - md5: 85bd7825d15c68f8bc7ad8de3b5895b1
- **2026-10-15 03:29:12.017299**: wrote 'en_lexdec_wuggy_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_comparisons_R.csv
    - rows: 4
    - md5: 08897c0a60cc9f96cead7bfb196a8277
- **2026-10-15 03:29:12.556608**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.py
    - rows: NA
    - md5: 8f06a6a5f643d963b3df72a40bf8cf31
- **2026-10-15 03:29:12.57**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output/experiments/en_lexdec_wuggy_english.osexp
    - rows: NA
    - md5: 5ac7d322afad8801139d2b37078c4b3b
- **2026-10-15 03:29:12.584469**: wrote 'en_lexdec_wuggy_english.html'
    - path: output/experiments/en_lexdec_wuggy_english.html
    - rows: NA
    - md5: 5d909b5d06946d5bd244ae9c51de88a2
- **2026-10-15 03:29:12.60419**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.csv
    - rows: NA
    - md5: 0de7b7f6581d5b70dbdc3900c1868ed0
- **2026-10-15 03:29:12.616045**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-15 03:29:12.627248**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame_text.csv
    - rows: NA
    - md5: e99b430bc4617d165f9ff00cd45d707f
- **2026-10-15 03:29:13.099581**: wrote 'en_lexdec_wuggy_english_datasheet_R.json'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.json
    - rows: NA
    - md5: 961389fa71c990b41ca5ffefe4ade774
- **2026-10-15 03:29:13.117973**: wrote 'en_lexdec_wuggy_english_datasheet_R.md'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.md
    - rows: NA
    - md5: cf9404680c9fffbab4e2b8e04e47cd9a
