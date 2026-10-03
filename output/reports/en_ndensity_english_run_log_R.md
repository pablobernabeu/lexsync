# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-10-03 13:10:49.662246
- Finished: 2026-10-03 13:11:07.55746

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 13:10:49.74672**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 13:10:52.11759**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 13:10:52.206664**: pool after filters: 4557 words
    - pool: 4557
- **2026-10-03 13:10:54.336517**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-03 13:10:54.442801**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 13:10:54.451662**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-03 13:10:54.460488**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.72, 3.50], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:10:54.470908**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.64, -1.97], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 13:10:55.400236**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-10-03 13:10:55.550729**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-10-03 13:10:55.827423**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 39f420a650e8857a7f9d65c8a36e9a6c
- **2026-10-03 13:11:06.018956**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: bd98a6c8198cbf9939237541726ed887
- **2026-10-03 13:11:06.205909**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 20eea6534281800fb670f1e595ca224b
- **2026-10-03 13:11:06.28389**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: a768811c17f9929fedf6ad56c5344b40
- **2026-10-03 13:11:06.499178**: wrote 'en_ndensity_english_psychopy.csv'
    - path: output/experiments/en_ndensity_english_psychopy.csv
    - rows: NA
    - md5: 17bfcc53a4722c27f80242104cb4ac68
- **2026-10-03 13:11:06.557932**: wrote 'en_ndensity_english_opensesame.csv'
    - path: output/experiments/en_ndensity_english_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-03 13:11:06.619538**: wrote 'en_ndensity_english_opensesame_text.csv'
    - path: output/experiments/en_ndensity_english_opensesame_text.csv
    - rows: NA
    - md5: b9335ee7989ca44e842c0d17e4735473
- **2026-10-03 13:11:07.317737**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: 84c8d6f1d33e6f242bc12a9c3f1c3535
- **2026-10-03 13:11:07.412946**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 4822cfbc9db65cd043b68e40888928ef
