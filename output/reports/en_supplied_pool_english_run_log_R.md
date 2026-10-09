# lexsync run log: en_supplied_pool

- Engine: R 4.6.1
- Started: 2026-10-09 07:51:03.099354
- Finished: 2026-10-09 07:51:04.532828

## Run metadata

- design: en_supplied_pool
- language: english
- paradigm: factorial
- source: pool
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:51:03.103004**: loading supplied pool 'items/pool_en_concrete_nouns.csv'
- **2026-10-09 07:51:03.734858**: supplied pool: 131 words (dimensions from 'corpora/derived/en.csv')
    - words: 131
    - lexicon: corpora/derived/en.csv
- **2026-10-09 07:51:03.740011**: pool after filters: 131 words
    - pool: 131
- **2026-10-09 07:51:03.754409**: matched 40 items across 2 conditions
    - conditions: higher_frequency, lower_frequency
- **2026-10-09 07:51:04.003819**: equivalence lower_frequency vs higher_frequency on 'length': d = -0.11 [-0.64, 0.42], TOST p = 0.112 (not shown equivalent)
- **2026-10-09 07:51:04.008338**: equivalence lower_frequency vs higher_frequency on 'frequency': d = 3.53 [2.68, 4.38], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:51:04.012184**: equivalence lower_frequency vs higher_frequency on 'n_density': d = 0.13 [-0.40, 0.66], TOST p = 0.124 (not shown equivalent)
- **2026-10-09 07:51:04.016185**: equivalence lower_frequency vs higher_frequency on 'old20': d = -0.24 [-0.78, 0.29], TOST p = 0.209 (not shown equivalent)
- **2026-10-09 07:51:04.020327**: equivalence lower_frequency vs higher_frequency on 'n_syllables': d = 0.12 [-0.42, 0.65], TOST p = 0.117 (not shown equivalent)
- **2026-10-09 07:51:04.024348**: equivalence lower_frequency vs higher_frequency on 'bigram_freq': d = 0.28 [-0.25, 0.82], TOST p = 0.249 (not shown equivalent)
- **2026-10-09 07:51:04.051101**: wrote 'en_supplied_pool_english_stimuli_R.csv'
    - path: output/stimuli/en_supplied_pool_english_stimuli_R.csv
    - rows: 40
    - md5: 5f9123dce72c73b1f532a5b393c0ee55
- **2026-10-09 07:51:04.068494**: wrote 'en_supplied_pool_english_descriptives_R.csv'
    - path: output/reports/en_supplied_pool_english_descriptives_R.csv
    - rows: 12
    - md5: 80d68fb20b74bbf30aa1b5582453a92d
- **2026-10-09 07:51:04.083816**: wrote 'en_supplied_pool_english_comparisons_R.csv'
    - path: output/reports/en_supplied_pool_english_comparisons_R.csv
    - rows: 6
    - md5: 2d37214222aa3a4e3fe7ede093a61ed9
- **2026-10-09 07:51:04.288181**: wrote 'en_supplied_pool_english_psychopy.py'
    - path: output/experiments/en_supplied_pool_english_psychopy.py
    - rows: NA
    - md5: 8eb017607397783d6ae7ed6f45e83e33
- **2026-10-09 07:51:04.301215**: wrote 'en_supplied_pool_english.osexp'
    - path: output/experiments/en_supplied_pool_english.osexp
    - rows: NA
    - md5: dac639bc44a52d293ab225465556b048
- **2026-10-09 07:51:04.31177**: wrote 'en_supplied_pool_english.html'
    - path: output/experiments/en_supplied_pool_english.html
    - rows: NA
    - md5: 42ed2455ca5c3f9284c4ee01ba60f83f
- **2026-10-09 07:51:04.325455**: wrote 'en_supplied_pool_english_psychopy.csv'
    - path: output/experiments/en_supplied_pool_english_psychopy.csv
    - rows: NA
    - md5: 4e804ea51bfa10577453bac0659361dc
- **2026-10-09 07:51:04.333859**: wrote 'en_supplied_pool_english_opensesame.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame.csv
    - rows: NA
    - md5: 49ccbbdf46789be5a80e46fa6ac4da45
- **2026-10-09 07:51:04.340485**: wrote 'en_supplied_pool_english_opensesame_text.csv'
    - path: output/experiments/en_supplied_pool_english_opensesame_text.csv
    - rows: NA
    - md5: 15ce90562922debfdc17d77d5e448ebd
- **2026-10-09 07:51:04.509515**: wrote 'en_supplied_pool_english_datasheet_R.json'
    - path: output/reports/en_supplied_pool_english_datasheet_R.json
    - rows: NA
    - md5: 73055994d3769bd907f53f0891317668
- **2026-10-09 07:51:04.522001**: wrote 'en_supplied_pool_english_datasheet_R.md'
    - path: output/reports/en_supplied_pool_english_datasheet_R.md
    - rows: NA
    - md5: a697d38caceafe9179c93b46a80d1968
