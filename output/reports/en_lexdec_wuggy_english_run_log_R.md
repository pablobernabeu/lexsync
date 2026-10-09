# lexsync run log: en_lexdec_wuggy

- Engine: R 4.6.1
- Started: 2026-10-09 09:52:45.418852
- Finished: 2026-10-09 09:52:59.829342

## Run metadata

- design: en_lexdec_wuggy
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:52:45.42238**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 09:52:46.068834**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:52:46.087841**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 09:52:58.129329**: generated 120 items (words + pseudowords, subsyllabic)
    - conditions: word, pseudoword
- **2026-10-09 09:52:59.204393**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-09 09:52:59.209489**: equivalence pseudoword vs word on 'bigram_freq': d = -1.59 [-1.94, -1.25], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:52:59.213603**: equivalence pseudoword vs word on 'n_density': d = 0.32 [0.01, 0.62], TOST p = 0.158 (not shown equivalent)
- **2026-10-09 09:52:59.217392**: equivalence pseudoword vs word on 'old20': d = -0.34 [-0.64, -0.04], TOST p = 0.192 (not shown equivalent)
- **2026-10-09 09:52:59.261546**: wrote 'en_lexdec_wuggy_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_wuggy_english_stimuli_R.csv
    - rows: 120
    - md5: f61658d63ceedd481095201a16e84243
- **2026-10-09 09:52:59.278568**: wrote 'en_lexdec_wuggy_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_descriptives_R.csv
    - rows: 8
    - md5: 308960c8bc8065b1cb357900ae00b59f
- **2026-10-09 09:52:59.294545**: wrote 'en_lexdec_wuggy_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_wuggy_english_comparisons_R.csv
    - rows: 4
    - md5: 368ebde0b0d771e30ca0691b63afb844
- **2026-10-09 09:52:59.587129**: wrote 'en_lexdec_wuggy_english_psychopy.py'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.py
    - rows: NA
    - md5: ea0c5c48e3e6274f3f12683dc2434809
- **2026-10-09 09:52:59.598073**: wrote 'en_lexdec_wuggy_english.osexp'
    - path: output/experiments/en_lexdec_wuggy_english.osexp
    - rows: NA
    - md5: 469e39d61647c8f3f7256dee61682eeb
- **2026-10-09 09:52:59.607821**: wrote 'en_lexdec_wuggy_english.html'
    - path: output/experiments/en_lexdec_wuggy_english.html
    - rows: NA
    - md5: a848c4b076c85b72dbee21fc613b78f4
- **2026-10-09 09:52:59.62136**: wrote 'en_lexdec_wuggy_english_psychopy.csv'
    - path: output/experiments/en_lexdec_wuggy_english_psychopy.csv
    - rows: NA
    - md5: 7ec3af0947432fb80cb5ee35e9c3364c
- **2026-10-09 09:52:59.627532**: wrote 'en_lexdec_wuggy_english_opensesame.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-09 09:52:59.63553**: wrote 'en_lexdec_wuggy_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_wuggy_english_opensesame_text.csv
    - rows: NA
    - md5: 1c3272c3c8db56145cbd8aa483d04f3b
- **2026-10-09 09:52:59.806761**: wrote 'en_lexdec_wuggy_english_datasheet_R.json'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.json
    - rows: NA
    - md5: c43fd63721e568aa872df6c86c5ef8f3
- **2026-10-09 09:52:59.819186**: wrote 'en_lexdec_wuggy_english_datasheet_R.md'
    - path: output/reports/en_lexdec_wuggy_english_datasheet_R.md
    - rows: NA
    - md5: 6ebe2c6f5be3787083d906c81f29a872
