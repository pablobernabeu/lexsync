# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-10-09 04:43:16.657458
- Finished: 2026-10-09 04:43:20.215636

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 04:43:16.666387**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 04:43:17.646804**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 04:43:17.670155**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 04:43:18.821645**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09 04:43:18.843776**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-09 04:43:19.03357**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-10-09 04:43:19.043897**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-10-09 04:43:19.054233**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-10-09 04:43:19.061741**: presented 56 trial(s); 40 analysed
- **2026-10-09 04:43:19.098259**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-10-09 04:43:19.123214**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-10-09 04:43:19.149232**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-10-09 04:43:19.901663**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 6b9f7f8631069cc6cf7c6ede496eb06d
- **2026-10-09 04:43:19.917478**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: 1e87120fc4ba80a9430428f8e634aef9
- **2026-10-09 04:43:19.929455**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: ed5e2116c2ce4bb518c210eb6e8177ad
- **2026-10-09 04:43:19.950134**: wrote 'en_lexdec_blocks_english_psychopy.csv'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.csv
    - rows: NA
    - md5: 079332a39f63c6651631d7944a282322
- **2026-10-09 04:43:19.966095**: wrote 'en_lexdec_blocks_english_opensesame.csv'
    - path: output/experiments/en_lexdec_blocks_english_opensesame.csv
    - rows: NA
    - md5: 2f7351bc8df496f4eb354857d7c5d4a9
- **2026-10-09 04:43:19.978363**: wrote 'en_lexdec_blocks_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_blocks_english_opensesame_text.csv
    - rows: NA
    - md5: 4da67b7575c7acc6bb74bdc01ec91988
- **2026-10-09 04:43:20.17315**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: 130c9bdd2fb38c8a4e309062549ed4ab
- **2026-10-09 04:43:20.196384**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: 0040ad95c0e76ca306c77f1a897f1b3c
