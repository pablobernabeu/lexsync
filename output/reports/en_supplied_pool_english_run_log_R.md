# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-09 05:23:45.662203
- Finished: 2026-10-09 05:23:47.860303

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 05:23:45.66946**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-09 05:23:46.731274**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-10-09 05:23:46.748117**: pool after filters: 131 words
    - pool: 131
- **2026-10-09 05:23:46.779643**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-09 05:23:46.827181**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-10-09 05:23:46.836875**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 05:23:46.842309**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-10-09 05:23:46.851663**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-10-09 05:23:46.909684**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-10-09 05:23:46.958533**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-10-09 05:23:47.038649**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: 35a87203c30fae56f60a96fc70db958c
- **2026-10-09 05:23:47.460846**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: 8eb017607397783d6ae7ed6f45e83e33
- **2026-10-09 05:23:47.479432**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: dac639bc44a52d293ab225465556b048
- **2026-10-09 05:23:47.49395**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 42ed2455ca5c3f9284c4ee01ba60f83f
- **2026-10-09 05:23:47.52135**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 4e804ea51bfa10577453bac0659361dc
- **2026-10-09 05:23:47.533648**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-09 05:23:47.552421**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: 15ce90562922debfdc17d77d5e448ebd
- **2026-10-09 05:23:47.802926**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 26c4d40d47be10be5b04eacbb62092cb
- **2026-10-09 05:23:47.83028**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: 9c24cb2e5c59f760aa6bd79af48251f4
