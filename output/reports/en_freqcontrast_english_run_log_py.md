# lexsync run log: en_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-07T14:12:03
- Finished: 2026-06-07T14:12:03

## Run metadata

- design: en_freqcontrast
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-07T14:12:03** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-07T14:12:03** -- lexicon loaded: 10000 words
    - words: 10000
- **2026-06-07T14:12:03** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-07T14:12:03** -- matched 60 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-07T14:12:03** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00, TOST p = 0.0288 (equivalent)
- **2026-06-07T14:12:03** -- equivalence low_frequency vs high_frequency on 'frequency': d = 4.67, TOST p = 1.0 (not shown equivalent)
- **2026-06-07T14:12:03** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.06, TOST p = 0.0462 (equivalent)
- **2026-06-07T14:12:03** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01, TOST p = 0.0305 (equivalent)
- **2026-06-07T14:12:03** -- wrote 'en_freqcontrast_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontrast_english_stimuli_py.csv
    - rows: 60
    - md5: 2f1b0ce2725c9e6245bb1cb3383c5b97
- **2026-06-07T14:12:03** -- wrote 'en_freqcontrast_english_descriptives_py.csv'
    - path: output\reports\en_freqcontrast_english_descriptives_py.csv
    - rows: 8
    - md5: 7b75f6307de6b11528f0d5b962a1b405
- **2026-06-07T14:12:03** -- wrote 'en_freqcontrast_english_comparisons_py.csv'
    - path: output\reports\en_freqcontrast_english_comparisons_py.csv
    - rows: 4
    - md5: 4f32c5bf52ab94f880879c10f0a7dd1d
- **2026-06-07T14:12:03** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output\experiments\en_freqcontrast_english_psychopy.py
    - rows: None
    - md5: 27b3ec7b98b65627694e5947227cc2bb
- **2026-06-07T14:12:03** -- wrote 'en_freqcontrast_english.osexp'
    - path: output\experiments\en_freqcontrast_english.osexp
    - rows: None
    - md5: bb870757c0ea761c3601f4574d6e3e2a
