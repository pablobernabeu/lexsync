# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-09-24 16:59:53.504307
- Finished: 2026-09-24 16:59:55.622871

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 16:59:53.509778**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-24 16:59:54.122964**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-24 16:59:54.144253**: pool after filters: 8177 words
    - pool: 8177
- **2026-09-24 16:59:55.030055**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-09-24 16:59:55.04522**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-09-24 16:59:55.178375**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-09-24 16:59:55.184075**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-09-24 16:59:55.188827**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-09-24 16:59:55.196529**: presented 56 trial(s); 40 analysed
- **2026-09-24 16:59:55.22733**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-09-24 16:59:55.246984**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-09-24 16:59:55.269434**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-09-24 16:59:55.404822**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 0f893d30fa6aa2bc1a23c20e9c16322d
- **2026-09-24 16:59:55.41882**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: be77372684e9531418f679dea3294e09
- **2026-09-24 16:59:55.432731**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: b5fd647854a780f8f04b95f11136e995
- **2026-09-24 16:59:55.59579**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: 512d4d2ab783afa6c9d42f53bf57fd35
- **2026-09-24 16:59:55.610392**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: 6aa69eb8025e6d3c7163db414d71ffa0
