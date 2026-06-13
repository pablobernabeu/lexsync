# lexsync run log: en_lexdec

- Engine: Python 3.13.7
- Started: 2026-06-13T21:42:25
- Finished: 2026-06-13T21:42:26

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026

## Steps

- **2026-06-13T21:42:25** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13T21:42:25** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13T21:42:25** -- pool after filters: 8177 words
    - pool: 8177
- **2026-06-13T21:42:26** -- generated 120 items (words + pseudowords)
    - conditions: word, pseudoword
- **2026-06-13T21:42:26** -- equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english_stimuli_py.csv'
    - path: output\stimuli\en_lexdec_english_stimuli_py.csv
    - rows: 120
    - md5: fc7d968241ce9361cc6daad6fdc3ecb2
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english_descriptives_py.csv'
    - path: output\reports\en_lexdec_english_descriptives_py.csv
    - rows: 2
    - md5: 61ff24fe3f286092f7c39c99edc5b454
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english_comparisons_py.csv'
    - path: output\reports\en_lexdec_english_comparisons_py.csv
    - rows: 1
    - md5: d649cfe19f4343501a6c16c205f472ca
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english_psychopy.py'
    - path: output\experiments\en_lexdec_english_psychopy.py
    - rows: None
    - md5: b45b46a0873de2a2db48569df4827ae0
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english.osexp'
    - path: output\experiments\en_lexdec_english.osexp
    - rows: None
    - md5: 7d28b548200bfee8bf2bc4c99397436c
- **2026-06-13T21:42:26** -- wrote 'en_lexdec_english.html'
    - path: output\experiments\en_lexdec_english.html
    - rows: None
    - md5: 083e77f5788597130471e2452df7d7b5
