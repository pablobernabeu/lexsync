# lexsync run log: en_richdim

- Engine: R 4.6.1
- Started: 2026-10-02 12:20:30.437322
- Finished: 2026-10-02 12:20:38.508263

## Run metadata

- design: en_richdim
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 12:20:30.897226**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 12:20:32.679023**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 12:20:32.735387**: pool after filters: 10205 words
    - pool: 10205
- **2026-10-02 12:20:32.758805**: computing bigram frequency (phonotactic-probability proxy)
- **2026-10-02 12:20:34.939529**: matched 120 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-02 12:20:35.052471**: equivalence low_frequency vs high_frequency on 'length': d = 0.01 [-0.29, 0.32], TOST p = 0.004 (equivalent)
- **2026-10-02 12:20:35.063759**: equivalence low_frequency vs high_frequency on 'frequency': d = 5.57 [4.90, 6.24], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 12:20:35.094642**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.08 [-0.23, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-02 12:20:35.119661**: equivalence low_frequency vs high_frequency on 'old20': d = 0.08 [-0.22, 0.38], TOST p = 0.011 (equivalent)
- **2026-10-02 12:20:35.167922**: equivalence low_frequency vs high_frequency on 'n_syllables': d = 0.17 [-0.13, 0.48], TOST p = 0.038 (equivalent)
- **2026-10-02 12:20:35.222942**: equivalence low_frequency vs high_frequency on 'bigram_freq': d = 0.01 [-0.29, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-02 12:20:35.935279**: wrote 'en_richdim_english_stimuli_R.csv'
    - path: output/stimuli/en_richdim_english_stimuli_R.csv
    - rows: 120
    - md5: 9dc5f5642000f89a4ddcafe72a18ff05
- **2026-10-02 12:20:36.326719**: wrote 'en_richdim_english_descriptives_R.csv'
    - path: output/reports/en_richdim_english_descriptives_R.csv
    - rows: 12
    - md5: 3bb9bd2d9181ecb0a19a4d79b547c252
- **2026-10-02 12:20:36.378403**: wrote 'en_richdim_english_comparisons_R.csv'
    - path: output/reports/en_richdim_english_comparisons_R.csv
    - rows: 6
    - md5: c6e0f0a19b0b176fdd5a9ad80946e658
- **2026-10-02 12:20:37.661861**: wrote 'en_richdim_english_psychopy.py'
    - path: output/experiments/en_richdim_english_psychopy.py
    - rows: NA
    - md5: ef7ebc10229e3d031c02ea4ae56b8fc1
- **2026-10-02 12:20:37.717426**: wrote 'en_richdim_english.osexp'
    - path: output/experiments/en_richdim_english.osexp
    - rows: NA
    - md5: d51ed336f89ea0b2009be22e506583ea
- **2026-10-02 12:20:37.768996**: wrote 'en_richdim_english.html'
    - path: output/experiments/en_richdim_english.html
    - rows: NA
    - md5: 6886e9083af3453ef3c5f23124bcadcd
- **2026-10-02 12:20:38.397697**: wrote 'en_richdim_english_datasheet_R.json'
    - path: output/reports/en_richdim_english_datasheet_R.json
    - rows: NA
    - md5: 3a6f8911b7aa767900032eedbf73b228
- **2026-10-02 12:20:38.479553**: wrote 'en_richdim_english_datasheet_R.md'
    - path: output/reports/en_richdim_english_datasheet_R.md
    - rows: NA
    - md5: 504bde3461230c3459a7f188d27b2288
