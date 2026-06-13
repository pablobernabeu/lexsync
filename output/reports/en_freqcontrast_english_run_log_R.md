# lexsync run log: en_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 22:14:38.604857
- Finished: 2026-06-13 22:14:41.129977

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:14:38.634994** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 22:14:40.268905** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 22:14:40.287687** -- pool after filters: 7230 words
    - pool: 7230
- **2026-06-13 22:14:40.412873** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 22:14:40.487016** -- equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-06-13 22:14:40.487221** -- equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:40.487344** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-06-13 22:14:40.48745** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-06-13 22:14:40.524351** -- wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: d18c7660e0747e5f8e276af9c27446bf
- **2026-06-13 22:14:40.538012** -- wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-06-13 22:14:40.54959** -- wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: e8463b1fa845a23c6a5041ad6e71577b
- **2026-06-13 22:14:40.820214** -- wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 90f4887589d5cf98536ffb675e389d74
- **2026-06-13 22:14:40.82588** -- wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: 6af45f8fa24cfd73ef12ef2073f9f4f2
- **2026-06-13 22:14:40.831061** -- wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 5ea9473e534314ccf9b4b9a0fd6ae90e
- **2026-06-13 22:14:41.088477** -- wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: da30c992767a5b0394f2495568ddad52
- **2026-06-13 22:14:41.096074** -- wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: eee3c0f4a5152cf5bdebdb9d9c0cb0f8
