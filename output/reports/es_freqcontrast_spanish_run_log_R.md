# lexsync run log: es_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-10 09:31:50.674718
- Finished: 2026-06-10 09:31:51.262952

## Run metadata

- design: es_freqcontrast
- language: spanish
- lexicon: corpora/derived/es.csv
- seed: 2026
- match_on: length, n_density, old20

## Steps

- **2026-06-10 09:31:50.675177** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-10 09:31:50.823547** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-10 09:31:50.839542** -- pool after filters: 7172 words
    - pool: 7172
- **2026-06-10 09:31:51.014424** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-10 09:31:51.030344** -- equivalence low_frequency vs high_frequency on 'length': d = 0.05, TOST p = 0.002 (equivalent)
- **2026-06-10 09:31:51.030757** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.55, TOST p = 1.000 (not shown equivalent)
- **2026-06-10 09:31:51.031017** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08, TOST p = 0.004 (equivalent)
- **2026-06-10 09:31:51.03124** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01, TOST p = 0.001 (equivalent)
- **2026-06-10 09:31:51.088825** -- wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 362ba66219e3f009f570a3d0d92ad1d0
- **2026-06-10 09:31:51.107797** -- wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-06-10 09:31:51.124658** -- wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: a9ef31b312c4ee7efccdb9b56c22f9d9
- **2026-06-10 09:31:51.248739** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: ff37690ea2bd173a17c321a8612e6955
- **2026-06-10 09:31:51.256095** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 580efdccc4cc1c99551ae1fda645150d
