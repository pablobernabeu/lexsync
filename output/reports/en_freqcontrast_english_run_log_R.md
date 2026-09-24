# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-09-24 16:59:47.934892
- Finished: 2026-09-24 16:59:49.958498

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 16:59:47.940532**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-24 16:59:48.785611**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-24 16:59:48.825362**: pool after filters: 7230 words
    - pool: 7230
- **2026-09-24 16:59:49.167453**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-24 16:59:49.205857**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-09-24 16:59:49.212183**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.000 (not shown equivalent)
- **2026-09-24 16:59:49.221811**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-09-24 16:59:49.228273**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-09-24 16:59:49.300065**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-09-24 16:59:49.325028**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: b8426804e118105c1f3a3b5fb3eebc5c
- **2026-09-24 16:59:49.352866**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: b24c79d896435e038f6c0fe2d74e0bb2
- **2026-09-24 16:59:49.660202**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 8854499757ec3dbb9780a892f5750703
- **2026-09-24 16:59:49.674001**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-09-24 16:59:49.686838**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 581ed9809e740663d9fa14171c6b6350
- **2026-09-24 16:59:49.909513**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 2996f7608a6fb0eca9482c9e954110c6
- **2026-09-24 16:59:49.940469**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: f451fabd4c680162e1d310657ce87180
