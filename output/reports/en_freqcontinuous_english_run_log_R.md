# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-13 22:45:00.950154
- Finished: 2026-10-13 22:45:09.497175

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 22:45:00.962215**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 22:45:00.980015**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 22:45:03.510723**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 22:45:03.556517**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 22:45:03.592235**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-13 22:45:03.720417**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-13 22:45:03.772206**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-13 22:45:03.780413**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-13 22:45:03.791284**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-13 22:45:04.130185**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-13 22:45:04.191832**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-13 22:45:04.295836**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-13 22:45:07.026596**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: d54f92216dbe1e818aacd2b90e5696c8
- **2026-10-13 22:45:07.122134**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: 03fe67ab77ff362a886bb51b6df8b1db
- **2026-10-13 22:45:07.261518**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: c38377ae1837451602b8f7a5a7d47ec1
- **2026-10-13 22:45:07.548087**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-13 22:45:07.615834**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-13 22:45:07.694957**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-13 22:45:09.363654**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 7564c57462187c661f5b781dba32df06
- **2026-10-13 22:45:09.417283**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 4812966c414a373e7069bfd01e83bac2
