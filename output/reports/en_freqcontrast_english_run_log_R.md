# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-07 14:11:44.344769
- Finished: 2026-06-07 14:11:47.160692

## Run metadata

- design: en_freqcontrast
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-07 14:11:44.357446** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-07 14:11:46.25044** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 14:11:46.268379** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-07 14:11:46.463913** -- matched 60 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-07 14:11:46.613245** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.029 (equivalent)
- **2026-06-07 14:11:46.613995** -- equivalence low_frequency vs high_frequency on 'frequency': d = 4.67, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:46.614473** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.06, TOST p = 0.046 (equivalent)
- **2026-06-07 14:11:46.614911** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01, TOST p = 0.030 (equivalent)
- **2026-06-07 14:11:46.704479** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 60
    - md5: ca046e6a973074fbf7d07896c745b49e
- **2026-06-07 14:11:46.761349** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: 904de20fe8e6a9a6df605dd2bca567b4
- **2026-06-07 14:11:46.795353** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 97d4d192b49ffc241a162bebac2134ac
- **2026-06-07 14:11:47.095748** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 4eda7d7f36782408f5890ff49e6acf1c
- **2026-06-07 14:11:47.110055** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 1d4e1a7a64d46798dd1605edf58328a1
