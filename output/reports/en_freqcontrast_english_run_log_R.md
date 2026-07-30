# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-30 15:20:32.501863
- Finished: 2026-07-30 15:20:33.674522

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-30 15:20:32.505395**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-30 15:20:33.00761**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-30 15:20:33.028988**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-30 15:20:33.228846**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-30 15:20:33.255895**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-30 15:20:33.263623**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-30 15:20:33.268622**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-30 15:20:33.273447**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-30 15:20:33.331889**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-07-30 15:20:33.353236**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-30 15:20:33.36994**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-30 15:20:33.518013**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 8854499757ec3dbb9780a892f5750703
- **2026-07-30 15:20:33.527735**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-07-30 15:20:33.537104**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 3ecc68184d4f0c7d99124f4683d44fdb
- **2026-07-30 15:20:33.656147**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 872323e08290af7c31b9f112ab59d1f6
- **2026-07-30 15:20:33.666396**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 063549071c95785b03f5a5886e920e8e
