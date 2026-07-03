# lexsync run log: en_resample

- Engine: Python 3.13.7
- Started: 2026-07-03T00:10:12
- Finished: 2026-07-03T00:10:12

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03T00:10:12**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03T00:10:12**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03T00:10:12**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-03T00:10:12**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.0002 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.0 (not shown equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.0002 (equivalent)
- **2026-07-03T00:10:12**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.0001 (equivalent)
- **2026-07-03T00:10:12**: wrote 'en_resample_english_stimuli_py.csv'
    - path: output\stimuli\en_resample_english_stimuli_py.csv
    - rows: 240
    - md5: f48c8647fc8f7b6171e32806aee5b0fd
- **2026-07-03T00:10:12**: wrote 'en_resample_english_descriptives_py.csv'
    - path: output\reports\en_resample_english_descriptives_py.csv
    - rows: 8
    - md5: e6ad81211f7bfea3c421af401978a0d0
- **2026-07-03T00:10:12**: wrote 'en_resample_english_comparisons_py.csv'
    - path: output\reports\en_resample_english_comparisons_py.csv
    - rows: 4
    - md5: 871c7931f6e159bd3ade6ea2a06356fc
- **2026-07-03T00:10:12**: wrote 'en_resample_english_psychopy.py'
    - path: output\experiments\en_resample_english_psychopy.py
    - rows: None
    - md5: 869f8aa36d67bd4e99cbfa91fe5e7818
- **2026-07-03T00:10:12**: wrote 'en_resample_english.osexp'
    - path: output\experiments\en_resample_english.osexp
    - rows: None
    - md5: 445b28b98ea666f0fd8d53f47dd660ad
- **2026-07-03T00:10:12**: wrote 'en_resample_english.html'
    - path: output\experiments\en_resample_english.html
    - rows: None
    - md5: b33f72bb48eb42d9a4794ba12c93284f
- **2026-07-03T00:10:12**: wrote 'en_resample_english_datasheet_py.json'
    - path: output\reports\en_resample_english_datasheet_py.json
    - rows: None
    - md5: 89137771aefd69800b4ff2c93c733cc5
- **2026-07-03T00:10:12**: wrote 'en_resample_english_datasheet_py.md'
    - path: output\reports\en_resample_english_datasheet_py.md
    - rows: None
    - md5: b8a899c13cdec18f7616afa720b539a7
