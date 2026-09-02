# lexsync run log: en_balanced_lists

- Engine: Python 3.11.15
- Started: 2026-09-02T19:25:42
- Finished: 2026-09-02T19:25:42

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02T19:25:42**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02T19:25:42**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02T19:25:42**: pool after filters: 7230 words
    - pool: 7230
- **2026-09-02T19:25:42**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02T19:25:42**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.0178 (equivalent)
- **2026-09-02T19:25:42**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.68, 5.43], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02T19:25:42**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.0237 (equivalent)
- **2026-09-02T19:25:42**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.0246 (equivalent)
- **2026-09-02T19:25:42**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_stimuli_py.csv'
    - path: output/stimuli/en_balanced_lists_english_stimuli_py.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_descriptives_py.csv'
    - path: output/reports/en_balanced_lists_english_descriptives_py.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_comparisons_py.csv'
    - path: output/reports/en_balanced_lists_english_comparisons_py.csv
    - rows: 4
    - md5: 7325496b862eca567636088fd953eea3
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output/experiments/en_balanced_lists_english_psychopy.py
    - rows: None
    - md5: 41be5eeb97dc527b447d744044dc77af
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english.osexp'
    - path: output/experiments/en_balanced_lists_english.osexp
    - rows: None
    - md5: 528aaa56475514b689ea406391f17ca5
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english.html'
    - path: output/experiments/en_balanced_lists_english.html
    - rows: None
    - md5: f0dcba240e4f7be0ee324c4c9c074acd
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_datasheet_py.json'
    - path: output/reports/en_balanced_lists_english_datasheet_py.json
    - rows: None
    - md5: 18acb0d939ef38b4142b7a0a010b81c2
- **2026-09-02T19:25:42**: wrote 'en_balanced_lists_english_datasheet_py.md'
    - path: output/reports/en_balanced_lists_english_datasheet_py.md
    - rows: None
    - md5: aba8b4f101835765ff5ac926fa914152
