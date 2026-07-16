# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-16 16:37:39.000716
- Finished: 2026-07-16 16:37:41.448248

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-16 16:37:39.009609**: loading lexicon 'corpora/derived/es.csv'
- **2026-07-16 16:37:40.230212**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-16 16:37:40.269428**: pool after filters: 7172 words
    - pool: 7172
- **2026-07-16 16:37:40.603476**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-16 16:37:40.657317**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-07-16 16:37:40.668839**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-07-16 16:37:40.677197**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-07-16 16:37:40.685829**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-16 16:37:40.775869**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: d143dcfc416f330eee0f4eab44b3b212
- **2026-07-16 16:37:40.815595**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: aa5755dc930957dde93a60ae096d159f
- **2026-07-16 16:37:40.853922**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: b2dd610e72f3335fc3c6c01ff1bfa950
- **2026-07-16 16:37:41.125068**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: c544fe2ffdb8ca01f7f6af650f68b990
- **2026-07-16 16:37:41.145086**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-07-16 16:37:41.163701**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: dfb71abc4a367cc71cc200c1fee92382
- **2026-07-16 16:37:41.405076**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: f560f3fdd20b56529598fed85f99f0d5
- **2026-07-16 16:37:41.42632**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 2b2646632f0aa81d627ce75e81690efe
