# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 18:21:14.078636
- Finished: 2026-06-13 18:21:16.191466

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 18:21:14.082651** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 18:21:15.437369** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 18:21:15.465566** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-13 18:21:15.640333** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 18:21:15.754619** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-06-13 18:21:15.755179** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 18:21:15.75565** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-06-13 18:21:15.756036** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-13 18:21:15.8063** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: 1128d8936a37771df03a5d5368e55427
- **2026-06-13 18:21:15.826375** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-06-13 18:21:15.840318** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: e8463b1fa845a23c6a5041ad6e71577b
- **2026-06-13 18:21:16.161294** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 90f4887589d5cf98536ffb675e389d74
- **2026-06-13 18:21:16.166137** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
