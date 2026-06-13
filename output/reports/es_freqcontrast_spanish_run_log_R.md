# lexsync run log: es_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 18:21:18.815548
- Finished: 2026-06-13 18:21:19.310733

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 18:21:18.815965** -- loading lexicon 'corpora/derived/es.csv'
- **2026-06-13 18:21:18.933603** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 18:21:18.955093** -- pool after filters: 7172 words
    - pool: 7172
- **2026-06-13 18:21:19.107468** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 18:21:19.121451** -- equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-06-13 18:21:19.122041** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:19.12244** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-06-13 18:21:19.122713** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:19.165539** -- wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 362ba66219e3f009f570a3d0d92ad1d0
- **2026-06-13 18:21:19.179238** -- wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-06-13 18:21:19.191538** -- wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 3c58ab01910a1d7078694a5cf7c29b91
- **2026-06-13 18:21:19.296937** -- wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: 3ba4920fb82d490ac824920276af427e
- **2026-06-13 18:21:19.303911** -- wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: f89b9471ee7659ef78f20606c0526071
