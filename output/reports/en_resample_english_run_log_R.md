# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-07-16 16:37:30.71494
- Finished: 2026-07-16 16:37:34.471115

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16 16:37:30.725722**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-16 16:37:32.431751**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-16 16:37:32.470466**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-16 16:37:33.330873**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-16 16:37:33.372757**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-07-16 16:37:33.387068**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-07-16 16:37:33.396735**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-07-16 16:37:33.407141**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-07-16 16:37:33.548767**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 6da44764e555ff3b46aa170645468254
- **2026-07-16 16:37:33.596569**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-07-16 16:37:33.638568**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-07-16 16:37:34.117143**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 2eb83593c4677cf94ebff2c15223bce5
- **2026-07-16 16:37:34.136186**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-07-16 16:37:34.15655**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: fa356eaa20f9a56a71e9af0b65aee3fb
- **2026-07-16 16:37:34.423874**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 4a358a9307089b8e39c7d437ce648c44
- **2026-07-16 16:37:34.44969**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: a6d8ab6e108a868bd02d1e3ef2bec9a1
