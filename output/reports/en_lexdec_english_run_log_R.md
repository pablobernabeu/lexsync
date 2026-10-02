# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-09 07:15:52.728005
- Finished: 2026-10-09 07:15:55.685194

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:15:52.73262**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:15:53.407319**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:15:53.423586**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 07:15:54.933535**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09 07:15:54.945562**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-09 07:15:54.992364**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-10-09 07:15:55.00884**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-10-09 07:15:55.025321**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-10-09 07:15:55.376313**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: a9c90173d7b34b6b6c1a914fa5132f57
- **2026-10-09 07:15:55.387509**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 694c11f70ca325181628b5da1922e729
- **2026-10-09 07:15:55.398848**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 3307ed89b9e2aaa71ac5dfcff505306d
- **2026-10-09 07:15:55.418667**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 1fe32d4aaed880e77a845f82eb6df4a6
- **2026-10-09 07:15:55.427961**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-09 07:15:55.43661**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 706132481e716f2a1ada15a83b56c292
- **2026-10-09 07:15:55.660827**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 780ff7c8b340ca78160050503b399c0b
- **2026-10-09 07:15:55.672406**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: b6ca69c890ba3002f7a3ea7d576c1737
