# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-15 10:09:42.69313
- Finished: 2026-07-15 10:09:43.873278

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15 10:09:42.698989**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15 10:09:43.211302**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15 10:09:43.224949**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-15 10:09:43.349081**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-15 10:09:43.371253**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-15 10:09:43.375981**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-15 10:09:43.38271**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-15 10:09:43.389878**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-15 10:09:43.47879**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d18c7660e0747e5f8e276af9c27446bf
- **2026-07-15 10:09:43.504923**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-15 10:09:43.526864**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-15 10:09:43.67163**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 7db19120a7d77ee5be2640b68dfff7b3
- **2026-07-15 10:09:43.68343**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
- **2026-07-15 10:09:43.69626**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 9308f54572196f2f21e01f7ac9dbf98b
- **2026-07-15 10:09:43.840284**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 3a916ea135b39874accd4a17d9f95810
- **2026-07-15 10:09:43.854175**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: d25b75f9fda4f716ff8e74bcc91aa665
