# lexsync run log: en_freqcontrast

- Engine: R 4.6.0
- Started: 2026-07-06 10:27:16.54331
- Finished: 2026-07-06 10:27:18.204124

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06 10:27:16.551231**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-06 10:27:17.174192**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-06 10:27:17.18984**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-06 10:27:17.359653**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-06 10:27:17.411239**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-06 10:27:17.419636**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-06 10:27:17.428397**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-06 10:27:17.439498**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-06 10:27:17.520157**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d18c7660e0747e5f8e276af9c27446bf
- **2026-07-06 10:27:17.543414**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-06 10:27:17.583251**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-06 10:27:17.869345**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 7db19120a7d77ee5be2640b68dfff7b3
- **2026-07-06 10:27:17.900645**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
- **2026-07-06 10:27:17.919398**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 9308f54572196f2f21e01f7ac9dbf98b
- **2026-07-06 10:27:18.159282**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 27d7553c5a53ddd92e965f471ff8401b
- **2026-07-06 10:27:18.179668**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: bdd4c00eaa28b1cd8bb915f5b9f5097e
