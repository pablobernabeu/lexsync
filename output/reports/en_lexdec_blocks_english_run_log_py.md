# lexsync run log: en_lexdec_blocks

- Engine: Python 3.11.15
- Started: 2026-09-02T19:25:42
- Finished: 2026-09-02T19:25:43

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02T19:25:42**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02T19:25:42**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02T19:25:42**: pool after filters: 8177 words
    - pool: 8177
- **2026-09-02T19:25:43**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-09-02T19:25:43**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.0611 (not shown equivalent)
- **2026-09-02T19:25:43**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-09-02T19:25:43**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-09-02T19:25:43**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-09-02T19:25:43**: presented 56 trial(s); 40 analysed
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_stimuli_py.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_py.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_descriptives_py.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_py.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_comparisons_py.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_py.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: None
    - md5: 10d3dc540ad7ce6e0352ddbf289c1c74
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: None
    - md5: be77372684e9531418f679dea3294e09
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: None
    - md5: 09db2d67f7ccba29f6bc1ea0dcdfb6d0
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_datasheet_py.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_py.json
    - rows: None
    - md5: aa2bdacea842f86ed4acc9facbe8295a
- **2026-09-02T19:25:43**: wrote 'en_lexdec_blocks_english_datasheet_py.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_py.md
    - rows: None
    - md5: 6fcd8ab93a13a8880d224a1344102ed8
