# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 07:15:50.654041
- Finished: 2026-10-09 07:15:52.698876

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:15:50.661577**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:15:51.456958**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:15:51.472915**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09 07:15:51.795632**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 07:15:51.838275**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-09 07:15:51.846439**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:15:51.851545**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-10-09 07:15:51.857522**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 07:15:51.923066**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-10-09 07:15:51.940777**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: b8426804e118105c1f3a3b5fb3eebc5c
- **2026-10-09 07:15:51.958093**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: b24c79d896435e038f6c0fe2d74e0bb2
- **2026-10-09 07:15:52.40417**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 5e10ddf298e46dd40e829a9528caf4dc
- **2026-10-09 07:15:52.416594**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: c9edb85e4e090562e6da74709a2c65da
- **2026-10-09 07:15:52.428688**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: ae9f49ba03baa3eed8512fb3376ad0c8
- **2026-10-09 07:15:52.444562**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: a4753148b1d73cf9d4a4308c7890f00f
- **2026-10-09 07:15:52.457364**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 07:15:52.466976**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: f08f69159c317d77630bb68059dd6687
- **2026-10-09 07:15:52.677576**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 16b3e6328a5d12276431d7fa7193d58f
- **2026-10-09 07:15:52.689364**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 74482115a66d7625799ae4664742b1e3
