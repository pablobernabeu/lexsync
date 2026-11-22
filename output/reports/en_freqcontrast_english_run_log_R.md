# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-11-02 21:28:31.076953
- Finished: 2026-11-02 21:28:32.60259

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-11-02 21:28:31.077805**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-11-02 21:28:31.077952**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-11-02 21:28:31.90123**: lexicon loaded: 30000 words
    - words: 30000
- **2026-11-02 21:28:31.905307**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-11-02 21:28:31.911263**: pool after filters: 6308 words
    - pool: 6308
- **2026-11-02 21:28:32.06661**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-11-02 21:28:32.201842**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-11-02 21:28:32.202182**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.29 [4.74, 5.85], TOST p = 1.000 (not shown equivalent)
- **2026-11-02 21:28:32.202487**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.06 [-0.21, 0.32], TOST p = 0.003 (equivalent)
- **2026-11-02 21:28:32.202767**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.24, 0.28], TOST p = 0.002 (equivalent)
- **2026-11-02 21:28:32.203082**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.02 [-0.28, 0.24], TOST p = 0.001 (equivalent)
- **2026-11-02 21:28:32.20336**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-11-02 21:28:32.241493**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d47cd351a19c23267f3e6039c439faf7
- **2026-11-02 21:28:32.2461**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 12
    - md5: 082b6c5d2532c318cb7de6c566caf94d
- **2026-11-02 21:28:32.249425**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 6
    - md5: 24508cd69e101a7ca46e8b58700d4ce7
- **2026-11-02 21:28:32.531915**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 4624b80a1b2b4b2011704fb6f6e93a77
- **2026-11-02 21:28:32.5323**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: ba898c191550d11c8f777dfcf740e6b6
- **2026-11-02 21:28:32.532608**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 644fb9183d7c5a74bbcf53171f1cdc98
- **2026-11-02 21:28:32.532968**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output/experiments/en_freqcontrast_english_psychopy.csv
    - rows: NA
    - md5: 021a703375cd3213b738ee7c1dc0576a
- **2026-11-02 21:28:32.533265**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame.csv
    - rows: NA
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-11-02 21:28:32.533576**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output/experiments/en_freqcontrast_english_opensesame_text.csv
    - rows: NA
    - md5: 9c9292272f3cedc764049d6651f27902
- **2026-11-02 21:28:32.601717**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: d410b209cd7af5fc2593aeee337a95b2
- **2026-11-02 21:28:32.602081**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: ee60d33c93bd1f4c7191b4534e068afd
