# lexsync run log: en_priming_continuous

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:26.557636
- Finished: 2026-07-31 21:48:27.380077

## Run metadata

- design: en_priming_continuous
- language: english
- paradigm: priming
- source: table
- seed: 2026
- mode: continuous

## Steps

- **2026-07-31 21:48:26.56328**: loading items 'items/priming_pairs_en.csv'
- **2026-07-31 21:48:26.589685**: loaded 12 items across 2 conditions
    - conditions: related, unrelated
- **2026-07-31 21:48:26.595411**: loading member lexicon 'corpora/derived/en.csv'
- **2026-07-31 21:48:27.072815**: joined word-level norms onto prime and target
- **2026-07-31 21:48:27.080552**: computed relational dimensions (pair.lev, pair.overlap)
- **2026-07-31 21:48:27.09631**: selected 8 pairs spanning 'target.frequency' (12 eligible)
    - sets: 8
    - eligible: 12
- **2026-07-31 21:48:27.101031**: continuous: 'target.length' correlation with the predictor r = -0.292
- **2026-07-31 21:48:27.105176**: continuous: 'pair.overlap' correlation with the predictor r = -0.227
- **2026-07-31 21:48:27.132298**: wrote 'en_priming_continuous_english_stimuli_R.csv'
    - path: output/stimuli/en_priming_continuous_english_stimuli_R.csv
    - rows: 16
    - md5: 8a2bb9907edffd68183a1ed5f6c23030
- **2026-07-31 21:48:27.151921**: wrote 'en_priming_continuous_english_descriptives_R.csv'
    - path: output/reports/en_priming_continuous_english_descriptives_R.csv
    - rows: 3
    - md5: 1cae97ee35a1cce758b47ec9cf803b60
- **2026-07-31 21:48:27.170119**: wrote 'en_priming_continuous_english_comparisons_R.csv'
    - path: output/reports/en_priming_continuous_english_comparisons_R.csv
    - rows: 3
    - md5: 5f9405c3b989e0e9fa2d0672cd43c720
- **2026-07-31 21:48:27.237897**: wrote 'en_priming_continuous_english_psychopy.py'
    - path: output/experiments/en_priming_continuous_english_psychopy.py
    - rows: NA
    - md5: 0feed505e220db017528a85ea3e2c27d
- **2026-07-31 21:48:27.249352**: wrote 'en_priming_continuous_english.osexp'
    - path: output/experiments/en_priming_continuous_english.osexp
    - rows: NA
    - md5: b1487d45d95363d2c90bd864f91ea030
- **2026-07-31 21:48:27.261107**: wrote 'en_priming_continuous_english.html'
    - path: output/experiments/en_priming_continuous_english.html
    - rows: NA
    - md5: cadd8f52f5fe92c1d76b02fa33703c91
- **2026-07-31 21:48:27.361043**: wrote 'en_priming_continuous_english_datasheet_R.json'
    - path: output/reports/en_priming_continuous_english_datasheet_R.json
    - rows: NA
    - md5: a46dfe02992af8108aaa317f45e1a9a0
- **2026-07-31 21:48:27.371005**: wrote 'en_priming_continuous_english_datasheet_R.md'
    - path: output/reports/en_priming_continuous_english_datasheet_R.md
    - rows: NA
    - md5: 5f062975e0f765c2099630f53e8d1f30
