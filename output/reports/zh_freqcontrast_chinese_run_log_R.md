# lexsync run log: zh_freqcontrast

- Engine: R 4.5.1
- Started: 2026-06-13 22:14:49.446807
- Finished: 2026-06-13 22:14:50.496899

## Run metadata

- design: zh_freqcontrast
- language: chinese
- paradigm: factorial
- source: corpus
- seed: 2026

## Steps

- **2026-06-13 22:14:49.447602** -- loading lexicon 'corpora/derived/zh.csv'
- **2026-06-13 22:14:49.838512** -- lexicon loaded: 20000 words
    - words: 20000
- **2026-06-13 22:14:49.846206** -- pool after filters: 13613 words
    - pool: 13613
- **2026-06-13 22:14:50.164943** -- matched 160 items across 2 conditions
    - conditions: high_frequency, low_frequency
- **2026-06-13 22:14:50.179547** -- equivalence low_frequency vs high_frequency on 'length': d = 0.00 [0.00, 0.00], TOST p = 0.000 (equivalent)
- **2026-06-13 22:14:50.179923** -- equivalence low_frequency vs high_frequency on 'frequency': d = 6.00 [5.74, 6.27], TOST p = 1.000 (not shown equivalent)
- **2026-06-13 22:14:50.180231** -- equivalence low_frequency vs high_frequency on 'n_density': d = 0.07 [-0.19, 0.33], TOST p = 0.004 (equivalent)
- **2026-06-13 22:14:50.18049** -- equivalence low_frequency vs high_frequency on 'old20': d = 0.11 [-0.15, 0.37], TOST p = 0.007 (equivalent)
- **2026-06-13 22:14:50.222093** -- wrote 'zh_freqcontrast_chinese_stimuli_R.csv'
    - path: output/stimuli/zh_freqcontrast_chinese_stimuli_R.csv
    - rows: 160
    - md5: 09122d7d5b86f5e05be0f1905635291b
- **2026-06-13 22:14:50.235648** -- wrote 'zh_freqcontrast_chinese_descriptives_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_descriptives_R.csv
    - rows: 8
    - md5: ce89f99a54869edd10fb8193ca32a893
- **2026-06-13 22:14:50.249038** -- wrote 'zh_freqcontrast_chinese_comparisons_R.csv'
    - path: output/reports/zh_freqcontrast_chinese_comparisons_R.csv
    - rows: 4
    - md5: 1865ab1b5e96037795319fde3d0619e6
- **2026-06-13 22:14:50.360947** -- wrote 'zh_freqcontrast_chinese_psychopy.py'
    - path: output/experiments/zh_freqcontrast_chinese_psychopy.py
    - rows: NA
    - md5: dd2f6fe8c5d6aa98d9c738b457160d72
- **2026-06-13 22:14:50.366829** -- wrote 'zh_freqcontrast_chinese.osexp'
    - path: output/experiments/zh_freqcontrast_chinese.osexp
    - rows: NA
    - md5: ccda579609c93d507d1b2d7226d45db3
- **2026-06-13 22:14:50.371739** -- wrote 'zh_freqcontrast_chinese.html'
    - path: output/experiments/zh_freqcontrast_chinese.html
    - rows: NA
    - md5: 1f2d7a6495c1e2a75df3bfeab68d82ea
- **2026-06-13 22:14:50.480778** -- wrote 'zh_freqcontrast_chinese_datasheet_R.json'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.json
    - rows: NA
    - md5: 71110778ef762ddaf1d5344f90b0cdd4
- **2026-06-13 22:14:50.488058** -- wrote 'zh_freqcontrast_chinese_datasheet_R.md'
    - path: output/reports/zh_freqcontrast_chinese_datasheet_R.md
    - rows: NA
    - md5: 11a6f22f21a6b5d7b090f90468a1be12
