# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-09 09:52:38.24024
- Finished: 2026-10-09 09:52:40.046294

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:52:38.244873**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 09:52:38.766749**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:52:38.777745**: pool after filters: 7230 words
    - pool: 7230
- **2026-10-09 09:52:39.029518**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09 09:52:39.331488**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-09 09:52:39.336959**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [4.72, 5.83], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:52:39.342397**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-10-09 09:52:39.34695**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-09 09:52:39.350766**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.21 [-0.47, 0.05], TOST p = 0.034 (equivalent)
- **2026-10-09 09:52:39.354254**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = -0.04 [-0.31, 0.22], TOST p = 0.002 (equivalent)
- **2026-10-09 09:52:39.400425**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-10-09 09:52:39.41549**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 12
    - md5: 476a49213b59b31e07ab4fa36db4957c
- **2026-10-09 09:52:39.430809**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 6
    - md5: f58e360d9ac1f9f839ce3112e2dfb561
- **2026-10-09 09:52:39.737355**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 5e10ddf298e46dd40e829a9528caf4dc
- **2026-10-09 09:52:39.74567**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: c9edb85e4e090562e6da74709a2c65da
- **2026-10-09 09:52:39.75283**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: ae9f49ba03baa3eed8512fb3376ad0c8
- **2026-10-09 09:52:39.767631**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: a4753148b1d73cf9d4a4308c7890f00f
- **2026-10-09 09:52:39.77581**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-09 09:52:39.783278**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: f08f69159c317d77630bb68059dd6687
- **2026-10-09 09:52:40.026599**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 48610a00efe5e0e57cf22a7acc2b536e
- **2026-10-09 09:52:40.037184**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 14e3475f20de7d41784a7482436e4fa0
