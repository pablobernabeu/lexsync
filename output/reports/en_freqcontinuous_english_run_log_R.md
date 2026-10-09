# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-09 09:52:36.98391
- Finished: 2026-10-09 09:52:38.216857

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:52:36.987664**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 09:52:37.50678**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:52:37.52026**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09 09:52:37.588447**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-09 09:52:37.615087**: continuous: 'length' correlation with the predictor r = -0.165
- **2026-10-09 09:52:37.61954**: continuous: 'n_density' correlation with the predictor r = -0.049
- **2026-10-09 09:52:37.6235**: continuous: 'old20' correlation with the predictor r = -0.077
- **2026-10-09 09:52:37.662333**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: fcdccc1e813095d734281114acba796a
- **2026-10-09 09:52:37.676503**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 116b7845ef563fc194dbc065dfb7fde8
- **2026-10-09 09:52:37.690107**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: ef45bfdbc98ac7737cbf767eda7339e3
- **2026-10-09 09:52:37.881828**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: eb33927cb5ffc03ddc21140706f775ac
- **2026-10-09 09:52:37.891266**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: e828442b3ab854bfc29799262417e044
- **2026-10-09 09:52:37.900525**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: d3a78d062bd1e137e29e12cf8fe93318
- **2026-10-09 09:52:37.913685**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: 68560cf1003f06eb724c06ee197aaa3a
- **2026-10-09 09:52:37.921582**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-09 09:52:37.928214**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 762f172d8368b925699ddfc7209ad8ba
- **2026-10-09 09:52:38.195136**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: d670ea0321d33b297b67c8365afe19c7
- **2026-10-09 09:52:38.206674**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 5a087ea4068b3fc0cabb6680f0294cde
