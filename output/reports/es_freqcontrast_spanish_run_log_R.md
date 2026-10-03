# lexsync run log: es_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-03 09:50:07.873402
- Finished: 2026-10-03 09:50:28.042475

## Run metadata

- design: es_freqcontrast
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 09:50:07.891119**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-03 09:50:11.481436**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 09:50:11.658706**: pool after filters: 7172 words
    - pool: 7172
- **2026-10-03 09:50:12.653493**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-03 09:50:12.844079**: equivalence low_frequency vs high_frequency on 'length': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-03 09:50:12.867654**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.55 [4.97, 6.12], TOST p = 1.000 (not shown equivalent)
- **2026-10-03 09:50:12.885168**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.18, 0.34], TOST p = 0.004 (equivalent)
- **2026-10-03 09:50:12.899599**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.26, 0.27], TOST p = 0.001 (equivalent)
- **2026-10-03 09:50:14.278705**: wrote 'es_freqcontrast_spanish_stimuli_R.csv'
    - path: output/stimuli/es_freqcontrast_spanish_stimuli_R.csv
    - rows: 160
    - md5: 02356c7368366cd271e652d1d217f136
- **2026-10-03 09:50:14.586861**: wrote 'es_freqcontrast_spanish_descriptives_R.csv'
    - path: output/reports/es_freqcontrast_spanish_descriptives_R.csv
    - rows: 8
    - md5: 27efe7a7db42facb9f011a7a0d1ca3f0
- **2026-10-03 09:50:15.276226**: wrote 'es_freqcontrast_spanish_comparisons_R.csv'
    - path: output/reports/es_freqcontrast_spanish_comparisons_R.csv
    - rows: 4
    - md5: 9b43165868c2f00f9c9250e59cacd4ce
- **2026-10-03 09:50:25.873202**: wrote 'es_freqcontrast_spanish_psychopy.py'
    - path: output/experiments/es_freqcontrast_spanish_psychopy.py
    - rows: NA
    - md5: d9625b06edd4c9140cf5b98b60f431ea
- **2026-10-03 09:50:26.072626**: wrote 'es_freqcontrast_spanish.osexp'
    - path: output/experiments/es_freqcontrast_spanish.osexp
    - rows: NA
    - md5: 77125398dc3b65a41cd504d5005526fc
- **2026-10-03 09:50:26.221654**: wrote 'es_freqcontrast_spanish.html'
    - path: output/experiments/es_freqcontrast_spanish.html
    - rows: NA
    - md5: 0124c382fbd275f9afd0f71f5a983094
- **2026-10-03 09:50:27.342839**: wrote 'es_freqcontrast_spanish_datasheet_R.json'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.json
    - rows: NA
    - md5: 2c9ce0b8e528ca6b71532496c4de66e8
- **2026-10-03 09:50:27.499986**: wrote 'es_freqcontrast_spanish_datasheet_R.md'
    - path: output/reports/es_freqcontrast_spanish_datasheet_R.md
    - rows: NA
    - md5: 8ac8408d5fc18dfeb8ff9e92573bda4c
