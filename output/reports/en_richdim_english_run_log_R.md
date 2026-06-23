# lexsync run log: en_richdim

- Engine: R 4.6.0
- Started: 2026-06-23 10:18:55.020315
- Finished: 2026-06-23 10:18:57.790095

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:18:55.035442**: loading lexicon 'corpora/derived/en.csv'
- **2026-06-23 10:18:55.976063**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-23 10:18:55.997706**: pool after filters: 10205 words
    - pool: 10205
- **2026-06-23 10:18:56.004467**: computing bigram frequency (phonotactic-probability proxy)
- **2026-06-23 10:18:57.135848**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-23 10:18:57.184614**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-06-23 10:18:57.194754**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [5.27, 5.88], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:57.206742**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-06-23 10:18:57.216899**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-06-23 10:18:57.225077**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-06-23 10:18:57.235375**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-06-23 10:18:57.298863**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: b54d2cdc1945522b1b84c2dec9b9fda3
- **2026-06-23 10:18:57.332121**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-06-23 10:18:57.358684**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: 162f35b51b1447f53296db33e95dcff5
- **2026-06-23 10:18:57.510118**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: d5cb85fe8274db49ba39aae66f65e3bc
- **2026-06-23 10:18:57.527012**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: 3f5dd9da82e0df1f1029fcd672638b81
- **2026-06-23 10:18:57.54407**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 34c49a3b2a987cd56be507e91cb8289b
- **2026-06-23 10:18:57.754204**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: dc536b0af932697d9723809a09e2e116
- **2026-06-23 10:18:57.774538**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 62159ebeabc7d112d28c67e7490c6776
