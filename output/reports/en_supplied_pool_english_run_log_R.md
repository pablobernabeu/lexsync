# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-03 09:49:56.546092
- Finished: 2026-10-03 09:50:07.68456

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 09:49:56.57789**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-03 09:49:59.115066**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-10-03 09:49:59.146112**: pool after filters: 131 words
    - pool: 131
- **2026-10-03 09:49:59.223054**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-03 09:49:59.370259**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-10-03 09:49:59.420285**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 09:49:59.490471**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-10-03 09:49:59.554439**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-10-03 09:50:00.477333**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-10-03 09:50:00.909938**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 8
    - md5: 084478a4ea1b2982354267964701bdf0
- **2026-10-03 09:50:01.460735**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 4
    - md5: 35a87203c30fae56f60a96fc70db958c
- **2026-10-03 09:50:05.969369**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: f2a329e0d8bf81270a33cc700ab8d858
- **2026-10-03 09:50:06.106475**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: bcb603fe84755a2829b1b8733d10b18f
- **2026-10-03 09:50:06.211391**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 96361646fdb301915726601716042d9e
- **2026-10-03 09:50:07.293703**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: e5c15e1f382f39dc044da6e1c14803e8
- **2026-10-03 09:50:07.531031**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: f833c93d6341a10bbb1f663e8fe1c324
