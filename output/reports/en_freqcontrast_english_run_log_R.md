# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-17 01:38:35.133189
- Finished: 2026-07-17 01:38:36.253484

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-17 01:38:35.137171**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-17 01:38:35.587204**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-17 01:38:35.599658**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-17 01:38:35.721696**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-17 01:38:35.748819**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-17 01:38:35.755324**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-17 01:38:35.760856**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-17 01:38:35.767039**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-17 01:38:35.862808**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-07-17 01:38:35.895152**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: c206bf297a484887ee52e2745fb9ad24
- **2026-07-17 01:38:35.917466**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-17 01:38:36.063083**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 865d0243fecb10f504bc9d87bf69d583
- **2026-07-17 01:38:36.079367**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-07-17 01:38:36.09141**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: c73184037a60da2a3f0e30148e801de3
- **2026-07-17 01:38:36.224206**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 881a0379d77a4eda5085d96259f124a7
- **2026-07-17 01:38:36.238504**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: d25b75f9fda4f716ff8e74bcc91aa665
