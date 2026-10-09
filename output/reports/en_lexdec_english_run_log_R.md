# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-09 09:52:40.072206
- Finished: 2026-10-09 09:52:43.017004

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 09:52:40.076667**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 09:52:40.647618**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 09:52:40.657743**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 09:52:41.507477**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09 09:52:42.396927**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-09 09:52:42.403736**: equivalence pseudoword vs word on 'bigram_freq': d = -1.47 [-1.81, -1.13], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 09:52:42.408202**: equivalence pseudoword vs word on 'n_density': d = -0.28 [-0.59, 0.02], TOST p = 0.117 (not shown equivalent)
- **2026-10-09 09:52:42.4196**: equivalence pseudoword vs word on 'old20': d = 0.17 [-0.13, 0.47], TOST p = 0.037 (equivalent)
- **2026-10-09 09:52:42.460515**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: bc7c16452b7fd7cbabe8fafc8bb28287
- **2026-10-09 09:52:42.475509**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: bee90fb07b347d3fe262803a6f342ade
- **2026-10-09 09:52:42.490449**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 9464b3452793472e9abce17609e3d369
- **2026-10-09 09:52:42.76386**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: a9c90173d7b34b6b6c1a914fa5132f57
- **2026-10-09 09:52:42.77467**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 694c11f70ca325181628b5da1922e729
- **2026-10-09 09:52:42.784726**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 3307ed89b9e2aaa71ac5dfcff505306d
- **2026-10-09 09:52:42.797619**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 1fe32d4aaed880e77a845f82eb6df4a6
- **2026-10-09 09:52:42.802622**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-09 09:52:42.809775**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 706132481e716f2a1ada15a83b56c292
- **2026-10-09 09:52:42.999757**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 848e8363750053d10ba41dcaf155a0c7
- **2026-10-09 09:52:43.009327**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: c8f0b4c8f3809ba29f8ee4dafac90e32
