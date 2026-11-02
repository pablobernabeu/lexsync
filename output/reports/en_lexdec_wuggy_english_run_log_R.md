# lexsync run log: en_lexdec_wuggy

- Engine: R 4.6.1
- Started: 2026-11-02 21:28:40.468198
- Finished: 2026-11-02 21:28:51.493297

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-11-02 21:28:40.469272**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-11-02 21:28:41.324296**: lexicon loaded: 30000 words
    - words: 30000
- **2026-11-02 21:28:41.328484**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-11-02 21:28:41.33485**: pool after filters: 6767 words
    - pool: 6767
- **2026-11-02 21:28:41.632243**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-11-02 21:28:50.332587**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-11-02 21:28:51.039105**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-11-02 21:28:51.039475**: equivalence pseudoword vs word on 'bigram_freq': d = -1.04 [-1.36, -0.71], TOST p = 0.998 (not shown equivalent)
- **2026-11-02 21:28:51.039784**: equivalence pseudoword vs word on 'n_density': d = 0.77 [0.45, 1.08], TOST p = 0.926 (not shown equivalent)
- **2026-11-02 21:28:51.040128**: equivalence pseudoword vs word on 'old20': d = -0.81 [-1.13, -0.50], TOST p = 0.956 (not shown equivalent)
- **2026-11-02 21:28:51.07099**: wrote 'en_lexdec_wuggy_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_wuggy_english_stimuli_R.csv
    - rows: 120
    - md5: ee8cb48ab37e9e22472854cb6f8fbf9d
- **2026-11-02 21:28:51.074849**: wrote 'en_lexdec_wuggy_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_descriptives_R.csv
    - rows: 8
    - md5: 85bd7825d15c68f8bc7ad8de3b5895b1
- **2026-11-02 21:28:51.077791**: wrote 'en_lexdec_wuggy_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_comparisons_R.csv
    - rows: 4
    - md5: 08897c0a60cc9f96cead7bfb196a8277
- **2026-11-02 21:28:51.332372**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.py
    - rows: NA
    - md5: 2e7623cbb4f2cb5a27cb3b3f5c31da8b
- **2026-11-02 21:28:51.33285**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output/experiments/en_lexdec_wuggy_english.osexp
    - rows: NA
    - md5: 5ac7d322afad8801139d2b37078c4b3b
- **2026-11-02 21:28:51.333176**: wrote 'en_lexdec_wuggy_english.html'
    - path: output/experiments/en_lexdec_wuggy_english.html
    - rows: NA
    - md5: 6f6c4a1780ca2ec0d8ee707c90c854bd
- **2026-11-02 21:28:51.333544**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.csv
    - rows: NA
    - md5: 0de7b7f6581d5b70dbdc3900c1868ed0
- **2026-11-02 21:28:51.333852**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-11-02 21:28:51.33415**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame_text.csv
    - rows: NA
    - md5: e99b430bc4617d165f9ff00cd45d707f
- **2026-11-02 21:28:51.492307**: wrote 'en_lexdec_wuggy_english_datasheet_R.json'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.json
    - rows: NA
    - md5: 96a62cb076d9c0e005f2f196a13c1917
- **2026-11-02 21:28:51.492721**: wrote 'en_lexdec_wuggy_english_datasheet_R.md'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.md
    - rows: NA
    - md5: e65174e6afccdadc746d16f707732aff
