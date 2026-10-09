# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-10-09 04:44:03.886854
- Finished: 2026-10-09 04:44:11.501357

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09 04:44:03.910763**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 04:44:05.00532**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 04:44:05.055154**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-09 04:44:05.079167**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-09 04:44:07.00204**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 04:44:07.309585**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-10-09 04:44:07.394434**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [4.90, 6.24], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 04:44:07.483449**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-09 04:44:07.568523**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-09 04:44:07.618117**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-10-09 04:44:07.638912**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-09 04:44:08.482593**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-10-09 04:44:08.542839**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-10-09 04:44:08.588994**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: c6e0f0a19b0b176fdd5a9ad80946e658
- **2026-10-09 04:44:10.861088**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: 79705e247031e6758a2fef5a662c65d3
- **2026-10-09 04:44:10.880375**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: 982f3b21c018cbdb9debd5bb68e8ef0a
- **2026-10-09 04:44:10.900989**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 9d4096b27141d54195d82e47385b4097
- **2026-10-09 04:44:10.955424**: wrote 'en_richdim_english_psychopy.csv'
    - path: output/experiments/en_richdim_english_psychopy.csv
    - rows: NA
    - md5: 93a834aa073d733b6c36eff12c552218
- **2026-10-09 04:44:10.998485**: wrote 'en_richdim_english_opensesame.csv'
    - path: output/experiments/en_richdim_english_opensesame.csv
    - rows: NA
    - md5: 688d6883920616305069d8117f36a179
- **2026-10-09 04:44:11.06005**: wrote 'en_richdim_english_opensesame_text.csv'
    - path: output/experiments/en_richdim_english_opensesame_text.csv
    - rows: NA
    - md5: 9611480010e396d73933a022393170df
- **2026-10-09 04:44:11.437738**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: 59ed96d1bb77bbf5c372c1c4124e34e5
- **2026-10-09 04:44:11.473836**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 5c689e894af8276e548552e8e2d5258b
