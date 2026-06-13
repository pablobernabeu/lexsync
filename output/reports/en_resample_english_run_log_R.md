# lexsync run log: en_resample

- Engine: R 4.5.1
- Started: 2026-06-13 22:44:11.114844
- Finished: 2026-06-13 22:44:12.103516

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:44:11.115341** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 22:44:11.565413** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:44:11.57188** -- pool after filters: 10205 words
    - pool: 10205
- **2026-06-13 22:44:11.839855** -- resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-06-13 22:44:11.848331** -- equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-06-13 22:44:11.848769** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [5.17, 5.59], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:44:11.849088** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-06-13 22:44:11.84938** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-06-13 22:44:11.889942** -- wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 6da44764e555ff3b46aa170645468254
- **2026-06-13 22:44:11.901323** -- wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-06-13 22:44:11.909848** -- wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: b26ea43c53a742fbcbad9a6ea85bf684
- **2026-06-13 22:44:12.009868** -- wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: fbc6efe6de7b1fcee921749df9c87460
- **2026-06-13 22:44:12.016856** -- wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: fd435f746afa9f39c0d6bb6c923fefd9
- **2026-06-13 22:44:12.021731** -- wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 07fa7294eafc708dac3cfe6ae42eea1d
- **2026-06-13 22:44:12.091086** -- wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 2c352164cbe296c394df160238aec47a
- **2026-06-13 22:44:12.097802** -- wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: 4494fcd93b8b1773eb6472735cc876e0
