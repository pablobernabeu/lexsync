# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-08-01 00:33:45.943044
- Finished: 2026-08-01 00:33:46.62261

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-08-01 00:33:45.945262**: loading lexicon 'corpora/derived/es.csv'
- **2026-08-01 00:33:46.201684**: lexicon loaded: 30000 words
    - words: 30000
- **2026-08-01 00:33:46.217367**: pool after filters: 7172 words
    - pool: 7172
- **2026-08-01 00:33:46.307709**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-08-01 00:33:46.324383**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-08-01 00:33:46.32855**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [5.29, 5.81], TOST p = 1.000 (not shown equivalent)
- **2026-08-01 00:33:46.331927**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-08-01 00:33:46.334801**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-08-01 00:33:46.378681**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-08-01 00:33:46.392787**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-08-01 00:33:46.40626**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: b2dd610e72f3335fc3c6c01ff1bfa950
- **2026-08-01 00:33:46.506555**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: d9625b06edd4c9140cf5b98b60f431ea
- **2026-08-01 00:33:46.515693**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-08-01 00:33:46.523744**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 6f9a3d1b80074a8c08e7dfd93a040d8d
- **2026-08-01 00:33:46.605819**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 1f34875cdab7271f7fe06d4bb70dc937
- **2026-08-01 00:33:46.61408**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: aabab4ec0358877f0104e210ad0a95ab
