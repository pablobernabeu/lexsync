# lexsync run log: en_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-09T09:53:34
- Finished: 2026-10-09T09:53:35

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T09:53:34**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09T09:53:35**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T09:53:35**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09T09:53:35**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.0016 (equivalent)
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.0011 (equivalent)
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.21 [-0.47, 0.05], TOST p = 0.0337 (equivalent)
- **2026-10-09T09:53:35**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = -0.04 [-0.31, 0.22], TOST p = 0.0023 (equivalent)
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontrast_english_stimuli_py.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_descriptives_py.csv'
    - path: output\reports\en_freqcontrast_english_descriptives_py.csv
    - rows: 12
    - md5: 476a49213b59b31e07ab4fa36db4957c
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_comparisons_py.csv'
    - path: output\reports\en_freqcontrast_english_comparisons_py.csv
    - rows: 6
    - md5: f58e360d9ac1f9f839ce3112e2dfb561
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output\experiments\en_freqcontrast_english_psychopy.py
    - rows: None
    - md5: 5e10ddf298e46dd40e829a9528caf4dc
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english.osexp'
    - path: output\experiments\en_freqcontrast_english.osexp
    - rows: None
    - md5: c9edb85e4e090562e6da74709a2c65da
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english.html'
    - path: output\experiments\en_freqcontrast_english.html
    - rows: None
    - md5: ae9f49ba03baa3eed8512fb3376ad0c8
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output\experiments\en_freqcontrast_english_psychopy.csv
    - rows: None
    - md5: a4753148b1d73cf9d4a4308c7890f00f
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output\experiments\en_freqcontrast_english_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output\experiments\en_freqcontrast_english_opensesame_text.csv
    - rows: None
    - md5: f08f69159c317d77630bb68059dd6687
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_datasheet_py.json'
    - path: output\reports\en_freqcontrast_english_datasheet_py.json
    - rows: None
    - md5: 38608caea657e2a7658a343f534af084
- **2026-10-09T09:53:35**: wrote 'en_freqcontrast_english_datasheet_py.md'
    - path: output\reports\en_freqcontrast_english_datasheet_py.md
    - rows: None
    - md5: 1b24e8febc1b25127f4bbdbc484b66a2
