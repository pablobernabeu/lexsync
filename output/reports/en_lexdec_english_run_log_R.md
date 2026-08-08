# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-08-07 22:49:46.483824
- Finished: 2026-08-07 22:49:49.385677

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-08-07 22:49:46.49604**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-07 22:49:47.195343**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-07 22:49:47.219263**: pool after filters: 8177 words
    - pool: 8177
- **2026-08-07 22:49:48.61285**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-08-07 22:49:48.63042**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-08-07 22:49:48.965631**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-08-07 22:49:48.997201**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-08-07 22:49:49.029543**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-08-07 22:49:49.191405**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-08-07 22:49:49.205785**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-08-07 22:49:49.221278**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: b3841161510a3bea9d2de0be9419796f
- **2026-08-07 22:49:49.362043**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 4a2590ccff8ed865c7285c460165632c
- **2026-08-07 22:49:49.373325**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 2e3764bb122d9535be051e3bc50902ee
