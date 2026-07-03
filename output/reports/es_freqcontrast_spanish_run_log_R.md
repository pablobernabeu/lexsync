# lexsync run log: es_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-03 08:07:54.251208
- Finished: 2026-07-03 08:07:54.979973

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-07-03 08:07:54.255083**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-03 08:07:54.5833**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 08:07:54.594497**: pool after filters: 7172 words
    - pool: 7172
- **2026-07-03 08:07:54.678565**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-03 08:07:54.692091**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-07-03 08:07:54.696299**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-07-03 08:07:54.702241**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-07-03 08:07:54.707241**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-03 08:07:54.742752**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: d143dcfc416f330eee0f4eab44b3b212
- **2026-07-03 08:07:54.762417**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-07-03 08:07:54.77986**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 3c58ab01910a1d7078694a5cf7c29b91
- **2026-07-03 08:07:54.869834**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: a02d2d6ff1b4f5f18f59dbea69c039a4
- **2026-07-03 08:07:54.880598**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: f89b9471ee7659ef78f20606c0526071
- **2026-07-03 08:07:54.889172**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 3274154276f3c731e7c1965299702598
- **2026-07-03 08:07:54.959735**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 41df32661c3b45db36fd45fdcb2de33b
- **2026-07-03 08:07:54.968991**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: c791c8ae8207fdaa4ab7faaff42bab8d
