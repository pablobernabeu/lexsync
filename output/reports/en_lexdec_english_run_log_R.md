# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-07-31 22:35:03.911343
- Finished: 2026-07-31 22:35:05.784682

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 22:35:03.915338**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 22:35:04.368974**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 22:35:04.38001**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-31 22:35:05.401903**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-31 22:35:05.415648**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-31 22:35:05.46146**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-07-31 22:35:05.480338**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-07-31 22:35:05.499382**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-31 22:35:05.630132**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-07-31 22:35:05.644153**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-07-31 22:35:05.653986**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: b3841161510a3bea9d2de0be9419796f
- **2026-07-31 22:35:05.761902**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: a20a9f74f12b391e39527c21087948b2
- **2026-07-31 22:35:05.773279**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: a88767b2ecf499c79cd6100ee6684032
