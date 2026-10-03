# lexsync run log: en_balanced_lists

- Engine: R 4.6.1
- Started: 2026-10-03 09:46:18.599255
- Finished: 2026-10-03 09:46:36.525209

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 09:46:18.650811**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 09:46:22.055606**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 09:46:22.278326**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-03 09:46:23.481826**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03 09:46:24.097424**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.018 (equivalent)
- **2026-10-03 09:46:24.16769**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.29, 5.82], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 09:46:24.209651**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.024 (equivalent)
- **2026-10-03 09:46:24.288749**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.025 (equivalent)
- **2026-10-03 09:46:24.366454**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-10-03 09:46:25.869559**: wrote 'en_balanced_lists_english_stimuli_R.csv'
    - path: output/stimuli/en_balanced_lists_english_stimuli_R.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-10-03 09:46:26.099294**: wrote 'en_balanced_lists_english_descriptives_R.csv'
    - path: output/reports/en_balanced_lists_english_descriptives_R.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-10-03 09:46:26.309119**: wrote 'en_balanced_lists_english_comparisons_R.csv'
    - path: output/reports/en_balanced_lists_english_comparisons_R.csv
    - rows: 4
    - md5: 488dd8d3168996fb298b771d15a79bd2
- **2026-10-03 09:46:32.664698**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output/experiments/en_balanced_lists_english_psychopy.py
    - rows: NA
    - md5: 27a96761cd60bfc463da1a2a9b6ad759
- **2026-10-03 09:46:32.78394**: wrote 'en_balanced_lists_english.osexp'
    - path: output/experiments/en_balanced_lists_english.osexp
    - rows: NA
    - md5: b3f65c1089d250662965e2a12edb455f
- **2026-10-03 09:46:32.895298**: wrote 'en_balanced_lists_english.html'
    - path: output/experiments/en_balanced_lists_english.html
    - rows: NA
    - md5: 5d72eac05e183404c3048ac4b51a50b2
- **2026-10-03 09:46:35.60582**: wrote 'en_balanced_lists_english_datasheet_R.json'
    - path: output/reports/en_balanced_lists_english_datasheet_R.json
    - rows: NA
    - md5: 3a3c49caa7830f54fb6cf50b689aadc2
- **2026-10-03 09:46:36.122332**: wrote 'en_balanced_lists_english_datasheet_R.md'
    - path: output/reports/en_balanced_lists_english_datasheet_R.md
    - rows: NA
    - md5: 723705d73cf6f140d5b423142927a956
