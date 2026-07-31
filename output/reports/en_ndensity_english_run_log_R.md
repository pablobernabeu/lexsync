# lexsync run log: en_ndensity

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:25.309634
- Finished: 2026-07-31 21:48:26.290222

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:25.312699**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 21:48:25.615427**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:25.624027**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-31 21:48:25.952136**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-31 21:48:25.967103**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-31 21:48:25.971139**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-31 21:48:25.976208**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:25.980801**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 21:48:26.019177**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-07-31 21:48:26.03949**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-07-31 21:48:26.055436**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-07-31 21:48:26.157435**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 1f85015d5b69c92e56ad1c703129b039
- **2026-07-31 21:48:26.168107**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-07-31 21:48:26.178519**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 6d7cb383cfc3114c18f7f1499950ac35
- **2026-07-31 21:48:26.271039**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: e3a8757090493c7edd9362346ae4f9a1
- **2026-07-31 21:48:26.281744**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 80e0f0ceb2d8eda22cad2f536a918189
