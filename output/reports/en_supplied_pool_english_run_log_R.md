# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-09 03:41:34.524252
- Finished: 2026-10-09 03:41:37.39135

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 03:41:34.552641**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-09 03:41:36.42**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-10-09 03:41:36.427456**: pool after filters: 131 words
    - pool: 131
- **2026-10-09 03:41:36.458424**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-09 03:41:36.497095**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-10-09 03:41:36.509029**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 03:41:36.519466**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-10-09 03:41:36.530514**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-10-09 03:41:36.587357**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-10-09 03:41:36.629374**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-10-09 03:41:36.663119**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: 35a87203c30fae56f60a96fc70db958c
- **2026-10-09 03:41:37.0048**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: d14f62653fbfb75213da3c387293d3c9
- **2026-10-09 03:41:37.038332**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: bcb603fe84755a2829b1b8733d10b18f
- **2026-10-09 03:41:37.056176**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: a500681bbd6539bc0365cd46f5ca49d0
- **2026-10-09 03:41:37.078333**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 4e804ea51bfa10577453bac0659361dc
- **2026-10-09 03:41:37.094664**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-09 03:41:37.109196**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: 15ce90562922debfdc17d77d5e448ebd
- **2026-10-09 03:41:37.336373**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 3c695f34a0b9ac69e5ba53fcbb7170fb
- **2026-10-09 03:41:37.368813**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: ff0baf9ec5cc31c836294531cb0ecf59
