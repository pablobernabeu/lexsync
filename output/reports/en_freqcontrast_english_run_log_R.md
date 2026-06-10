# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-10 09:31:47.182963
- Finished: 2026-06-10 09:31:49.470563

## Run metadata

- design: en_freqcontrast
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10 09:31:47.19616** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-10 09:31:48.88751** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 09:31:48.902454** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-10 09:31:49.007323** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10 09:31:49.075838** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03, TOST p = 0.002 (equivalent)
- **2026-06-10 09:31:49.0762** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:49.076452** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04, TOST p = 0.002 (equivalent)
- **2026-06-10 09:31:49.076687** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:49.16411** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: 1128d8936a37771df03a5d5368e55427
- **2026-06-10 09:31:49.191726** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-06-10 09:31:49.216472** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: fc4bab33cf10bf2cf9f7f230ef2ed791
- **2026-06-10 09:31:49.423367** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 4eda7d7f36782408f5890ff49e6acf1c
- **2026-06-10 09:31:49.430057** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6c8909238d5f061cf420f994c4fa4b93
