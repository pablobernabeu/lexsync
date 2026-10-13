# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-13 18:17:56.838558
- Finished: 2026-10-13 18:18:00.916482

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 18:17:56.848239**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13 18:17:56.854126**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-13 18:17:59.569828**: supplied pool: 131 words (dimensions from 'corpora/derived/en_v2.csv')
    - words: 131
    - lexicon: corpora/derived/en_v2.csv
- **2026-10-13 18:17:59.578368**: pool after filters: 131 words
    - pool: 131
- **2026-10-13 18:17:59.611127**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-13 18:18:00.082153**: equivalence lower_frequency vs higher_frequency on 'length': d = 0.00 [-0.53, 0.53], TOST p = 0.061 (not shown equivalent)
- **2026-10-13 18:18:00.094678**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.51 [2.66, 4.36], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 18:18:00.114166**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.18 [-0.36, 0.71], TOST p = 0.157 (not shown equivalent)
- **2026-10-13 18:18:00.129476**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.14 [-0.67, 0.39], TOST p = 0.131 (not shown equivalent)
- **2026-10-13 18:18:00.146571**: equivalence lower_frequency vs higher_frequency on 'n_syllables': d = 0.14 [-0.40, 0.67], TOST p = 0.130 (not shown equivalent)
- **2026-10-13 18:18:00.164017**: equivalence lower_frequency vs higher_frequency on 'bigram_freq': d = 0.62 [0.08, 1.17], TOST p = 0.651 (not shown equivalent)
- **2026-10-13 18:18:00.233594**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 326f0865b15a1420c09af4c155fd1368
- **2026-10-13 18:18:00.288044**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 12
    - md5: ad9da0a92065faccb3515559bbc5b1e0
- **2026-10-13 18:18:00.33565**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 6
    - md5: a134fbdbbdb5624cea325f608fb54911
- **2026-10-13 18:18:00.61978**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: d2dc46d1c85b919335664e8be12e6b55
- **2026-10-13 18:18:00.632967**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: af300a0c1b6d8adc866bf5decde3bb14
- **2026-10-13 18:18:00.647367**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: f5e62275a2e8be492533cfc98938e711
- **2026-10-13 18:18:00.666197**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 91cf227f235cdce35ad90c1c8201a432
- **2026-10-13 18:18:00.677077**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-13 18:18:00.686935**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: c95cb1f947b24b55ffe98ed33aaae5cb
- **2026-10-13 18:18:00.889415**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: c6dd71dc7418ca69de5ea4f87c0e9572
- **2026-10-13 18:18:00.903305**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 644b3aceee9131be21b7ed73aac3d4c6
