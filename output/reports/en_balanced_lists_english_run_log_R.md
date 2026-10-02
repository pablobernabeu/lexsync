# lexsync run log: en_balanced_lists

- Engine: R 4.6.1
- Started: 2026-10-02 12:18:29.998835
- Finished: 2026-10-02 12:18:42.606869

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 12:18:30.116512**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 12:18:32.219221**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 12:18:32.333567**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-02 12:18:33.389757**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-02 12:18:34.265849**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.018 (equivalent)
- **2026-10-02 12:18:34.398612**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.29, 5.82], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 12:18:34.518639**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.024 (equivalent)
- **2026-10-02 12:18:34.559719**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.025 (equivalent)
- **2026-10-02 12:18:34.614904**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-10-02 12:18:35.875141**: wrote 'en_balanced_lists_english_stimuli_R.csv'
    - path: output/stimuli/en_balanced_lists_english_stimuli_R.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-10-02 12:18:36.205204**: wrote 'en_balanced_lists_english_descriptives_R.csv'
    - path: output/reports/en_balanced_lists_english_descriptives_R.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-10-02 12:18:36.464857**: wrote 'en_balanced_lists_english_comparisons_R.csv'
    - path: output/reports/en_balanced_lists_english_comparisons_R.csv
    - rows: 4
    - md5: 488dd8d3168996fb298b771d15a79bd2
- **2026-10-02 12:18:39.810377**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output/experiments/en_balanced_lists_english_psychopy.py
    - rows: NA
    - md5: 27a96761cd60bfc463da1a2a9b6ad759
- **2026-10-02 12:18:39.905577**: wrote 'en_balanced_lists_english.osexp'
    - path: output/experiments/en_balanced_lists_english.osexp
    - rows: NA
    - md5: 22c24451fbd512e17ba8d8f8923ca3d3
- **2026-10-02 12:18:39.980119**: wrote 'en_balanced_lists_english.html'
    - path: output/experiments/en_balanced_lists_english.html
    - rows: NA
    - md5: 5d72eac05e183404c3048ac4b51a50b2
- **2026-10-02 12:18:42.053496**: wrote 'en_balanced_lists_english_datasheet_R.json'
    - path: output/reports/en_balanced_lists_english_datasheet_R.json
    - rows: NA
    - md5: 7e3ff08a9c99d24d3a68a4083895009b
- **2026-10-02 12:18:42.428786**: wrote 'en_balanced_lists_english_datasheet_R.md'
    - path: output/reports/en_balanced_lists_english_datasheet_R.md
    - rows: NA
    - md5: 0a1ccd651f193aa7288b83e5cb766a51
