# lexsync run log: zh_freqcontrast

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:05.094522
- Finished: 2026-09-02 19:25:05.629864

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:05.094795**: loading lexicon 'corpora/derived/zh.csv'
- **2026-09-02 19:25:05.330214**: lexicon loaded: 20000 words
    - words: 20000
- **2026-09-02 19:25:05.33437**: pool after filters: 13613 words
    - pool: 13613
- **2026-09-02 19:25:05.573016**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-09-02 19:25:05.582497**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.0000 (equivalent)
- **2026-09-02 19:25:05.582746**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:05.582921**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.0037 (equivalent)
- **2026-09-02 19:25:05.583047**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.0069 (equivalent)
- **2026-09-02 19:25:05.592182**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-09-02 19:25:05.594297**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-09-02 19:25:05.596081**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: eab9f98b6a500d9f8914616bd62f9b30
- **2026-09-02 19:25:05.614216**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: c7ba62668b013e8705048f015e694f86
- **2026-09-02 19:25:05.614403**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 61241d2f316024fe20ddc8ea700d7816
- **2026-09-02 19:25:05.614498**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 0ad2a8ba376cfe37545113b2c24e5b7f
- **2026-09-02 19:25:05.629534**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: d518124c56399e60dffe170344ddc742
- **2026-09-02 19:25:05.629705**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 16baa9561f03566d923e956b98c33832
