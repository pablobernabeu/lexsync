# lexsync run log: en_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-07-16T16:39:48
- Finished: 2026-07-16T16:39:49

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16T16:39:48**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-16T16:39:48**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-16T16:39:48**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-16T16:39:49**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-16T16:39:49**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.0016 (equivalent)
- **2026-07-16T16:39:49**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.0 (not shown equivalent)
- **2026-07-16T16:39:49**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-16T16:39:49**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.0011 (equivalent)
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontrast_english_stimuli_py.csv
    - rows: 160
    - md5: 85498ced86ee9dd0889fc8570991186c
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_descriptives_py.csv'
    - path: output\reports\en_freqcontrast_english_descriptives_py.csv
    - rows: 8
    - md5: 7135fab77082b025f982081da8777bc5
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_comparisons_py.csv'
    - path: output\reports\en_freqcontrast_english_comparisons_py.csv
    - rows: 4
    - md5: 570416a536eb213c030aefa27c72d2eb
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output\experiments\en_freqcontrast_english_psychopy.py
    - rows: None
    - md5: 865d0243fecb10f504bc9d87bf69d583
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english.osexp'
    - path: output\experiments\en_freqcontrast_english.osexp
    - rows: None
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english.html'
    - path: output\experiments\en_freqcontrast_english.html
    - rows: None
    - md5: ec31acafc9d6bef8932ab76fabf94179
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_datasheet_py.json'
    - path: output\reports\en_freqcontrast_english_datasheet_py.json
    - rows: None
    - md5: c27061a3708659afa69b82b74f0701a4
- **2026-07-16T16:39:49**: wrote 'en_freqcontrast_english_datasheet_py.md'
    - path: output\reports\en_freqcontrast_english_datasheet_py.md
    - rows: None
    - md5: 8e768d442cc210275d792709fc9c7524
