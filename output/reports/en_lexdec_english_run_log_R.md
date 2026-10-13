# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-13 18:16:37.356758
- Finished: 2026-10-13 18:16:52.798129

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:16:37.367576**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 18:16:41.089032**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 18:16:41.137016**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 18:16:41.202183**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-13 18:16:43.279737**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-13 18:16:48.617735**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-13 18:16:50.513862**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-13 18:16:50.534097**: equivalence pseudoword vs word on 'bigram_freq': d = -0.97 [-1.29, -0.65], TOST p = 0.994 (not shown equivalent)
- **2026-10-13 18:16:50.553036**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-13 18:16:50.567049**: equivalence pseudoword vs word on 'old20': d = -0.04 [-0.34, 0.26], TOST p = 0.006 (equivalent)
- **2026-10-13 18:16:50.658582**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: 904a03751c491ba9979823cf6ad1aca4
- **2026-10-13 18:16:50.687478**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: f703a5d9fc95ab14d7c8b7b81238ee62
- **2026-10-13 18:16:50.735925**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 1351a5c0c730e41e247d8ee90369ac23
- **2026-10-13 18:16:52.019963**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 5a813c807e11ae574719dacaa4e88855
- **2026-10-13 18:16:52.065976**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: ec860e7513b32667cae428ef08a60c53
- **2026-10-13 18:16:52.091508**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: d443889251ce38aa0b34726c10b78e70
- **2026-10-13 18:16:52.132091**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 5ad87de0d5fb738c0c4b1217a34e2bed
- **2026-10-13 18:16:52.171626**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-13 18:16:52.190381**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 850a6fc2a8c8cccde050f67c41e70fa7
- **2026-10-13 18:16:52.760594**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: d85e1370eba7723d8ff22fcb2723bd97
- **2026-10-13 18:16:52.778392**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 2bd1258e250949aab3323563408db510
