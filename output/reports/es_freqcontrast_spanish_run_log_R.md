# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:30.773192
- Finished: 2026-07-31 21:48:31.553982

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:30.776808**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-31 21:48:31.103367**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:31.120847**: pool after filters: 7172 words
    - pool: 7172
- **2026-07-31 21:48:31.231383**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 21:48:31.254468**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-07-31 21:48:31.262318**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:31.26961**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-07-31 21:48:31.276197**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-31 21:48:31.327198**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-07-31 21:48:31.343697**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-07-31 21:48:31.358584**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: b2dd610e72f3335fc3c6c01ff1bfa950
- **2026-07-31 21:48:31.448176**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: d9625b06edd4c9140cf5b98b60f431ea
- **2026-07-31 21:48:31.458125**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-07-31 21:48:31.464501**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 0879fbd018bbf978029ccbb1c23992d4
- **2026-07-31 21:48:31.536808**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 69b1b330612bc5cb7a4c68b40ded38ae
- **2026-07-31 21:48:31.544838**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 2298b6b8629a20c3793cc96eed36ba9d
