# lexsync run log: en_priming_continuous

- Engine: R 4.6.1
- Started: 2026-07-31 22:35:15.811715
- Finished: 2026-07-31 22:35:16.570346

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-07-31 22:35:15.815324**: loading items 'items/priming_pairs_en.csv'
- **2026-07-31 22:35:15.843253**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-07-31 22:35:15.846916**: loading member lexicon 'corpora/derived/en.csv'
- **2026-07-31 22:35:16.300438**: joined word-level norms onto prime and target
- **2026-07-31 22:35:16.307884**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-07-31 22:35:16.31712**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-07-31 22:35:16.321387**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-07-31 22:35:16.327925**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-07-31 22:35:16.350831**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-07-31 22:35:16.366765**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-07-31 22:35:16.383911**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-07-31 22:35:16.451859**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: 0feed505e220db017528a85ea3e2c27d
- **2026-07-31 22:35:16.462861**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: b1487d45d95363d2c90bd864f91ea030
- **2026-07-31 22:35:16.473493**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: 0698986fa2935e67cd12c069f27a61dc
- **2026-07-31 22:35:16.552358**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: acef9bdee64a0241c95997da90b9af3b
- **2026-07-31 22:35:16.5636**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: 5f062975e0f765c2099630f53e8d1f30
