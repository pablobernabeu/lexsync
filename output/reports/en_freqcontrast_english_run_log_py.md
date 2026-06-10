# lexsync run log: en_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-06-10T10:20:18
- Finished: 2026-06-10T10:20:19

## Run metadata

- design: en_freqcontrast
- language: english
- lexicon: corpora/derived/en.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10T10:20:18** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-10T10:20:18** -- lexicon loaded: 29999 words
    - words: 29999
- **2026-06-10T10:20:18** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-10T10:20:19** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10T10:20:19** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.0016 (equivalent)
- **2026-06-10T10:20:19** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.0 (not shown equivalent)
- **2026-06-10T10:20:19** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-06-10T10:20:19** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.0011 (equivalent)
- **2026-06-10T10:20:19** -- wrote 'en_freqcontrast_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontrast_english_stimuli_py.csv
    - rows: 160
    - md5: f64ddd7c0f4757669ca5a5ffcba253f5
- **2026-06-10T10:20:19** -- wrote 'en_freqcontrast_english_descriptives_py.csv'
    - path: output\reports\en_freqcontrast_english_descriptives_py.csv
    - rows: 8
    - md5: 1e991a9aa06cd9738dda397b4e79ec2e
- **2026-06-10T10:20:19** -- wrote 'en_freqcontrast_english_comparisons_py.csv'
    - path: output\reports\en_freqcontrast_english_comparisons_py.csv
    - rows: 4
    - md5: 1fa5eb727b5785fb26ec76141f161aba
- **2026-06-10T10:20:19** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output\experiments\en_freqcontrast_english_psychopy.py
    - rows: None
    - md5: 27b3ec7b98b65627694e5947227cc2bb
- **2026-06-10T10:20:19** -- wrote 'en_freqcontrast_english.osexp'
    - path: output\experiments\en_freqcontrast_english.osexp
    - rows: None
    - md5: 90ef51b116d969128463384d3362e1dd
