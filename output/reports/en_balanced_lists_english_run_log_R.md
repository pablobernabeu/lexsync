# lexsync run log: en_balanced_lists

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:12.558843
- Finished: 2026-07-31 21:48:13.418436

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:12.563124**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 21:48:12.94872**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:12.960049**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-31 21:48:13.030283**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 21:48:13.047182**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.018 (equivalent)
- **2026-07-31 21:48:13.051044**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.68, 5.43], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:13.054199**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.024 (equivalent)
- **2026-07-31 21:48:13.056982**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.025 (equivalent)
- **2026-07-31 21:48:13.0656**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-07-31 21:48:13.102591**: wrote 'en_balanced_lists_english_stimuli_R.csv'
    - path: output/stimuli/en_balanced_lists_english_stimuli_R.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-07-31 21:48:13.124757**: wrote 'en_balanced_lists_english_descriptives_R.csv'
    - path: output/reports/en_balanced_lists_english_descriptives_R.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-07-31 21:48:13.144715**: wrote 'en_balanced_lists_english_comparisons_R.csv'
    - path: output/reports/en_balanced_lists_english_comparisons_R.csv
    - rows: 4
    - md5: 7325496b862eca567636088fd953eea3
- **2026-07-31 21:48:13.284277**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output/experiments/en_balanced_lists_english_psychopy.py
    - rows: NA
    - md5: 27a96761cd60bfc463da1a2a9b6ad759
- **2026-07-31 21:48:13.294966**: wrote 'en_balanced_lists_english.osexp'
    - path: output/experiments/en_balanced_lists_english.osexp
    - rows: NA
    - md5: 22c24451fbd512e17ba8d8f8923ca3d3
- **2026-07-31 21:48:13.302171**: wrote 'en_balanced_lists_english.html'
    - path: output/experiments/en_balanced_lists_english.html
    - rows: NA
    - md5: 923c9ac521c938fc87e92796bfd0c0ae
- **2026-07-31 21:48:13.398171**: wrote 'en_balanced_lists_english_datasheet_R.json'
    - path: output/reports/en_balanced_lists_english_datasheet_R.json
    - rows: NA
    - md5: 700fd8262dc7cebadc113ec514279812
- **2026-07-31 21:48:13.406546**: wrote 'en_balanced_lists_english_datasheet_R.md'
    - path: output/reports/en_balanced_lists_english_datasheet_R.md
    - rows: NA
    - md5: 787b61c83efb138804e799d5366b239c
