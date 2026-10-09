# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 07:50:31.873412
- Finished: 2026-10-09 07:50:33.720834

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:50:31.878192**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:50:32.51169**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:50:32.52704**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09 07:50:32.760781**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 07:50:33.034955**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-09 07:50:33.039645**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:50:33.042808**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-10-09 07:50:33.046079**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 07:50:33.049377**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.21 [-0.47, 0.05], TOST p = 0.034 (equivalent)
- **2026-10-09 07:50:33.052923**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = -0.04 [-0.31, 0.22], TOST p = 0.002 (equivalent)
- **2026-10-09 07:50:33.098112**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-10-09 07:50:33.114129**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 12
    - md5: 476a49213b59b31e07ab4fa36db4957c
- **2026-10-09 07:50:33.129506**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 6
    - md5: f58e360d9ac1f9f839ce3112e2dfb561
- **2026-10-09 07:50:33.455353**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 5e10ddf298e46dd40e829a9528caf4dc
- **2026-10-09 07:50:33.464908**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: c9edb85e4e090562e6da74709a2c65da
- **2026-10-09 07:50:33.472489**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: ae9f49ba03baa3eed8512fb3376ad0c8
- **2026-10-09 07:50:33.485022**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: a4753148b1d73cf9d4a4308c7890f00f
- **2026-10-09 07:50:33.492182**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 07:50:33.500144**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: f08f69159c317d77630bb68059dd6687
- **2026-10-09 07:50:33.704851**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 97d0b2d2452122fec1e076c0a2416593
- **2026-10-09 07:50:33.71323**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 55b4a401ea8e9ca2c2e5c531a91f1f3e
