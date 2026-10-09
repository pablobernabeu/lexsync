# lexsync run log: en_lexdec

- Engine: Python 3.13.7
- Started: 2026-10-09T09:53:35
- Finished: 2026-10-09T09:53:36

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T09:53:35**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09T09:53:36**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T09:53:36**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09T09:53:36**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09T09:53:36**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-09T09:53:36**: equivalence pseudoword vs word on 'bigram_freq': d = -1.47 [-1.81, -1.13], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T09:53:36**: equivalence pseudoword vs word on 'n_density': d = -0.28 [-0.59, 0.02], TOST p = 0.1167 (not shown equivalent)
- **2026-10-09T09:53:36**: equivalence pseudoword vs word on 'old20': d = 0.17 [-0.13, 0.47], TOST p = 0.0372 (equivalent)
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_stimuli_py.csv'
    - path: output\stimuli\en_lexdec_english_stimuli_py.csv
    - rows: 120
    - md5: bc7c16452b7fd7cbabe8fafc8bb28287
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_descriptives_py.csv'
    - path: output\reports\en_lexdec_english_descriptives_py.csv
    - rows: 8
    - md5: bee90fb07b347d3fe262803a6f342ade
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_comparisons_py.csv'
    - path: output\reports\en_lexdec_english_comparisons_py.csv
    - rows: 4
    - md5: 9464b3452793472e9abce17609e3d369
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_psychopy.py'
    - path: output\experiments\en_lexdec_english_psychopy.py
    - rows: None
    - md5: a9c90173d7b34b6b6c1a914fa5132f57
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english.osexp'
    - path: output\experiments\en_lexdec_english.osexp
    - rows: None
    - md5: 694c11f70ca325181628b5da1922e729
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english.html'
    - path: output\experiments\en_lexdec_english.html
    - rows: None
    - md5: 3307ed89b9e2aaa71ac5dfcff505306d
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output\experiments\en_lexdec_english_psychopy.csv
    - rows: None
    - md5: 1fe32d4aaed880e77a845f82eb6df4a6
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output\experiments\en_lexdec_english_opensesame.csv
    - rows: None
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output\experiments\en_lexdec_english_opensesame_text.csv
    - rows: None
    - md5: 706132481e716f2a1ada15a83b56c292
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_datasheet_py.json'
    - path: output\reports\en_lexdec_english_datasheet_py.json
    - rows: None
    - md5: 601c636328aab9c41d4771729169e821
- **2026-10-09T09:53:36**: wrote 'en_lexdec_english_datasheet_py.md'
    - path: output\reports\en_lexdec_english_datasheet_py.md
    - rows: None
    - md5: ea3f34367b1d6da4d5cbfef9be9599ca
