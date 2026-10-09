# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-09 11:49:09.361605
- Finished: 2026-10-09 11:49:12.461921

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 11:49:09.370214**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-09 11:49:11.418611**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 11:49:11.440338**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-09 11:49:11.459542**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-09 11:49:11.52801**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-09 11:49:11.563005**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-09 11:49:11.570214**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-09 11:49:11.575235**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-09 11:49:11.624753**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-09 11:49:11.64205**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-09 11:49:11.662353**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-09 11:49:11.954312**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: eb33927cb5ffc03ddc21140706f775ac
- **2026-10-09 11:49:11.965513**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: e828442b3ab854bfc29799262417e044
- **2026-10-09 11:49:11.976639**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: 440b9e42199a5e3a58e1820b45ab2a0b
- **2026-10-09 11:49:11.990759**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-09 11:49:11.999108**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-09 11:49:12.007487**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-09 11:49:12.436463**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: c99d21a1350b8fadfbdd85d66a937509
- **2026-10-09 11:49:12.449941**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 4812966c414a373e7069bfd01e83bac2
