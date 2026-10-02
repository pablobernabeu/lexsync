# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-02 16:42:41.728326
- Finished: 2026-10-02 16:43:00.024558

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:42:41.891314**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 16:42:43.456978**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:42:43.618111**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-02 16:42:44.448611**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-02 16:42:44.987958**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-02 16:42:45.00884**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:42:45.049244**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-10-02 16:42:45.129231**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-02 16:42:45.813105**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-10-02 16:42:47.318099**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: b8426804e118105c1f3a3b5fb3eebc5c
- **2026-10-02 16:42:47.696666**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: b24c79d896435e038f6c0fe2d74e0bb2
- **2026-10-02 16:42:58.272907**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 8854499757ec3dbb9780a892f5750703
- **2026-10-02 16:42:58.458385**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: c836551c0afdfb5bd89811b773c92de3
- **2026-10-02 16:42:58.508717**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 581ed9809e740663d9fa14171c6b6350
- **2026-10-02 16:42:59.746011**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: f99ef4cd75b8e3f52f8f40d4c0448bc6
- **2026-10-02 16:42:59.849064**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: da5fc99eb78db3879227b5af762a5eb9
