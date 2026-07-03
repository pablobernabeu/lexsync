# lexsync run log: en_ndensity

- Engine: R 4.6.0
- Started: 2026-07-03 10:36:55.827225
- Finished: 2026-07-03 10:36:57.150892

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 10:36:55.832143**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03 10:36:56.349425**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 10:36:56.362928**: pool after filters: 4557 words
    - pool: 4557
- **2026-07-03 10:36:56.733372**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-07-03 10:36:56.763391**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-03 10:36:56.770276**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-07-03 10:36:56.777891**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 10:36:56.783952**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 10:36:56.831685**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 83ac260307e41472e1b694c80270a560
- **2026-07-03 10:36:56.855939**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 6cac620d8e59d190427f9cb49fb92252
- **2026-07-03 10:36:56.878959**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-07-03 10:36:57.002713**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: 9eeaa09c594db721be6eebd5eeb01f63
- **2026-07-03 10:36:57.015966**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 17b37538967b395adb7b014c4aeadf25
- **2026-07-03 10:36:57.027873**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 3ad3ff1fababe542351d4414ed621cb4
- **2026-07-03 10:36:57.126978**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: ecf71234e4f154d9dafd04f7cf7e3034
- **2026-07-03 10:36:57.138586**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 9106bd01fbe16cd93b0208ad17e4d546
