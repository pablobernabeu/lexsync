# lexsync run log: en_priming_continuous

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:42.461569
- Finished: 2026-08-01 00:33:42.959579

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-08-01 00:33:42.464626**: loading items 'items/priming_pairs_en.csv'
- **2026-08-01 00:33:42.485954**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-08-01 00:33:42.489364**: loading member lexicon 'corpora/derived/en.csv'
- **2026-08-01 00:33:42.760644**: joined word-level norms onto prime and target
- **2026-08-01 00:33:42.765527**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-08-01 00:33:42.772139**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-08-01 00:33:42.774938**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-08-01 00:33:42.777033**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-08-01 00:33:42.792545**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-08-01 00:33:42.802053**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-08-01 00:33:42.811495**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-08-01 00:33:42.85524**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: 0feed505e220db017528a85ea3e2c27d
- **2026-08-01 00:33:42.862849**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: b1487d45d95363d2c90bd864f91ea030
- **2026-08-01 00:33:42.870049**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: 0698986fa2935e67cd12c069f27a61dc
- **2026-08-01 00:33:42.944713**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: acef9bdee64a0241c95997da90b9af3b
- **2026-08-01 00:33:42.952071**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: 5f062975e0f765c2099630f53e8d1f30
