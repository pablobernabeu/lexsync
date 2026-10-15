# lexsync run log: es_lexdec

- Engine: Python 3.13.7
- Started: 2026-10-15T03:30:52
- Finished: 2026-10-15T03:30:56

## Run metadata

- design: es_lexdec
- language: spanish
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15T03:30:52**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15T03:30:52**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-15T03:30:52**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15T03:30:52**: pool after filters: 8305 words
    - pool: 8305
- **2026-10-15T03:30:54**: pseudowords checked against 334625 known word form(s) from 'corpora/derived/es_known_forms.txt'
    - exclude: corpora/derived/es_known_forms.txt
    - sha256: 281fa6c374e1fa6550e6f5700d19b9bae4ccb664cfd3fc37ca6ffc087acdd776
- **2026-10-15T03:30:55**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-15T03:30:55**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-15T03:30:55**: equivalence pseudoword vs word on 'bigram_freq': d = -1.21 [-1.54, -0.88], TOST p = 0.9999 (not shown equivalent)
- **2026-10-15T03:30:55**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-15T03:30:55**: equivalence pseudoword vs word on 'old20': d = 0.02 [-0.28, 0.32], TOST p = 0.0049 (equivalent)
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_stimuli_py.csv'
    - path: output\stimuli\es_lexdec_spanish_stimuli_py.csv
    - rows: 120
    - md5: f34a8e3b82774563ec5c6e51211fa385
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_descriptives_py.csv'
    - path: output\reports\es_lexdec_spanish_descriptives_py.csv
    - rows: 8
    - md5: a5359adc48f76fd75aefa9b95c83907e
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_comparisons_py.csv'
    - path: output\reports\es_lexdec_spanish_comparisons_py.csv
    - rows: 4
    - md5: a2b9a2754d018354bbe0abdbb5850666
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_psychopy.py'
    - path: output\experiments\es_lexdec_spanish_psychopy.py
    - rows: None
    - md5: 6e8ec3994e96f4ef6239e27d55e8836a
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish.osexp'
    - path: output\experiments\es_lexdec_spanish.osexp
    - rows: None
    - md5: 275c631cd7a24cd5bd7d7b5c2f6d7dc5
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish.html'
    - path: output\experiments\es_lexdec_spanish.html
    - rows: None
    - md5: d18626fc6446058d92149ddd78bdbd8d
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_psychopy.csv'
    - path: output\experiments\es_lexdec_spanish_psychopy.csv
    - rows: None
    - md5: 2a6f6f7cfb6929d91027c03e23698263
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_opensesame.csv'
    - path: output\experiments\es_lexdec_spanish_opensesame.csv
    - rows: None
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_opensesame_text.csv'
    - path: output\experiments\es_lexdec_spanish_opensesame_text.csv
    - rows: None
    - md5: bf9c50c952be24b560b4a1ce78815bce
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_datasheet_py.json'
    - path: output\reports\es_lexdec_spanish_datasheet_py.json
    - rows: None
    - md5: 3782762825d3a0a82dd146267c01058b
- **2026-10-15T03:30:56**: wrote 'es_lexdec_spanish_datasheet_py.md'
    - path: output\reports\es_lexdec_spanish_datasheet_py.md
    - rows: None
    - md5: 7bbfc851327019b055c53f594332cc7f
