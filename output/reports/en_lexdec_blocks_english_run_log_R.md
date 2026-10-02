# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-10-03 00:30:01.833598
- Finished: 2026-10-03 00:30:36.433335

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:30:02.018586**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:30:06.362555**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 00:30:06.58283**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-03 00:30:08.880231**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-03 00:30:09.013955**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-03 00:30:11.117954**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-10-03 00:30:11.243072**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-10-03 00:30:11.251885**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-10-03 00:30:11.257642**: presented 56 trial(s); 40 analysed
- **2026-10-03 00:30:14.487375**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-10-03 00:30:15.420532**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-10-03 00:30:15.800808**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-10-03 00:30:32.052757**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 0f893d30fa6aa2bc1a23c20e9c16322d
- **2026-10-03 00:30:32.358859**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: e47058473d90568b614897977ced9359
- **2026-10-03 00:30:32.749147**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: b5fd647854a780f8f04b95f11136e995
- **2026-10-03 00:30:35.879408**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: d5c9fc75ee03974694763d8c3bfe0357
- **2026-10-03 00:30:36.113003**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: f36df5faa41f3595b09f26b22d929903
