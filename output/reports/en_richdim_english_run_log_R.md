# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-08-07 22:50:05.174917
- Finished: 2026-08-07 22:50:07.782111

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-07 22:50:05.184375**: loading lexicon 'corpora/derived/en.csv'
- **2026-08-07 22:50:06.083613**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-07 22:50:06.105187**: pool after filters: 10205 words
    - pool: 10205
- **2026-08-07 22:50:06.112107**: computing bigram frequency (phonotactic-probability proxy)
- **2026-08-07 22:50:07.23635**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-08-07 22:50:07.27585**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-08-07 22:50:07.281739**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-08-07 22:50:07.288653**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-08-07 22:50:07.295428**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-08-07 22:50:07.301758**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-08-07 22:50:07.307867**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-08-07 22:50:07.366233**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-08-07 22:50:07.396446**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-08-07 22:50:07.42071**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-08-07 22:50:07.578657**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: ef7ebc10229e3d031c02ea4ae56b8fc1
- **2026-08-07 22:50:07.591694**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-08-07 22:50:07.602213**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 8687106952d0bb70ff76bd21d15c25ca
- **2026-08-07 22:50:07.757381**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: 87ae031e67d119d29f32aafe26d8daed
- **2026-08-07 22:50:07.770566**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 26bdc9d443bd420250ce3bade493c8f5
