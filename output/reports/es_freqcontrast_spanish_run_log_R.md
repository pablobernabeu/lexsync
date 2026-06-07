# lexsync run log: es_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-07 13:15:17.844151
- Finished: 2026-06-07 13:15:17.993122

## Run metadata

- design: es_freqcontrast
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-07 13:15:17.84441** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07 13:15:17.87079** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 13:15:17.872398** -- pool after filters: 7056 words
    - pool: 7056
- **2026-06-07 13:15:17.90395** -- matched 60 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-07 13:15:17.909374** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.029 (equivalent)
- **2026-06-07 13:15:17.909538** -- equivalence low_frequency vs high_frequency on 'frequency': d = 4.93, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 13:15:17.909676** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08, TOST p = 0.057 (not shown equivalent)
- **2026-06-07 13:15:17.909831** -- equivalence low_frequency vs high_frequency on 'old20': d = -0.00, TOST p = 0.030 (equivalent)
- **2026-06-07 13:15:17.926326** -- wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 60
    - md5: b8ae83822a7991b309ab53d0fc1d49ca
- **2026-06-07 13:15:17.936563** -- wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 0e5932a5aba83f1e7fd8a931658c8a10
- **2026-06-07 13:15:17.945502** -- wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 87934165b38908f53510b58d45264604
- **2026-06-07 13:15:17.98303** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff37690ea2bd173a17c321a8612e6955
- **2026-06-07 13:15:17.987613** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 91c86aa5f42e7e6c9f22effb27510dc1
