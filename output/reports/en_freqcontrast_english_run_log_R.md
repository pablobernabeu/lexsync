# lexsync run log: en_freqcontrast

- Engine: R 4.3.3
- Started: 2026-09-02 19:24:54.861457
- Finished: 2026-09-02 19:24:55.336982

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:24:54.861679**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:24:55.142445**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:24:55.147676**: pool after filters: 7230 words
    - pool: 7230
- **2026-09-02 19:24:55.272072**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:24:55.28374**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.0016 (equivalent)
- **2026-09-02 19:24:55.284001**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:24:55.284148**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.0020 (equivalent)
- **2026-09-02 19:24:55.284273**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.0011 (equivalent)
- **2026-09-02 19:24:55.294039**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-09-02 19:24:55.296266**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: b8426804e118105c1f3a3b5fb3eebc5c
- **2026-09-02 19:24:55.298444**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-09-02 19:24:55.318867**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 6b142f2efeb59283250df4653d6acfbc
- **2026-09-02 19:24:55.319064**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-09-02 19:24:55.319171**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 155164b2741f0ec43d1f3616784f480b
- **2026-09-02 19:24:55.336618**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 756f2c09dd05137a1a8cb7697b4d807f
- **2026-09-02 19:24:55.336809**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 7d0b0cd597bc0cd4498b6a9f83a1db24
