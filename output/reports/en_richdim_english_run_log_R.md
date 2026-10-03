# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-10-03 13:12:04.781285
- Finished: 2026-10-03 13:12:17.080967

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 13:12:04.802006**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 13:12:06.807167**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 13:12:07.094746**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-03 13:12:07.121353**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-03 13:12:09.003092**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03 13:12:09.100717**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-10-03 13:12:09.117951**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [4.90, 6.24], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:12:09.138727**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-03 13:12:09.14888**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-03 13:12:09.167891**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-10-03 13:12:09.184479**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-03 13:12:09.592845**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-10-03 13:12:09.660179**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-10-03 13:12:09.715611**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: c6e0f0a19b0b176fdd5a9ad80946e658
- **2026-10-03 13:12:15.565524**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: 7ef41675cf8ff87ec3ead289bbf4e0ba
- **2026-10-03 13:12:15.615854**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: ff4c4663416e45f9cbb882d29f4b1fc3
- **2026-10-03 13:12:15.660856**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 7d6bb7eca498071ab597b4db69130242
- **2026-10-03 13:12:15.760144**: wrote 'en_richdim_english_psychopy.csv'
    - path: output/experiments/en_richdim_english_psychopy.csv
    - rows: NA
    - md5: 93a834aa073d733b6c36eff12c552218
- **2026-10-03 13:12:15.839094**: wrote 'en_richdim_english_opensesame.csv'
    - path: output/experiments/en_richdim_english_opensesame.csv
    - rows: NA
    - md5: 688d6883920616305069d8117f36a179
- **2026-10-03 13:12:15.938282**: wrote 'en_richdim_english_opensesame_text.csv'
    - path: output/experiments/en_richdim_english_opensesame_text.csv
    - rows: NA
    - md5: 9611480010e396d73933a022393170df
- **2026-10-03 13:12:16.777646**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: d2e17a4904ef08edf767c48d7222a0dd
- **2026-10-03 13:12:16.946745**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 8430adb7ec920a1085e37afd41d76ea8
