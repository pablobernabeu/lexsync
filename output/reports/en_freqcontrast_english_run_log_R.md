# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 21:40:55.702638
- Finished: 2026-06-13 21:40:57.477345

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 21:40:55.705167** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 21:40:56.982089** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 21:40:56.996844** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-13 21:40:57.101432** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 21:40:57.166678** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-06-13 21:40:57.166856** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 21:40:57.166973** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-06-13 21:40:57.167076** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-13 21:40:57.210858** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: 1128d8936a37771df03a5d5368e55427
- **2026-06-13 21:40:57.227609** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-06-13 21:40:57.240083** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: e8463b1fa845a23c6a5041ad6e71577b
- **2026-06-13 21:40:57.446901** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 90f4887589d5cf98536ffb675e389d74
- **2026-06-13 21:40:57.45326** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
- **2026-06-13 21:40:57.457407** -- wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 5ea9473e534314ccf9b4b9a0fd6ae90e
