# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-10 10:16:42.686366
- Finished: 2026-06-10 10:16:44.701872

## Run metadata

- design: en_freqcontrast
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10 10:16:42.70168** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-10 10:16:43.912192** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 10:16:43.95137** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-10 10:16:44.208756** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10 10:16:44.377511** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-06-10 10:16:44.377866** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-06-10 10:16:44.378125** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-06-10 10:16:44.378345** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-10 10:16:44.451102** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: 1128d8936a37771df03a5d5368e55427
- **2026-06-10 10:16:44.475688** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-06-10 10:16:44.489152** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: e8463b1fa845a23c6a5041ad6e71577b
- **2026-06-10 10:16:44.663932** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 4eda7d7f36782408f5890ff49e6acf1c
- **2026-06-10 10:16:44.670323** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6c8909238d5f061cf420f994c4fa4b93
