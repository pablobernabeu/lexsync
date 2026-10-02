# lexsync run log: en_priming_continuous

- Engine: R 4.6.1
- Started: 2026-10-03 00:33:13.199508
- Finished: 2026-10-03 00:33:37.934867

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-10-03 00:33:13.274314**: loading items 'items/priming_pairs_en.csv'
- **2026-10-03 00:33:13.778658**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-10-03 00:33:14.58711**: loading member lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:33:19.331949**: joined word-level norms onto prime and target
- **2026-10-03 00:33:19.85503**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-10-03 00:33:21.016969**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-10-03 00:33:21.844037**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-10-03 00:33:22.824432**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-10-03 00:33:24.286913**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-10-03 00:33:25.720148**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-10-03 00:33:26.370364**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-10-03 00:33:31.262219**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: 0feed505e220db017528a85ea3e2c27d
- **2026-10-03 00:33:31.513515**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: 542e450ae871b28bf8181d2f76fa66bf
- **2026-10-03 00:33:32.224102**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: 0698986fa2935e67cd12c069f27a61dc
- **2026-10-03 00:33:36.874795**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: ae08387e6a9192eeef7cea0953c2b933
- **2026-10-03 00:33:37.364783**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: fccf12d27c35b3c53bb6bc58f6aa4ad2
