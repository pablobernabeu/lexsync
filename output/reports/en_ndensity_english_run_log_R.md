# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-09 07:50:50.793263
- Finished: 2026-10-09 07:50:53.000387

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:50:50.796984**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:50:51.322716**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:50:51.333528**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-09 07:50:52.123755**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-09 07:50:52.381249**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:50:52.386116**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-09 07:50:52.389446**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:50:52.393301**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:50:52.396791**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = -0.83 [-1.10, -0.56], TOST p = 0.980 (not shown equivalent)
- **2026-10-09 07:50:52.400246**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.13 [-0.13, 0.39], TOST p = 0.010 (equivalent)
- **2026-10-09 07:50:52.439954**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-09 07:50:52.454103**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 12
    - md5: 2b6ccf7a1eaef3521f22084cfa042738
- **2026-10-09 07:50:52.466671**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 6
    - md5: a41c6f1d22cdfbf077198045ace08eb5
- **2026-10-09 07:50:52.775492**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 644b7f22a01b99b7ca0d94c040cf0be5
- **2026-10-09 07:50:52.786076**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: a9903c46919cefb72c1a564b6407ba91
- **2026-10-09 07:50:52.795435**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: e1c3bc4d5c84b8de9ec8aa08b25c677e
- **2026-10-09 07:50:52.809166**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-09 07:50:52.817157**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-09 07:50:52.825352**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-09 07:50:52.983234**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: cbc9a6be8ec3e4d7a98f1aee4dbe884a
- **2026-10-09 07:50:52.993132**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 0520277f045bbcb2f3f75914a7af3927
