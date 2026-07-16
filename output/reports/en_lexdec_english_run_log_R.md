# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-07-16 16:36:57.409764
- Finished: 2026-07-16 16:37:02.049323

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16 16:36:57.418446**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-16 16:36:58.579465**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-16 16:36:58.60716**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-16 16:37:00.97245**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-16 16:37:00.992011**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-16 16:37:01.113051**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: f1c1159431d7d91972e84aab3bf876ab
- **2026-07-16 16:37:01.157465**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-07-16 16:37:01.212234**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-16 16:37:01.590459**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 0c50909a0211eca881dcdd5a7ad09822
- **2026-07-16 16:37:01.658406**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-07-16 16:37:01.68692**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 2f30a114bd5283759de8ff3e4a34cc3b
- **2026-07-16 16:37:02.000947**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 125d405c0a19babf9d3d68977aa6420d
- **2026-07-16 16:37:02.024808**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: beaac662bd475017aca2ab958459a367
