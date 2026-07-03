# lexsync run log: en_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-03 00:08:56.243109
- Finished: 2026-07-03 00:08:56.832706

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 00:08:56.246231**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03 00:08:56.498388**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 00:08:56.50911**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-03 00:08:56.568283**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-03 00:08:56.578806**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-03 00:08:56.583538**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 00:08:56.587275**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-03 00:08:56.591832**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-03 00:08:56.617978**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d18c7660e0747e5f8e276af9c27446bf
- **2026-07-03 00:08:56.634508**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-03 00:08:56.649432**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: e8463b1fa845a23c6a5041ad6e71577b
- **2026-07-03 00:08:56.744638**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 7db19120a7d77ee5be2640b68dfff7b3
- **2026-07-03 00:08:56.752516**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
- **2026-07-03 00:08:56.760471**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 9308f54572196f2f21e01f7ac9dbf98b
- **2026-07-03 00:08:56.814625**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: b5688733705686dceb731d8c32222de6
- **2026-07-03 00:08:56.824426**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 7a70858ff4db1fbabade0c37537ae3b8
