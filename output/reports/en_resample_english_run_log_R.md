# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-07-17 01:38:49.009965
- Finished: 2026-07-17 01:38:50.504244

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-17 01:38:49.014797**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-17 01:38:49.534592**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-17 01:38:49.552122**: pool after filters: 10205 words
    - pool: 10205
- **2026-07-17 01:38:49.815499**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-07-17 01:38:49.843153**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-07-17 01:38:49.84973**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-07-17 01:38:49.855536**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-07-17 01:38:49.86142**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-07-17 01:38:49.93867**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-07-17 01:38:49.96159**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-07-17 01:38:49.985599**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 2d175506dbcccca4ee454044f2581c7e
- **2026-07-17 01:38:50.289273**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 2eb83593c4677cf94ebff2c15223bce5
- **2026-07-17 01:38:50.304455**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2da54b9b205406c3555856687996ccd
- **2026-07-17 01:38:50.317661**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 49ac85e23221649870bb780ab2f53410
- **2026-07-17 01:38:50.479987**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: ba16cfdc87d3b0e6bf1575f0e916eb26
- **2026-07-17 01:38:50.492528**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: 72a0022ecbe0268f3bd1fb3221d6419a
