# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-09-23 23:12:24.871443
- Finished: 2026-09-23 23:12:31.333778

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-09-23 23:12:24.885808**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-23 23:12:26.038087**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-23 23:12:26.105276**: pool after filters: 8177 words
    - pool: 8177
- **2026-09-23 23:12:28.112209**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-09-23 23:12:28.194419**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-09-23 23:12:29.303745**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-09-23 23:12:29.454663**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-09-23 23:12:29.524083**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-09-23 23:12:30.85303**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-09-23 23:12:30.873201**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-09-23 23:12:30.894985**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 05d63ae6ec738c055aea3769358ef22a
- **2026-09-23 23:12:31.214748**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: de4c9337e54f8ba62bd8c5e0042fe719
- **2026-09-23 23:12:31.277581**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 2e3764bb122d9535be051e3bc50902ee
