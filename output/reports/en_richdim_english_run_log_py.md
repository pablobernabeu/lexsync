# lexsync run log: en_richdim

- Engine: Python 3.13.7
- Started: 2026-10-09T11:51:20
- Finished: 2026-10-09T11:51:22

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T11:51:20**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-09T11:51:21**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T11:51:21**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-09T11:51:21**: pool after filters: 8597 words
    - pool: 8597
- **2026-10-09T11:51:21**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-09T11:51:22**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.56 [4.89, 6.22], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'n_density': d = -0.13 [-0.43, 0.17], TOST p = 0.0221 (equivalent)
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'old20': d = -0.07 [-0.37, 0.23], TOST p = 0.0101 (equivalent)
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.02 [-0.28, 0.32], TOST p = 0.005 (equivalent)
- **2026-10-09T11:51:22**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.02 [-0.28, 0.33], TOST p = 0.0052 (equivalent)
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_stimuli_py.csv'
    - path: output\stimuli\en_richdim_english_stimuli_py.csv
    - rows: 120
    - md5: c91057197226d449b407d11cbad842ec
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_descriptives_py.csv'
    - path: output\reports\en_richdim_english_descriptives_py.csv
    - rows: 12
    - md5: 43550dcba20992170506aa9212065cf5
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_comparisons_py.csv'
    - path: output\reports\en_richdim_english_comparisons_py.csv
    - rows: 6
    - md5: 7f75c26160216125137214f43601aa2b
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_psychopy.py'
    - path: output\experiments\en_richdim_english_psychopy.py
    - rows: None
    - md5: 79705e247031e6758a2fef5a662c65d3
- **2026-10-09T11:51:22**: wrote 'en_richdim_english.osexp'
    - path: output\experiments\en_richdim_english.osexp
    - rows: None
    - md5: 982f3b21c018cbdb9debd5bb68e8ef0a
- **2026-10-09T11:51:22**: wrote 'en_richdim_english.html'
    - path: output\experiments\en_richdim_english.html
    - rows: None
    - md5: 7d3f2345f976fbd4c06785db9378c7a9
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_psychopy.csv'
    - path: output\experiments\en_richdim_english_psychopy.csv
    - rows: None
    - md5: 15c3ec229ea2f235ea71993ff5884d51
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_opensesame.csv'
    - path: output\experiments\en_richdim_english_opensesame.csv
    - rows: None
    - md5: 688d6883920616305069d8117f36a179
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_opensesame_text.csv'
    - path: output\experiments\en_richdim_english_opensesame_text.csv
    - rows: None
    - md5: cb591bc0fa64c110771aa5242b43bc7b
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_datasheet_py.json'
    - path: output\reports\en_richdim_english_datasheet_py.json
    - rows: None
    - md5: 8630c4997c355b6d3716b72ceab9e107
- **2026-10-09T11:51:22**: wrote 'en_richdim_english_datasheet_py.md'
    - path: output\reports\en_richdim_english_datasheet_py.md
    - rows: None
    - md5: 8c4354c5b6a86855858429841468118a
