# lexsync run log: en_balanced_lists

- Engine: Python 3.13.7
- Started: 2026-09-23T23:14:38
- Finished: 2026-09-23T23:14:39

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-23T23:14:38**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-23T23:14:38**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-23T23:14:38**: pool after filters: 7230 words
    - pool: 7230
- **2026-09-23T23:14:38**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-23T23:14:38**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.0178 (equivalent)
- **2026-09-23T23:14:38**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.29, 5.82], TOST p = 1.0 (not shown equivalent)
- **2026-09-23T23:14:38**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.0237 (equivalent)
- **2026-09-23T23:14:38**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.0246 (equivalent)
- **2026-09-23T23:14:39**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_stimuli_py.csv'
    - path: output\stimuli\en_balanced_lists_english_stimuli_py.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_descriptives_py.csv'
    - path: output\reports\en_balanced_lists_english_descriptives_py.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_comparisons_py.csv'
    - path: output\reports\en_balanced_lists_english_comparisons_py.csv
    - rows: 4
    - md5: 488dd8d3168996fb298b771d15a79bd2
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output\experiments\en_balanced_lists_english_psychopy.py
    - rows: None
    - md5: 27a96761cd60bfc463da1a2a9b6ad759
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english.osexp'
    - path: output\experiments\en_balanced_lists_english.osexp
    - rows: None
    - md5: 22c24451fbd512e17ba8d8f8923ca3d3
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english.html'
    - path: output\experiments\en_balanced_lists_english.html
    - rows: None
    - md5: 5d72eac05e183404c3048ac4b51a50b2
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_datasheet_py.json'
    - path: output\reports\en_balanced_lists_english_datasheet_py.json
    - rows: None
    - md5: e189b38c692cc33d043da872cb02ced0
- **2026-09-23T23:14:39**: wrote 'en_balanced_lists_english_datasheet_py.md'
    - path: output\reports\en_balanced_lists_english_datasheet_py.md
    - rows: None
    - md5: 78eb2973895b3204e344502d1837d324
