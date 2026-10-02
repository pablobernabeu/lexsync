# lexsync run log: zh_freqcontrast

- Engine: R 4.6.1
- Started: 2026-10-02 16:48:09.354172
- Finished: 2026-10-02 16:48:26.428929

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:48:09.388845**: loading lexicon 'corpora/derived/zh.csv'
- **2026-10-02 16:48:10.962327**: lexicon loaded: 20000 words
    - words: 20000
- **2026-10-02 16:48:11.139273**: pool after filters: 13613 words
    - pool: 13613
- **2026-10-02 16:48:12.400451**: matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-10-02 16:48:12.610147**: equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-10-02 16:48:13.01294**: equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.39, 6.62], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:48:13.05494**: equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-10-02 16:48:13.39485**: equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.16, 0.37], TOST p = 0.007 (equivalent)
- **2026-10-02 16:48:13.724105**: wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 696c6e672dbfab97f0f90a7f5ff60067
- **2026-10-02 16:48:15.055117**: wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: 83e6b799f70ff4dedee81fce775e7267
- **2026-10-02 16:48:15.600093**: wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 9823b728460d1fa1069400ef92b274d5
- **2026-10-02 16:48:24.991652**: wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: e125056b7a1fae42e45ee23c544b0077
- **2026-10-02 16:48:25.014064**: wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: 3ecf66dcf5b8337c44c7d36fe85756ec
- **2026-10-02 16:48:25.047339**: wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 04f5aba638eeed04e20d12e5763d50a7
- **2026-10-02 16:48:26.125533**: wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 2ffd0881ff2de2991825be5c4422609d
- **2026-10-02 16:48:26.243226**: wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 67918ae25c4ff805321d08f235aafac1
