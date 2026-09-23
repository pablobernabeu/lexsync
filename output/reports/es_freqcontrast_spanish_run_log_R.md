# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-09-23 23:13:28.270425
- Finished: 2026-09-23 23:13:35.987611

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-23 23:13:28.288659**: loading lexicon 'corpora/derived/es.csv'
- **2026-09-23 23:13:29.35698**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-23 23:13:29.401879**: pool after filters: 7172 words
    - pool: 7172
- **2026-09-23 23:13:29.814054**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-23 23:13:29.908661**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-09-23 23:13:29.927336**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-09-23 23:13:29.955074**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-09-23 23:13:29.962597**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-09-23 23:13:31.35602**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-09-23 23:13:31.641384**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-09-23 23:13:31.848175**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-09-23 23:13:34.957968**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: d9625b06edd4c9140cf5b98b60f431ea
- **2026-09-23 23:13:35.017775**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 09d5b1cb048bec514aad7d8bebc546d2
- **2026-09-23 23:13:35.076861**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 0124c382fbd275f9afd0f71f5a983094
- **2026-09-23 23:13:35.791517**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: d0062e0687766cda83708650a8c9bd25
- **2026-09-23 23:13:35.915083**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: fb2fe2b3f37d29eab56494f878e4911b
