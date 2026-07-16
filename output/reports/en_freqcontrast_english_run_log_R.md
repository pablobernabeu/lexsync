# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-16 16:36:54.900722
- Finished: 2026-07-16 16:36:57.36196

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16 16:36:54.91109**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-16 16:36:56.128748**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-16 16:36:56.169511**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-16 16:36:56.523837**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-16 16:36:56.571628**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-16 16:36:56.583481**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-16 16:36:56.593478**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-16 16:36:56.601479**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-16 16:36:56.709869**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d18c7660e0747e5f8e276af9c27446bf
- **2026-07-16 16:36:56.751727**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-16 16:36:56.796299**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-16 16:36:57.054887**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 865d0243fecb10f504bc9d87bf69d583
- **2026-07-16 16:36:57.074231**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-07-16 16:36:57.094848**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 13d6f01bf8ad04b2d05ab30913a619cb
- **2026-07-16 16:36:57.324408**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 15aae6918a3696837138f6129bb69feb
- **2026-07-16 16:36:57.344106**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: d25b75f9fda4f716ff8e74bcc91aa665
