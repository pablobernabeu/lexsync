# lexsync run log: en_priming_continuous

- Engine: R 4.6.1
- Started: 2026-08-07 22:50:00.019686
- Finished: 2026-08-07 22:50:00.849422

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-08-07 22:50:00.022867**: loading items 'items/priming_pairs_en.csv'
- **2026-08-07 22:50:00.042863**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-08-07 22:50:00.047616**: loading member lexicon 'corpora/derived/en.csv'
- **2026-08-07 22:50:00.522394**: joined word-level norms onto prime and target
- **2026-08-07 22:50:00.529598**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-08-07 22:50:00.542201**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-08-07 22:50:00.548506**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-08-07 22:50:00.554018**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-08-07 22:50:00.584366**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-08-07 22:50:00.605118**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-08-07 22:50:00.624336**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-08-07 22:50:00.697308**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: 0feed505e220db017528a85ea3e2c27d
- **2026-08-07 22:50:00.708684**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: b1487d45d95363d2c90bd864f91ea030
- **2026-08-07 22:50:00.716773**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: 0698986fa2935e67cd12c069f27a61dc
- **2026-08-07 22:50:00.830595**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: c19df617b6397ca03759e0cde974b476
- **2026-08-07 22:50:00.841227**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: 016fa2b05ea7707d51668b4d2b133168
