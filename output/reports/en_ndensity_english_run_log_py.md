# lexsync run log: en_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-09T03:42:35
- Finished: 2026-10-09T03:42:37

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-09T03:42:35**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09T03:42:35**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09T03:42:35**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-09T03:42:36**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09T03:42:36**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T03:42:36**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-09T03:42:36**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T03:42:36**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.0 (not shown equivalent)
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_stimuli_py.csv'
    - path: output\stimuli\en_ndensity_english_stimuli_py.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_descriptives_py.csv'
    - path: output\reports\en_ndensity_english_descriptives_py.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_comparisons_py.csv'
    - path: output\reports\en_ndensity_english_comparisons_py.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_psychopy.py'
    - path: output\experiments\en_ndensity_english_psychopy.py
    - rows: None
    - md5: bd98a6c8198cbf9939237541726ed887
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english.osexp'
    - path: output\experiments\en_ndensity_english.osexp
    - rows: None
    - md5: 20eea6534281800fb670f1e595ca224b
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english.html'
    - path: output\experiments\en_ndensity_english.html
    - rows: None
    - md5: a768811c17f9929fedf6ad56c5344b40
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output\experiments\en_ndensity_english_psychopy.csv
    - rows: None
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output\experiments\en_ndensity_english_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output\experiments\en_ndensity_english_opensesame_text.csv
    - rows: None
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_datasheet_py.json'
    - path: output\reports\en_ndensity_english_datasheet_py.json
    - rows: None
    - md5: 459452f7ab2af1b582c3c9151aca2272
- **2026-10-09T03:42:37**: wrote 'en_ndensity_english_datasheet_py.md'
    - path: output\reports\en_ndensity_english_datasheet_py.md
    - rows: None
    - md5: 3b955898fde349b34ce4a2ce27104641
