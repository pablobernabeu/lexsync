# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-10-09 03:41:25.870073
- Finished: 2026-10-09 03:41:32.834562

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 03:41:25.878352**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 03:41:27.532062**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 03:41:27.723776**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-09 03:41:27.891802**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-09 03:41:29.964294**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 03:41:30.20581**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-10-09 03:41:30.23062**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [4.90, 6.24], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 03:41:30.249305**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-09 03:41:30.26899**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-09 03:41:30.278117**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-10-09 03:41:30.285258**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-09 03:41:30.432009**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-10-09 03:41:30.516955**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-10-09 03:41:30.582384**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: c6e0f0a19b0b176fdd5a9ad80946e658
- **2026-10-09 03:41:32.188406**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: 7ef41675cf8ff87ec3ead289bbf4e0ba
- **2026-10-09 03:41:32.22912**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: ff4c4663416e45f9cbb882d29f4b1fc3
- **2026-10-09 03:41:32.265449**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 7d6bb7eca498071ab597b4db69130242
- **2026-10-09 03:41:32.31785**: wrote 'en_richdim_english_psychopy.csv'
    - path: output/experiments/en_richdim_english_psychopy.csv
    - rows: NA
    - md5: 93a834aa073d733b6c36eff12c552218
- **2026-10-09 03:41:32.358843**: wrote 'en_richdim_english_opensesame.csv'
    - path: output/experiments/en_richdim_english_opensesame.csv
    - rows: NA
    - md5: 688d6883920616305069d8117f36a179
- **2026-10-09 03:41:32.384919**: wrote 'en_richdim_english_opensesame_text.csv'
    - path: output/experiments/en_richdim_english_opensesame_text.csv
    - rows: NA
    - md5: 9611480010e396d73933a022393170df
- **2026-10-09 03:41:32.758992**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: 08db26bb30f493357b71df74bec7a3dc
- **2026-10-09 03:41:32.803159**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 773da452c4be60b525fac72d6e2956db
