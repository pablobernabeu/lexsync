# lexsync run log: en_ndensity

- Engine: R 4.3.3
- Started: 2026-09-02 19:25:00.394685
- Finished: 2026-09-02 19:25:01.454854

## Run metadata

- design: en_ndensity
- language: english
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-09-02 19:25:00.394931**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-02 19:25:00.601058**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-02 19:25:00.605336**: pool after filters: 4557 words
    - pool: 4557
- **2026-09-02 19:25:01.390056**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-09-02 19:25:01.399481**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-09-02 19:25:01.399721**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-09-02 19:25:01.399927**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.11 [2.85, 3.37], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:01.40007**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.30 [-2.56, -2.04], TOST p = 1.0000 (not shown equivalent)
- **2026-09-02 19:25:01.410621**: wrote 'en_ndensity_english_stimuli_R.csv'
    - path: output/stimuli/en_ndensity_english_stimuli_R.csv
    - rows: 160
    - md5: 2f785563afd3cc575320ac35dbea3ea5
- **2026-09-02 19:25:01.413148**: wrote 'en_ndensity_english_descriptives_R.csv'
    - path: output/reports/en_ndensity_english_descriptives_R.csv
    - rows: 8
    - md5: 25e02256139ad746974a981fa0ba78f1
- **2026-09-02 19:25:01.415269**: wrote 'en_ndensity_english_comparisons_R.csv'
    - path: output/reports/en_ndensity_english_comparisons_R.csv
    - rows: 4
    - md5: 4fef67902e35e37dacf4d9a21430677e
- **2026-09-02 19:25:01.435498**: wrote 'en_ndensity_english_psychopy.py'
    - path: output/experiments/en_ndensity_english_psychopy.py
    - rows: NA
    - md5: dc913390d4b749bdefbb60542d45f529
- **2026-09-02 19:25:01.435774**: wrote 'en_ndensity_english.osexp'
    - path: output/experiments/en_ndensity_english.osexp
    - rows: NA
    - md5: 15cadda213e1698d46019bffd5677d2f
- **2026-09-02 19:25:01.435932**: wrote 'en_ndensity_english.html'
    - path: output/experiments/en_ndensity_english.html
    - rows: NA
    - md5: 27b16016d15a0ee534f72a31bb1d1a14
- **2026-09-02 19:25:01.454427**: wrote 'en_ndensity_english_datasheet_R.json'
    - path: output/reports/en_ndensity_english_datasheet_R.json
    - rows: NA
    - md5: b8b03269b3cc5cf2adb873a099a91b2b
- **2026-09-02 19:25:01.454684**: wrote 'en_ndensity_english_datasheet_R.md'
    - path: output/reports/en_ndensity_english_datasheet_R.md
    - rows: NA
    - md5: 05138aa562251b91528196209dce2936
