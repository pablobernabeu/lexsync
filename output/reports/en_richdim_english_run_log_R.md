# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:28.905732
- Finished: 2026-07-31 21:48:29.955958

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:28.909037**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 21:48:29.223497**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:29.234455**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-31 21:48:29.238217**: computing bigram frequency (phonotactic-probability proxy)
- **2026-07-31 21:48:29.646758**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 21:48:29.664663**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-07-31 21:48:29.668479**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:29.671441**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-31 21:48:29.675433**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-07-31 21:48:29.678949**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-07-31 21:48:29.682744**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-07-31 21:48:29.715981**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-07-31 21:48:29.732393**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-07-31 21:48:29.748731**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 62e0dfb6b39db4370ecd6a062c6113fb
- **2026-07-31 21:48:29.830721**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: ef7ebc10229e3d031c02ea4ae56b8fc1
- **2026-07-31 21:48:29.839511**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-07-31 21:48:29.847509**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: f749f8e6e1b425461fda816c42c9ec27
- **2026-07-31 21:48:29.932289**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: fce4649f8a2b27ae0978a1002946e29b
- **2026-07-31 21:48:29.942057**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 409954c83e10726fd98df7df6e02141b
