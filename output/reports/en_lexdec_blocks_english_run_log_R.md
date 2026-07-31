# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-07-31 22:35:05.806437
- Finished: 2026-07-31 22:35:07.214773

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 22:35:05.809903**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 22:35:06.248565**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 22:35:06.262403**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-31 22:35:06.884097**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-31 22:35:06.894851**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-07-31 22:35:06.951918**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-07-31 22:35:06.956384**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-07-31 22:35:06.961273**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-07-31 22:35:06.964687**: presented 56 trial(s); 40 analysed
- **2026-07-31 22:35:06.983553**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-07-31 22:35:06.999568**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-07-31 22:35:07.014596**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-07-31 22:35:07.0941**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 0f893d30fa6aa2bc1a23c20e9c16322d
- **2026-07-31 22:35:07.102663**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: be77372684e9531418f679dea3294e09
- **2026-07-31 22:35:07.110754**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: b5fd647854a780f8f04b95f11136e995
- **2026-07-31 22:35:07.197675**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: 662e30ba5342fd49f926b502b0cb2325
- **2026-07-31 22:35:07.206053**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: 4f1ff40fccfb2f4af3cb4e7d3c0df482
