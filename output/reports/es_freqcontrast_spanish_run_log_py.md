# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-07T13:33:56
- Finished: 2026-06-07T13:33:57

## Run metadata

- design: es_freqcontrast
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-07T13:33:56** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07T13:33:57** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07T13:33:57** -- pool after filters: 7056 words
    - pool: 7056
- **2026-06-07T13:33:57** -- matched 60 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-07T13:33:57** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.0288 (equivalent)
- **2026-06-07T13:33:57** -- equivalence low_frequency vs high_frequency on 'frequency': d = 4.93, TOST p = 1.0 (not shown equivalent)
- **2026-06-07T13:33:57** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.09, TOST p = 0.0568 (not shown equivalent)
- **2026-06-07T13:33:57** -- equivalence low_frequency vs high_frequency on 'old20': d = -0.01, TOST p = 0.0301 (equivalent)
- **2026-06-07T13:33:57** -- wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 60
    - md5: 6e395ef103ac0451244ea5f6c13a62ca
- **2026-06-07T13:33:57** -- wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 8
    - md5: 70238314545734bdcda4a77ca2b9384d
- **2026-06-07T13:33:57** -- wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 4
    - md5: 9f176e670e70ccb04d5339ca9511daaa
- **2026-06-07T13:33:57** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: 974b7fc6e4f93e9f41a78dbb12f8ea38
- **2026-06-07T13:33:57** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: b6179bee586793eeadc97d16df8de9af
