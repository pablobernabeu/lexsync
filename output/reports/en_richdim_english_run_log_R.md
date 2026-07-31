# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-07-31 22:35:17.881855
- Finished: 2026-07-31 22:35:19.051348

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 22:35:17.884284**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 22:35:18.22615**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 22:35:18.235221**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-31 22:35:18.238457**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-31 22:35:18.713654**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 22:35:18.741813**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-07-31 22:35:18.746515**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 22:35:18.749194**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-31 22:35:18.752526**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-31 22:35:18.756522**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-07-31 22:35:18.759862**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-07-31 22:35:18.799293**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-07-31 22:35:18.816899**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-07-31 22:35:18.835121**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-07-31 22:35:18.933199**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: ef7ebc10229e3d031c02ea4ae56b8fc1
- **2026-07-31 22:35:18.941654**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-07-31 22:35:18.949339**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 8687106952d0bb70ff76bd21d15c25ca
- **2026-07-31 22:35:19.034068**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: c526bfbbaaca21b826fc40c688778446
- **2026-07-31 22:35:19.042529**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 409954c83e10726fd98df7df6e02141b
