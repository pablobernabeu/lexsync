# lexsync run log: es_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-07 14:11:47.891804
- Finished: 2026-06-07 14:11:48.594882

## Run metadata

- design: es_freqcontrast
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-07 14:11:47.892554** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-07 14:11:47.987714** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07 14:11:47.996499** -- pool after filters: 7056 words
    - pool: 7056
- **2026-06-07 14:11:48.112626** -- matched 60 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-07 14:11:48.146098** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.029 (equivalent)
- **2026-06-07 14:11:48.14654** -- equivalence low_frequency vs high_frequency on 'frequency': d = 4.93, TOST p = 1.000 (not shown equivalent)
- **2026-06-07 14:11:48.147027** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08, TOST p = 0.057 (not shown equivalent)
- **2026-06-07 14:11:48.147268** -- equivalence low_frequency vs high_frequency on 'old20': d = -0.00, TOST p = 0.030 (equivalent)
- **2026-06-07 14:11:48.23584** -- wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 60
    - md5: b8ae83822a7991b309ab53d0fc1d49ca
- **2026-06-07 14:11:48.294874** -- wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 0e5932a5aba83f1e7fd8a931658c8a10
- **2026-06-07 14:11:48.350371** -- wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 87934165b38908f53510b58d45264604
- **2026-06-07 14:11:48.576258** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff37690ea2bd173a17c321a8612e6955
- **2026-06-07 14:11:48.585376** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 91c86aa5f42e7e6c9f22effb27510dc1
