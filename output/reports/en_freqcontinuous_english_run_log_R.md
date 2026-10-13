# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-13 18:16:21.371914
- Finished: 2026-10-13 18:16:25.280907

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:16:21.380308**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:16:21.386609**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 18:16:23.420516**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 18:16:23.455695**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 18:16:23.483015**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-13 18:16:23.594159**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-13 18:16:23.660981**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-13 18:16:23.685178**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-13 18:16:23.697079**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-13 18:16:23.813365**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-13 18:16:23.862603**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-13 18:16:23.988214**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-13 18:16:24.657864**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: 35acb3fede3885c18f4a4ca8f3d2af07
- **2026-10-13 18:16:24.677136**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: 3897b11c2828e2027cea7d2af9fb81e0
- **2026-10-13 18:16:24.695843**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: c38377ae1837451602b8f7a5a7d47ec1
- **2026-10-13 18:16:24.717324**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-13 18:16:24.733063**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-13 18:16:24.747741**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-13 18:16:25.225397**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 100de92f64cad3b6d6e87c8f82598075
- **2026-10-13 18:16:25.250065**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 4812966c414a373e7069bfd01e83bac2
