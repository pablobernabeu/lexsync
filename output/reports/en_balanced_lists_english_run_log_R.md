# lexsync run log: en_balanced_lists

- Engine: R 4.3.3
- Started: 2026-09-02 19:24:53.833502
- Finished: 2026-09-02 19:24:54.417764

## Run metadata

- design: en_balanced_lists
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:24:53.833752**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:24:54.101987**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:24:54.11125**: pool after filters: 7230 words
    - pool: 7230
- **2026-09-02 19:24:54.18882**: matched 80 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:24:54.197806**: equivalence low_frequency vs high_frequency on 'length': d = 0.02 [-0.35, 0.39], TOST p = 0.0178 (equivalent)
- **2026-09-02 19:24:54.198087**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.05 [4.68, 5.43], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:54.198233**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.05 [-0.32, 0.42], TOST p = 0.0237 (equivalent)
- **2026-09-02 19:24:54.198361**: equivalence low_frequency vs high_frequency on 'old20': d = 0.05 [-0.32, 0.43], TOST p = 0.0246 (equivalent)
- **2026-09-02 19:24:54.276657**: balanced 40 item sets across 4 lists on length, n_density, old20, frequency: cost 1121480 -> 53820 in 10 swap(s)
    - cost_before: 1121480
    - cost_after: 53820
    - swaps: 10
- **2026-09-02 19:24:54.301948**: wrote 'en_balanced_lists_english_stimuli_R.csv'
    - path: output/stimuli/en_balanced_lists_english_stimuli_R.csv
    - rows: 80
    - md5: ea6027af81e16cad2979e4e8c1afe7a2
- **2026-09-02 19:24:54.303874**: wrote 'en_balanced_lists_english_descriptives_R.csv'
    - path: output/reports/en_balanced_lists_english_descriptives_R.csv
    - rows: 8
    - md5: 0773a3bf93269e14568726dfea032629
- **2026-09-02 19:24:54.305493**: wrote 'en_balanced_lists_english_comparisons_R.csv'
    - path: output/reports/en_balanced_lists_english_comparisons_R.csv
    - rows: 4
    - md5: 7325496b862eca567636088fd953eea3
- **2026-09-02 19:24:54.382876**: wrote 'en_balanced_lists_english_psychopy.py'
    - path: output/experiments/en_balanced_lists_english_psychopy.py
    - rows: NA
    - md5: 41be5eeb97dc527b447d744044dc77af
- **2026-09-02 19:24:54.383086**: wrote 'en_balanced_lists_english.osexp'
    - path: output/experiments/en_balanced_lists_english.osexp
    - rows: NA
    - md5: 528aaa56475514b689ea406391f17ca5
- **2026-09-02 19:24:54.383177**: wrote 'en_balanced_lists_english.html'
    - path: output/experiments/en_balanced_lists_english.html
    - rows: NA
    - md5: f0dcba240e4f7be0ee324c4c9c074acd
- **2026-09-02 19:24:54.417428**: wrote 'en_balanced_lists_english_datasheet_R.json'
    - path: output/reports/en_balanced_lists_english_datasheet_R.json
    - rows: NA
    - md5: 7ced6b1b5eef5b73c94dd4fddf40a111
- **2026-09-02 19:24:54.417624**: wrote 'en_balanced_lists_english_datasheet_R.md'
    - path: output/reports/en_balanced_lists_english_datasheet_R.md
    - rows: NA
    - md5: eef8de7a7a5db1ac42903e81cbbc9432
