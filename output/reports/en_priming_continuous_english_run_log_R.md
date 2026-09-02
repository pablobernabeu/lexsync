# lexsync run log: en_priming_continuous

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:01.460427
- Finished: 2026-09-02 19:25:01.826728

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-09-02 19:25:01.460731**: loading items 'items/priming_pairs_en.csv'
- **2026-09-02 19:25:01.474159**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-09-02 19:25:01.474324**: loading member lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:25:01.736064**: joined word-level norms onto prime and target
- **2026-09-02 19:25:01.754142**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-09-02 19:25:01.786892**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-09-02 19:25:01.787314**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-09-02 19:25:01.787466**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-09-02 19:25:01.797257**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-09-02 19:25:01.799264**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-09-02 19:25:01.80087**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-09-02 19:25:01.812723**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: aac2cafa051a6fd293b7253394443b85
- **2026-09-02 19:25:01.812934**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: 89aef8ebf0507a24a77b87c0b558d282
- **2026-09-02 19:25:01.813046**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: 6f6d724ad414c20ffef97d234c9f3c68
- **2026-09-02 19:25:01.826402**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: a1511bdc0567084aee44c78017b54f2c
- **2026-09-02 19:25:01.826577**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: 6d0b7c770ade3ea4b08f621d31f5ae3a
