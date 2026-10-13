# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-13 11:09:46.908313
- Finished: 2026-10-13 11:09:55.685676

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:09:47.142903**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 11:09:50.183836**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 11:09:50.257823**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 11:09:50.313878**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-13 11:09:51.115992**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13 11:09:51.741694**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-10-13 11:09:51.875903**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.29 [4.74, 5.85], TOST p = 1.000 (not shown equivalent)
- **2026-10-13 11:09:51.934723**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.06 [-0.21, 0.32], TOST p = 0.003 (equivalent)
- **2026-10-13 11:09:51.956118**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.24, 0.28], TOST p = 0.002 (equivalent)
- **2026-10-13 11:09:51.970909**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.02 [-0.28, 0.24], TOST p = 0.001 (equivalent)
- **2026-10-13 11:09:51.987616**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-13 11:09:52.385206**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d47cd351a19c23267f3e6039c439faf7
- **2026-10-13 11:09:52.479287**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 12
    - md5: 082b6c5d2532c318cb7de6c566caf94d
- **2026-10-13 11:09:52.561868**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 6
    - md5: 24508cd69e101a7ca46e8b58700d4ce7
- **2026-10-13 11:09:54.955365**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 5e10ddf298e46dd40e829a9528caf4dc
- **2026-10-13 11:09:54.990802**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: c9edb85e4e090562e6da74709a2c65da
- **2026-10-13 11:09:55.023256**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: e376037100863088a14a4f7592d89bb2
- **2026-10-13 11:09:55.081191**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: 021a703375cd3213b738ee7c1dc0576a
- **2026-10-13 11:09:55.112859**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13 11:09:55.141673**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: 9c9292272f3cedc764049d6651f27902
- **2026-10-13 11:09:55.630383**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 9818da035d517b6f9d2b52d448457248
- **2026-10-13 11:09:55.656991**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: fbb80925449acb13987206de820cfa19
