# lexsync run log: en_lexdec

- Engine: R 4.3.3
- Started: 2026-09-02 19:24:59.635872
- Finished: 2026-09-02 19:25:00.39074

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:24:59.636098**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:24:59.848121**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:24:59.853128**: pool after filters: 8177 words
    - pool: 8177
- **2026-09-02 19:25:00.34564**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-09-02 19:25:00.348848**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.0036 (equivalent)
- **2026-09-02 19:25:00.360094**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-09-02 19:25:00.361879**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-09-02 19:25:00.363518**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-09-02 19:25:00.378361**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 1504c568260802eed4dcb41daccb8144
- **2026-09-02 19:25:00.378559**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-09-02 19:25:00.378642**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: fb969d979282508a6fca961a666c20a5
- **2026-09-02 19:25:00.390453**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: b082d6e68eb14ec4280220c356b1398b
- **2026-09-02 19:25:00.390619**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 94a295c6306efed44431a655d48cb373
