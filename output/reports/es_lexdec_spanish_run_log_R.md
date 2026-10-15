# lexsync run log: es_lexdec

- Engine: R 4.6.1
- Started: 2026-10-15 03:29:45.193695
- Finished: 2026-10-15 03:29:58.01044

## Run metadata

- design: es_lexdec
- language: spanish
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 03:29:45.202378**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15 03:29:45.21083**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-15 03:29:45.971336**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 03:29:45.990444**: pool after filters: 8305 words
    - pool: 8305
- **2026-10-15 03:29:47.253526**: pseudowords checked against 334625 known word form(s) from 'corpora/derived/es_known_forms.txt'
    - exclude: corpora/derived/es_known_forms.txt
    - sha256: 281fa6c374e1fa6550e6f5700d19b9bae4ccb664cfd3fc37ca6ffc087acdd776
- **2026-10-15 03:29:54.594029**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-15 03:29:56.662831**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-15 03:29:56.672718**: equivalence pseudoword vs word on 'bigram_freq': d = -1.21 [-1.54, -0.88], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 03:29:56.680737**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-15 03:29:56.689265**: equivalence pseudoword vs word on 'old20': d = 0.02 [-0.28, 0.32], TOST p = 0.005 (equivalent)
- **2026-10-15 03:29:56.770451**: wrote 'es_lexdec_spanish_stimuli_R.csv'
    - path: output/stimuli/es_lexdec_spanish_stimuli_R.csv
    - rows: 120
    - md5: f34a8e3b82774563ec5c6e51211fa385
- **2026-10-15 03:29:56.808611**: wrote 'es_lexdec_spanish_descriptives_R.csv'
    - path: output/reports/es_lexdec_spanish_descriptives_R.csv
    - rows: 8
    - md5: a5359adc48f76fd75aefa9b95c83907e
- **2026-10-15 03:29:56.844654**: wrote 'es_lexdec_spanish_comparisons_R.csv'
    - path: output/reports/es_lexdec_spanish_comparisons_R.csv
    - rows: 4
    - md5: a2b9a2754d018354bbe0abdbb5850666
- **2026-10-15 03:29:57.329293**: wrote 'es_lexdec_spanish_psychopy.py'
    - path: output/experiments/es_lexdec_spanish_psychopy.py
    - rows: NA
    - md5: 6e8ec3994e96f4ef6239e27d55e8836a
- **2026-10-15 03:29:57.351393**: wrote 'es_lexdec_spanish.osexp'
    - path: output/experiments/es_lexdec_spanish.osexp
    - rows: NA
    - md5: 275c631cd7a24cd5bd7d7b5c2f6d7dc5
- **2026-10-15 03:29:57.373834**: wrote 'es_lexdec_spanish.html'
    - path: output/experiments/es_lexdec_spanish.html
    - rows: NA
    - md5: d18626fc6446058d92149ddd78bdbd8d
- **2026-10-15 03:29:57.403029**: wrote 'es_lexdec_spanish_psychopy.csv'
    - path: output/experiments/es_lexdec_spanish_psychopy.csv
    - rows: NA
    - md5: 2a6f6f7cfb6929d91027c03e23698263
- **2026-10-15 03:29:57.426371**: wrote 'es_lexdec_spanish_opensesame.csv'
    - path: output/experiments/es_lexdec_spanish_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-15 03:29:57.451219**: wrote 'es_lexdec_spanish_opensesame_text.csv'
    - path: output/experiments/es_lexdec_spanish_opensesame_text.csv
    - rows: NA
    - md5: bf9c50c952be24b560b4a1ce78815bce
- **2026-10-15 03:29:57.968314**: wrote 'es_lexdec_spanish_datasheet_R.json'
    - path: output/reports/es_lexdec_spanish_datasheet_R.json
    - rows: NA
    - md5: a0741ed99c1b63d0e114a9de36bc625a
- **2026-10-15 03:29:57.991124**: wrote 'es_lexdec_spanish_datasheet_R.md'
    - path: output/reports/es_lexdec_spanish_datasheet_R.md
    - rows: NA
    - md5: 5796250c054ac313bbe49ef66df1b06a
