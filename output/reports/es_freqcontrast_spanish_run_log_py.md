# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-10T09:34:23
- Finished: 2026-06-10T09:34:24

## Run metadata

- design: es_freqcontrast
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10T09:34:23** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-10T09:34:23** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10T09:34:23** -- pool after filters: 7172 words
    - pool: 7172
- **2026-06-10T09:34:24** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10T09:34:24** -- equivalence low_frequency vs high_frequency on 'length': d = 0.05, TOST p = 0.0024 (equivalent)
- **2026-06-10T09:34:24** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.55, TOST p = 1.0 (not shown equivalent)
- **2026-06-10T09:34:24** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08, TOST p = 0.0041 (equivalent)
- **2026-06-10T09:34:24** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01, TOST p = 0.0011 (equivalent)
- **2026-06-10T09:34:24** -- wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: e1b0b96797ded84315c9f12c62428ef0
- **2026-06-10T09:34:24** -- wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 8
    - md5: 39ab32df0422848e430490693e909303
- **2026-06-10T09:34:24** -- wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 4
    - md5: 2d8db863581d0f6cc5247968444fe81a
- **2026-06-10T09:34:24** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: 974b7fc6e4f93e9f41a78dbb12f8ea38
- **2026-06-10T09:34:24** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: f9b89f62682cf45abfd99a8edfdf313e
