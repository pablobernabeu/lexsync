# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-09 07:15:48.979097
- Finished: 2026-10-09 07:15:50.597834

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:15:48.984633**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:15:49.666841**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:15:49.687391**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09 07:15:49.706009**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-09 07:15:49.750702**: continuous: 'length' correlation with the predictor r = -0.165
- **2026-10-09 07:15:49.75684**: continuous: 'n_density' correlation with the predictor r = -0.049
- **2026-10-09 07:15:49.761615**: continuous: 'old20' correlation with the predictor r = -0.077
- **2026-10-09 07:15:49.802123**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: fcdccc1e813095d734281114acba796a
- **2026-10-09 07:15:49.818187**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 116b7845ef563fc194dbc065dfb7fde8
- **2026-10-09 07:15:49.838149**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: f654bdcb431ebfcdcf053b49444c4408
- **2026-10-09 07:15:50.14202**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: eb33927cb5ffc03ddc21140706f775ac
- **2026-10-09 07:15:50.161263**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: e828442b3ab854bfc29799262417e044
- **2026-10-09 07:15:50.175853**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: d3a78d062bd1e137e29e12cf8fe93318
- **2026-10-09 07:15:50.21373**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: 68560cf1003f06eb724c06ee197aaa3a
- **2026-10-09 07:15:50.237038**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-09 07:15:50.250385**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 762f172d8368b925699ddfc7209ad8ba
- **2026-10-09 07:15:50.570351**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 2339d3f3b9c2be46eab0fad84a4ddf10
- **2026-10-09 07:15:50.583862**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 5a129f3bfe532dc4a579f1a2b9e5b4c1
