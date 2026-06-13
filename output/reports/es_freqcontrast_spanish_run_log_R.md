# lexsync run log: es_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 22:14:46.871606
- Finished: 2026-06-13 22:14:47.967175

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:14:46.872294** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-13 22:14:47.494311** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:14:47.519072** -- pool after filters: 7172 words
    - pool: 7172
- **2026-06-13 22:14:47.664864** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 22:14:47.679607** -- equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-06-13 22:14:47.680195** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:47.680658** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-06-13 22:14:47.681056** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:47.722945** -- wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: d143dcfc416f330eee0f4eab44b3b212
- **2026-06-13 22:14:47.736927** -- wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-06-13 22:14:47.749526** -- wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 3c58ab01910a1d7078694a5cf7c29b91
- **2026-06-13 22:14:47.851282** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: 3ba4920fb82d490ac824920276af427e
- **2026-06-13 22:14:47.856259** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: f89b9471ee7659ef78f20606c0526071
- **2026-06-13 22:14:47.860728** -- wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: ee27d11d26fe86dcf23386e3644c5e6e
- **2026-06-13 22:14:47.952845** -- wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 186bf8804679193dc6f7b08b96a4ac50
- **2026-06-13 22:14:47.959458** -- wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 212e3475c32bc40e8217b433b0cbe8dd
