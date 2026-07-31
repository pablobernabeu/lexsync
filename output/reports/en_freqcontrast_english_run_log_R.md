# lexsync run log: en_freqcontrast

- Engine: R 4.6.1
- Started: 2026-07-31 22:35:02.928977
- Finished: 2026-07-31 22:35:03.887721

## Run metadata

- design: en_freqcontrast
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 22:35:02.932989**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 22:35:03.308058**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 22:35:03.318533**: pool after filters: 7230 words
    - pool: 7230
- **2026-07-31 22:35:03.435241**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-07-31 22:35:03.454427**: equivalence low_frequency vs high_frequency on 'length': d = 0.03 [-0.23, 0.29], TOST p = 0.002 (equivalent)
- **2026-07-31 22:35:03.459676**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.27 [5.01, 5.53], TOST p = 1.000 (not shown equivalent)
- **2026-07-31 22:35:03.462468**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.04 [-0.22, 0.30], TOST p = 0.002 (equivalent)
- **2026-07-31 22:35:03.466969**: equivalence low_frequency vs high_frequency on 'old20': d = 0.01 [-0.25, 0.27], TOST p = 0.001 (equivalent)
- **2026-07-31 22:35:03.51501**: wrote 'en_freqcontrast_english_stimuli_R.csv'
    - path: output/stimuli/en_freqcontrast_english_stimuli_R.csv
    - rows: 160
    - md5: b271a09350cb0f0ea64671812a388be3
- **2026-07-31 22:35:03.540338**: wrote 'en_freqcontrast_english_descriptives_R.csv'
    - path: output/reports/en_freqcontrast_english_descriptives_R.csv
    - rows: 8
    - md5: b8426804e118105c1f3a3b5fb3eebc5c
- **2026-07-31 22:35:03.559828**: wrote 'en_freqcontrast_english_comparisons_R.csv'
    - path: output/reports/en_freqcontrast_english_comparisons_R.csv
    - rows: 4
    - md5: 64f1dfc21c853deec090da7694d39813
- **2026-07-31 22:35:03.708514**: wrote 'en_freqcontrast_english_psychopy.py'
    - path: output/experiments/en_freqcontrast_english_psychopy.py
    - rows: NA
    - md5: 8854499757ec3dbb9780a892f5750703
- **2026-07-31 22:35:03.727186**: wrote 'en_freqcontrast_english.osexp'
    - path: output/experiments/en_freqcontrast_english.osexp
    - rows: NA
    - md5: bbefbff96a23c2161652c3ccb864350f
- **2026-07-31 22:35:03.740343**: wrote 'en_freqcontrast_english.html'
    - path: output/experiments/en_freqcontrast_english.html
    - rows: NA
    - md5: 2f421b02cc4cb3d7275da9ba1f4f5bdf
- **2026-07-31 22:35:03.863149**: wrote 'en_freqcontrast_english_datasheet_R.json'
    - path: output/reports/en_freqcontrast_english_datasheet_R.json
    - rows: NA
    - md5: 3f7b661c07c13719fd8b500ab303928a
- **2026-07-31 22:35:03.877781**: wrote 'en_freqcontrast_english_datasheet_R.md'
    - path: output/reports/en_freqcontrast_english_datasheet_R.md
    - rows: NA
    - md5: 063549071c95785b03f5a5886e920e8e
