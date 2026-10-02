# lexsync run log: en_lexdec_blocks

- Engine: R 4.6.1
- Started: 2026-10-02 16:43:28.442638
- Finished: 2026-10-02 16:43:46.504364

## Run metadata

- design: en_lexdec_blocks
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:43:28.499251**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 16:43:30.450366**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:43:31.01344**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-02 16:43:33.156063**: generated 40 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-02 16:43:33.500474**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-02 16:43:34.524628**: block 'main': 40 trial(s) per list
    - block: main
    - n_per_list: 40
- **2026-10-02 16:43:34.898019**: block 'filler': 8 trial(s) per list, interleaved with the main trials by the seeded order
    - block: filler
    - n_per_list: 8
- **2026-10-02 16:43:34.934035**: block 'practice': 8 trial(s) per list, before the main trials
    - block: practice
    - n_per_list: 8
- **2026-10-02 16:43:34.941289**: presented 56 trial(s); 40 analysed
- **2026-10-02 16:43:35.915761**: wrote 'en_lexdec_blocks_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_blocks_english_stimuli_R.csv
    - rows: 40
    - md5: e8cebfaae793fa0fd06361f08ab299a7
- **2026-10-02 16:43:36.837363**: wrote 'en_lexdec_blocks_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_blocks_english_descriptives_R.csv
    - rows: 2
    - md5: 3367654215186214d386f99c675b7c91
- **2026-10-02 16:43:37.516545**: wrote 'en_lexdec_blocks_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_blocks_english_comparisons_R.csv
    - rows: 1
    - md5: 546cefb81ae05b5cc1e2d0e3d0d49349
- **2026-10-02 16:43:44.317908**: wrote 'en_lexdec_blocks_english_psychopy.py'
    - path: output/experiments/en_lexdec_blocks_english_psychopy.py
    - rows: NA
    - md5: 0f893d30fa6aa2bc1a23c20e9c16322d
- **2026-10-02 16:43:44.486993**: wrote 'en_lexdec_blocks_english.osexp'
    - path: output/experiments/en_lexdec_blocks_english.osexp
    - rows: NA
    - md5: e47058473d90568b614897977ced9359
- **2026-10-02 16:43:44.621066**: wrote 'en_lexdec_blocks_english.html'
    - path: output/experiments/en_lexdec_blocks_english.html
    - rows: NA
    - md5: b5fd647854a780f8f04b95f11136e995
- **2026-10-02 16:43:46.255494**: wrote 'en_lexdec_blocks_english_datasheet_R.json'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.json
    - rows: NA
    - md5: 9a92591373084481e33aed5694b84420
- **2026-10-02 16:43:46.375204**: wrote 'en_lexdec_blocks_english_datasheet_R.md'
    - path: output/reports/en_lexdec_blocks_english_datasheet_R.md
    - rows: NA
    - md5: 6cff4f53043766019eb6811a7ed053ae
