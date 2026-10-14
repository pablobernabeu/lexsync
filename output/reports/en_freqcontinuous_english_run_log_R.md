# lexsync run log: en_freqcontinuous

- Engine: R 4.6.1
- Started: 2026-10-14 22:39:29.355144
- Finished: 2026-10-14 22:39:39.743065

## Run metadata

- design: en_freqcontinuous
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: continuous
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 22:39:29.460445**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 22:39:29.717825**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-14 22:39:32.711892**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 22:39:32.787097**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-14 22:39:32.834371**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-14 22:39:32.99513**: selected 80 items spanning 'frequency' (continuous design)
    - predictor: frequency
- **2026-10-14 22:39:33.168167**: continuous: 'length' correlation with the predictor r = -0.226
- **2026-10-14 22:39:33.208028**: continuous: 'n_density' correlation with the predictor r = 0.301
- **2026-10-14 22:39:33.285816**: continuous: 'old20' correlation with the predictor r = -0.295
- **2026-10-14 22:39:34.096129**: wrote 'en_freqcontinuous_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontinuous_english_stimuli_R.csv
    - rows: 80
    - md5: ef4feebea410e6a1b40610574f3731a9
- **2026-10-14 22:39:34.307258**: wrote 'en_freqcontinuous_english_descriptives_R.csv'
    - path: output/reports/en_freqcontinuous_english_descriptives_R.csv
    - rows: 4
    - md5: 8deba049a56522b5428aa66b8a529ab4
- **2026-10-14 22:39:34.483453**: wrote 'en_freqcontinuous_english_comparisons_R.csv'
    - path: output/reports/en_freqcontinuous_english_comparisons_R.csv
    - rows: 4
    - md5: 6de5d8a105d57d2a0f13418a86c4d4b4
- **2026-10-14 22:39:38.341495**: wrote 'en_freqcontinuous_english_psychopy.py'
    - path: output/experiments/en_freqcontinuous_english_psychopy.py
    - rows: NA
    - md5: 7b6a87b99005ad0f792018406721eb22
- **2026-10-14 22:39:38.374449**: wrote 'en_freqcontinuous_english.osexp'
    - path: output/experiments/en_freqcontinuous_english.osexp
    - rows: NA
    - md5: cb2a75b1c214c4fb75a33e0c64814009
- **2026-10-14 22:39:38.415445**: wrote 'en_freqcontinuous_english.html'
    - path: output/experiments/en_freqcontinuous_english.html
    - rows: NA
    - md5: 3b3c8696dd2be9306085811fa388a039
- **2026-10-14 22:39:38.484695**: wrote 'en_freqcontinuous_english_psychopy.csv'
    - path: output/experiments/en_freqcontinuous_english_psychopy.csv
    - rows: NA
    - md5: bcdd546051f2673d0cf58a96721dca07
- **2026-10-14 22:39:38.572237**: wrote 'en_freqcontinuous_english_opensesame.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame.csv
    - rows: NA
    - md5: 667f183c9bffc66dfd04f92645e07466
- **2026-10-14 22:39:38.65436**: wrote 'en_freqcontinuous_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontinuous_english_opensesame_text.csv
    - rows: NA
    - md5: 639f53f5320babf616c29c70cb1440ea
- **2026-10-14 22:39:39.604994**: wrote 'en_freqcontinuous_english_datasheet_R.json'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.json
    - rows: NA
    - md5: 985690b1efde951f18d7eb9baff5bc30
- **2026-10-14 22:39:39.704281**: wrote 'en_freqcontinuous_english_datasheet_R.md'
    - path: output/reports/en_freqcontinuous_english_datasheet_R.md
    - rows: NA
    - md5: 4812966c414a373e7069bfd01e83bac2
