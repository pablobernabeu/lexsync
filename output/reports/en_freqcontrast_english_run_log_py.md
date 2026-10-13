# lexsync run log: en_freqcontrast

- Engine: Python 3.13.7
- Started: 2026-10-13T22:49:26
- Finished: 2026-10-13T22:49:29

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T22:49:26**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13T22:49:26**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13T22:49:28**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T22:49:28**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13T22:49:28**: pool after filters: 6308 words
    - pool: 6308
- **2026-10-13T22:49:28**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.0017 (equivalent)
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.29 [4.74, 5.85], TOST p = 1.0 (not shown equivalent)
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.06 [-0.21, 0.32], TOST p = 0.0028 (equivalent)
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'old20': d = 0.02 [-0.24, 0.28], TOST p = 0.0015 (equivalent)
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'n_syllables': d = -0.02 [-0.28, 0.24], TOST p = 0.0014 (equivalent)
- **2026-10-13T22:49:29**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.25, 0.27], TOST p = 0.0011 (equivalent)
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_stimuli_py.csv'
    - path: output\stimuli\en_freqcontrast_english_stimuli_py.csv
    - rows: 160
    - md5: d47cd351a19c23267f3e6039c439faf7
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_descriptives_py.csv'
    - path: output\reports\en_freqcontrast_english_descriptives_py.csv
    - rows: 12
    - md5: 082b6c5d2532c318cb7de6c566caf94d
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_comparisons_py.csv'
    - path: output\reports\en_freqcontrast_english_comparisons_py.csv
    - rows: 6
    - md5: 24508cd69e101a7ca46e8b58700d4ce7
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output\experiments\en_freqcontrast_english_psychopy.py
    - rows: None
    - md5: 12f18bc6f1e9271229571aaf97663624
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english.osexp'
    - path: output\experiments\en_freqcontrast_english.osexp
    - rows: None
    - md5: 3ac3462d00b155d8ea18f3127f4720c3
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english.html'
    - path: output\experiments\en_freqcontrast_english.html
    - rows: None
    - md5: f6515a9f880e61730f29519f38e36dcf
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_psychopy.csv'
    - path: output\experiments\en_freqcontrast_english_psychopy.csv
    - rows: None
    - md5: 021a703375cd3213b738ee7c1dc0576a
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_opensesame.csv'
    - path: output\experiments\en_freqcontrast_english_opensesame.csv
    - rows: None
    - md5: 92e29c7a204d46f2df23de8018ad235a
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_opensesame_text.csv'
    - path: output\experiments\en_freqcontrast_english_opensesame_text.csv
    - rows: None
    - md5: 9c9292272f3cedc764049d6651f27902
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_datasheet_py.json'
    - path: output\reports\en_freqcontrast_english_datasheet_py.json
    - rows: None
    - md5: 3ce6e577a5c46d15e9e320b6fb1103a3
- **2026-10-13T22:49:29**: wrote 'en_freqcontrast_english_datasheet_py.md'
    - path: output\reports\en_freqcontrast_english_datasheet_py.md
    - rows: None
    - md5: 2b20e2c1e0cd257c541315a7e1e47db5
