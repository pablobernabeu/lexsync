# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-10-09 05:57:46.07468
- Finished: 2026-10-09 05:57:48.659225

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:57:46.081654**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 05:57:46.926859**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 05:57:46.950344**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 05:57:47.822706**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09 05:57:47.836815**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-09 05:57:47.97489**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-10-09 05:57:47.985211**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-10-09 05:57:47.994244**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-10-09 05:57:48.007283**: presented 56 trial(s); 40 analysed
- **2026-10-09 05:57:48.043245**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-10-09 05:57:48.067633**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-10-09 05:57:48.091829**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-10-09 05:57:48.370442**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 6b9f7f8631069cc6cf7c6ede496eb06d
- **2026-10-09 05:57:48.38157**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: 1e87120fc4ba80a9430428f8e634aef9
- **2026-10-09 05:57:48.390717**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: ed5e2116c2ce4bb518c210eb6e8177ad
- **2026-10-09 05:57:48.405698**: wrote 'en_lexdec_blocks_english_psychopy.csv'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.csv
    - rows: NA
    - md5: 079332a39f63c6651631d7944a282322
- **2026-10-09 05:57:48.414361**: wrote 'en_lexdec_blocks_english_opensesame.csv'
    - path: output/experiments/en_lexdec_blocks_english_opensesame.csv
    - rows: NA
    - md5: 2f7351bc8df496f4eb354857d7c5d4a9
- **2026-10-09 05:57:48.424058**: wrote 'en_lexdec_blocks_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_blocks_english_opensesame_text.csv
    - rows: NA
    - md5: 4da67b7575c7acc6bb74bdc01ec91988
- **2026-10-09 05:57:48.635819**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: 46707a1e37af6264caa3dc3f44f6fe91
- **2026-10-09 05:57:48.647314**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: 0040ad95c0e76ca306c77f1a897f1b3c
