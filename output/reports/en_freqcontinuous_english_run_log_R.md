# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:29.560932
- Finished: 2026-08-01 00:33:30.247788

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous

## Steps

- **2026-08-01 00:33:29.56562**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-01 00:33:29.921694**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-01 00:33:29.938536**: pool after filters: 7230 words
    - pool: 7230
- **2026-08-01 00:33:29.951133**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-08-01 00:33:29.966236**: continuous: 'length' correlation with the predictor r = -0.165
- **2026-08-01 00:33:29.970271**: continuous: 'n_density' correlation with the predictor r = -0.049
- **2026-08-01 00:33:29.975413**: continuous: 'old20' correlation with the predictor r = -0.077
- **2026-08-01 00:33:30.004961**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: fcdccc1e813095d734281114acba796a
- **2026-08-01 00:33:30.018722**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 116b7845ef563fc194dbc065dfb7fde8
- **2026-08-01 00:33:30.034768**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: f654bdcb431ebfcdcf053b49444c4408
- **2026-08-01 00:33:30.123633**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: d7a770830721a210513e1c393beb2066
- **2026-08-01 00:33:30.133051**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: d9953f16653d5e11612d5e3b49f63686
- **2026-08-01 00:33:30.14132**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: bd05cb434d52b7dd568c35505287acc0
- **2026-08-01 00:33:30.223963**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 5214529d596f8c5e852f0decb8554a6b
- **2026-08-01 00:33:30.237976**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 623d9336bb299d50dcf7af0a78805a79
