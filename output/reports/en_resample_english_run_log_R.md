# lexsync run log: en_resample

- Engine: R 4.6.1
- Started: 2026-10-02 16:45:17.403106
- Finished: 2026-10-02 16:45:57.117501

## Run metadata

- design: en_resample
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:45:17.528549**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 16:45:19.243976**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:45:19.376658**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-02 16:45:21.422348**: resampled 3 disjoint matched sets (240 items total)
    - conditions: high_frequency, low_frequency
- **2026-10-02 16:45:21.686581**: equivalence low_frequency vs high_frequency on 'length': d = 0.04 [-0.17, 0.26], TOST p = 0.000 (equivalent)
- **2026-10-02 16:45:21.756843**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.38 [4.92, 5.84], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:45:21.763328**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.03 [-0.18, 0.24], TOST p = 0.000 (equivalent)
- **2026-10-02 16:45:21.779978**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.20, 0.23], TOST p = 0.000 (equivalent)
- **2026-10-02 16:45:25.160361**: wrote 'en_resample_english_stimuli_R.csv'
    - path: output/stimuli/en_resample_english_stimuli_R.csv
    - rows: 240
    - md5: 32440a4d5753ad21bf307a389773cd05
- **2026-10-02 16:45:26.054011**: wrote 'en_resample_english_descriptives_R.csv'
    - path: output/reports/en_resample_english_descriptives_R.csv
    - rows: 8
    - md5: 19a03d1d55d822bdbb75c074c9f3bdc0
- **2026-10-02 16:45:27.290092**: wrote 'en_resample_english_comparisons_R.csv'
    - path: output/reports/en_resample_english_comparisons_R.csv
    - rows: 4
    - md5: 70cb67a8e7d4f1d34dc1c7d4d2c6f28e
- **2026-10-02 16:45:53.349304**: wrote 'en_resample_english_psychopy.py'
    - path: output/experiments/en_resample_english_psychopy.py
    - rows: NA
    - md5: 5dfa6ea79de17442db4c7c2c81e2e589
- **2026-10-02 16:45:54.021523**: wrote 'en_resample_english.osexp'
    - path: output/experiments/en_resample_english.osexp
    - rows: NA
    - md5: a2360ba020d77d5201e9ff5b680606e1
- **2026-10-02 16:45:54.38458**: wrote 'en_resample_english.html'
    - path: output/experiments/en_resample_english.html
    - rows: NA
    - md5: 0bbb5250caae16e7265d68ddeee31041
- **2026-10-02 16:45:56.491336**: wrote 'en_resample_english_datasheet_R.json'
    - path: output/reports/en_resample_english_datasheet_R.json
    - rows: NA
    - md5: 0f2435663e5e44ac7b7758373866479d
- **2026-10-02 16:45:56.955641**: wrote 'en_resample_english_datasheet_R.md'
    - path: output/reports/en_resample_english_datasheet_R.md
    - rows: NA
    - md5: d57cdf32114aa8c1ea8c9a1a0d6da84c
