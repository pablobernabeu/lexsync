# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-14 01:24:31.463506
- Finished: 2026-10-14 01:24:34.113926

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 01:24:31.472731**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 01:24:31.4769**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-14 01:24:33.063288**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 01:24:33.081316**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-14 01:24:33.1067**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-14 01:24:33.178769**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-14 01:24:33.216194**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-14 01:24:33.232908**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-14 01:24:33.23929**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-14 01:24:33.276161**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-14 01:24:33.292581**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-14 01:24:33.31061**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-14 01:24:33.56759**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: 8c825450505800f7f2e641df1f51286a
- **2026-10-14 01:24:33.57824**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: cb2a75b1c214c4fb75a33e0c64814009
- **2026-10-14 01:24:33.588551**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: 25e6eb7bf55b6d7b912027bd35f8b691
- **2026-10-14 01:24:33.602875**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-14 01:24:33.659244**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-14 01:24:33.683833**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-14 01:24:34.094013**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 41762820077199546ce58ebd00fe50bd
- **2026-10-14 01:24:34.105713**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 4812966c414a373e7069bfd01e83bac2
