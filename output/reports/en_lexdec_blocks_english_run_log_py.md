# lexsync run log: en_lexdec_blocks

- Engine: Python 3.13.7
- Started: 2026-10-03T00:45:29
- Finished: 2026-10-03T00:45:34

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03T00:45:29**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03T00:45:30**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03T00:45:30**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-03T00:45:31**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-03T00:45:31**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.0611 (not shown equivalent)
- **2026-10-03T00:45:31**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-10-03T00:45:31**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-10-03T00:45:31**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-10-03T00:45:31**: presented 56 trial(s); 40 analysed
- **2026-10-03T00:45:32**: wrote 'en_lexdec_blocks_english_stimuli_py.csv'
    - path: output\stimuli\en_lexdec_blocks_english_stimuli_py.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-10-03T00:45:32**: wrote 'en_lexdec_blocks_english_descriptives_py.csv'
    - path: output\reports\en_lexdec_blocks_english_descriptives_py.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-10-03T00:45:32**: wrote 'en_lexdec_blocks_english_comparisons_py.csv'
    - path: output\reports\en_lexdec_blocks_english_comparisons_py.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-10-03T00:45:33**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output\experiments\en_lexdec_blocks_english_psychopy.py
    - rows: None
    - md5: 0f893d30fa6aa2bc1a23c20e9c16322d
- **2026-10-03T00:45:33**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output\experiments\en_lexdec_blocks_english.osexp
    - rows: None
    - md5: e47058473d90568b614897977ced9359
- **2026-10-03T00:45:33**: wrote 'en_lexdec_blocks_english.html'
    - path: output\experiments\en_lexdec_blocks_english.html
    - rows: None
    - md5: b5fd647854a780f8f04b95f11136e995
- **2026-10-03T00:45:34**: wrote 'en_lexdec_blocks_english_datasheet_py.json'
    - path: output\reports\en_lexdec_blocks_english_datasheet_py.json
    - rows: None
    - md5: 539f022fc3b8ec1fca136353cbdcfd81
- **2026-10-03T00:45:34**: wrote 'en_lexdec_blocks_english_datasheet_py.md'
    - path: output\reports\en_lexdec_blocks_english_datasheet_py.md
    - rows: None
    - md5: 98978eafb4e2a10b540ebb7cf9861c24
