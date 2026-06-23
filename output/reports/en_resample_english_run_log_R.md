# lexsync run log: en_resample

- Engine: R 4.6.0
- Started: 2026-06-23 10:18:53.460572
- Finished: 2026-06-23 10:18:54.978905

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-23 10:18:53.466732**: loading lexicon 'corpora/derived/en.csv'
- **2026-06-23 10:18:54.052134**: lexicon loaded: 30000 words
    - words: 30000
- **2026-06-23 10:18:54.080086**: pool after filters: 10205 words
    - pool: 10205
- **2026-06-23 10:18:54.506441**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-06-23 10:18:54.527989**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-06-23 10:18:54.534795**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-06-23 10:18:54.541916**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-06-23 10:18:54.548429**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-06-23 10:18:54.615223**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 6da44764e555ff3b46aa170645468254
- **2026-06-23 10:18:54.640124**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-06-23 10:18:54.660794**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: b26ea43c53a742fbcbad9a6ea85bf684
- **2026-06-23 10:18:54.809385**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 432c4e76e3c3af46c95d2713a738bb6b
- **2026-06-23 10:18:54.820134**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: fd435f746afa9f39c0d6bb6c923fefd9
- **2026-06-23 10:18:54.833043**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 07fa7294eafc708dac3cfe6ae42eea1d
- **2026-06-23 10:18:54.941021**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 59074e7e4a914702ad599d03c8bc2d8b
- **2026-06-23 10:18:54.959601**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: f26f3e13b854c0a4371cb5cece14f538
