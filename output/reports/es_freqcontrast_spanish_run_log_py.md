# lexsync run log: es_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-03T09:52:56
- Finished: 2026-10-03T09:53:01

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03T09:52:56**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-03T09:52:58**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03T09:52:58**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-03T09:52:59**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03T09:52:59**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.0024 (equivalent)
- **2026-10-03T09:52:59**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.0 (not shown equivalent)
- **2026-10-03T09:52:59**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.0041 (equivalent)
- **2026-10-03T09:52:59**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.0011 (equivalent)
- **2026-10-03T09:52:59**: wrote 'es_freqcontrast_spanish_stimuli_py.csv'
    - path: output\stimuli\es_freqcontrast_spanish_stimuli_py.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-03T09:53:00**: wrote 'es_freqcontrast_spanish_descriptives_py.csv'
    - path: output\reports\es_freqcontrast_spanish_descriptives_py.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-10-03T09:53:00**: wrote 'es_freqcontrast_spanish_comparisons_py.csv'
    - path: output\reports\es_freqcontrast_spanish_comparisons_py.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-10-03T09:53:00**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output\experiments\es_freqcontrast_spanish_psychopy.py
    - rows: None
    - md5: d9625b06edd4c9140cf5b98b60f431ea
- **2026-10-03T09:53:01**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output\experiments\es_freqcontrast_spanish.osexp
    - rows: None
    - md5: 77125398dc3b65a41cd504d5005526fc
- **2026-10-03T09:53:01**: wrote 'es_freqcontrast_spanish.html'
    - path: output\experiments\es_freqcontrast_spanish.html
    - rows: None
    - md5: 0124c382fbd275f9afd0f71f5a983094
- **2026-10-03T09:53:01**: wrote 'es_freqcontrast_spanish_datasheet_py.json'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.json
    - rows: None
    - md5: a8adfdf74be5738eade486bc6ee03c35
- **2026-10-03T09:53:01**: wrote 'es_freqcontrast_spanish_datasheet_py.md'
    - path: output\reports\es_freqcontrast_spanish_datasheet_py.md
    - rows: None
    - md5: 3bf98ddcd241244cc69954fb8672b923
