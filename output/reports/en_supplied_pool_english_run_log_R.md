# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-03 13:12:21.33968
- Finished: 2026-10-03 13:12:28.865261

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 13:12:21.373335**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-03 13:12:23.319267**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-10-03 13:12:23.39816**: pool after filters: 131 words
    - pool: 131
- **2026-10-03 13:12:23.52195**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-03 13:12:23.587697**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-10-03 13:12:23.635321**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:12:23.652954**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-10-03 13:12:23.767185**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-10-03 13:12:24.668376**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-10-03 13:12:24.811161**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-10-03 13:12:25.321811**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: 35a87203c30fae56f60a96fc70db958c
- **2026-10-03 13:12:27.563471**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: d14f62653fbfb75213da3c387293d3c9
- **2026-10-03 13:12:27.731394**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: bcb603fe84755a2829b1b8733d10b18f
- **2026-10-03 13:12:27.876289**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: a500681bbd6539bc0365cd46f5ca49d0
- **2026-10-03 13:12:28.026649**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 4e804ea51bfa10577453bac0659361dc
- **2026-10-03 13:12:28.147491**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-03 13:12:28.194847**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: 15ce90562922debfdc17d77d5e448ebd
- **2026-10-03 13:12:28.775084**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: fa9a08823e297418ca7280d3db4ac70a
- **2026-10-03 13:12:28.818604**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: f833c93d6341a10bbb1f663e8fe1c324
