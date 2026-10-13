# lexsync run log: en_freqcontinuous

- Engine: Python 3.13.7
- Started: 2026-10-13T11:13:14
- Finished: 2026-10-13T11:13:16

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T11:13:14**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13T11:13:16**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T11:13:16**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13T11:13:16**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-13T11:13:16**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-13T11:13:16**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-13T11:13:16**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-13T11:13:16**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontinuous_english_stimuli_py.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_descriptives_py.csv'
    - path: output\reports\en_freqcontinuous_english_descriptives_py.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_comparisons_py.csv'
    - path: output\reports\en_freqcontinuous_english_comparisons_py.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output\experiments\en_freqcontinuous_english_psychopy.py
    - rows: None
    - md5: eb33927cb5ffc03ddc21140706f775ac
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english.osexp'
    - path: output\experiments\en_freqcontinuous_english.osexp
    - rows: None
    - md5: e828442b3ab854bfc29799262417e044
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english.html'
    - path: output\experiments\en_freqcontinuous_english.html
    - rows: None
    - md5: 440b9e42199a5e3a58e1820b45ab2a0b
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output\experiments\en_freqcontinuous_english_psychopy.csv
    - rows: None
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output\experiments\en_freqcontinuous_english_opensesame.csv
    - rows: None
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output\experiments\en_freqcontinuous_english_opensesame_text.csv
    - rows: None
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_datasheet_py.json'
    - path: output\reports\en_freqcontinuous_english_datasheet_py.json
    - rows: None
    - md5: c51933e3cb8de4b2955313c691ff5c6e
- **2026-10-13T11:13:16**: wrote 'en_freqcontinuous_english_datasheet_py.md'
    - path: output\reports\en_freqcontinuous_english_datasheet_py.md
    - rows: None
    - md5: 041891a7fe7aa3151f6e103e9b949d80
