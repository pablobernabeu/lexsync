# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-07-17T01:54:51
- Finished: 2026-07-17T01:54:52

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-17T01:54:51**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-17T01:54:51**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-17T01:54:51**: pool after filters: 7172 words
    - pool: 7172
- **2026-07-17T01:54:52**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-17T01:54:52**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-07-17T01:54:52**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.0 (not shown equivalent)
- **2026-07-17T01:54:52**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-07-17T01:54:52**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: 6821614ec1f62013ded3b3bbacb889cb
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 8
    - md5: 7a918123c58421c1edf79b8bff45e077
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 4
    - md5: 648d1921053ac5bbf2a2f493c706db46
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: c544fe2ffdb8ca01f7f6af650f68b990
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish.html'
    - path: output\experiments\es_freqcontrast_spanish.html
    - rows: None
    - md5: e2e9f25abec7fa13f8712289a5687232
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_datasheet_py.json'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.json
    - rows: None
    - md5: c9737a125640309b7186b0f80d92aec1
- **2026-07-17T01:54:52**: wrote 'es_freqcontrast_spanish_datasheet_py.md'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.md
    - rows: None
    - md5: 70df0de189de685226c4f5f5115ec54b
