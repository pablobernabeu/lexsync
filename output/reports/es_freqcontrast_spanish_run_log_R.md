# lexsync run log: es_freqcontrast

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:03.694753
- Finished: 2026-09-02 19:25:04.132976

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:03.695101**: loading lexicon 'corpora/derived/es.csv'
- **2026-09-02 19:25:03.934178**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:25:03.93941**: pool after filters: 7172 words
    - pool: 7172
- **2026-09-02 19:25:04.064741**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:25:04.075151**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-09-02 19:25:04.075394**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:04.075536**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-09-02 19:25:04.075675**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-09-02 19:25:04.085662**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-09-02 19:25:04.088243**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-09-02 19:25:04.090322**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: b2dd610e72f3335fc3c6c01ff1bfa950
- **2026-09-02 19:25:04.111796**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: cf939a5ab2e1111de770fafab0bf066e
- **2026-09-02 19:25:04.112147**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-09-02 19:25:04.112327**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 020966107246b4140ff11d810d1cf00c
- **2026-09-02 19:25:04.13253**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 1e134d86815f22fe9ed9761aa0b59571
- **2026-09-02 19:25:04.132772**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 6b30bcafa7f37a6c359e8710c2f90f14
