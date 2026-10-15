# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-15 04:44:29.065854
- Finished: 2026-10-15 04:44:33.16393

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 04:44:29.074252**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15 04:44:29.080119**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-15 04:44:31.061258**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 04:44:31.084357**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-15 04:44:31.112713**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-15 04:44:31.558878**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-15 04:44:31.978988**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-15 04:44:31.984592**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.29 [4.74, 5.85], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 04:44:31.991216**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.06 [-0.21, 0.32], TOST p = 0.003 (equivalent)
- **2026-10-15 04:44:31.996789**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.24, 0.28], TOST p = 0.002 (equivalent)
- **2026-10-15 04:44:32.004912**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.02 [-0.28, 0.24], TOST p = 0.001 (equivalent)
- **2026-10-15 04:44:32.010497**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-15 04:44:32.096776**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d47cd351a19c23267f3e6039c439faf7
- **2026-10-15 04:44:32.125797**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 12
    - md5: 082b6c5d2532c318cb7de6c566caf94d
- **2026-10-15 04:44:32.156894**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 6
    - md5: 24508cd69e101a7ca46e8b58700d4ce7
- **2026-10-15 04:44:32.750367**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 72e16d8220df92c83c9d1b37806c9fb8
- **2026-10-15 04:44:32.762922**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: ba898c191550d11c8f777dfcf740e6b6
- **2026-10-15 04:44:32.774897**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 2ee9751048de4559453cd29f4da4419c
- **2026-10-15 04:44:32.79374**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: 021a703375cd3213b738ee7c1dc0576a
- **2026-10-15 04:44:32.804581**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-15 04:44:32.816179**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: 9c9292272f3cedc764049d6651f27902
- **2026-10-15 04:44:33.136651**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: ba14ddf292513a7d6c12487e7548f71e
- **2026-10-15 04:44:33.152155**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: fbb80925449acb13987206de820cfa19
