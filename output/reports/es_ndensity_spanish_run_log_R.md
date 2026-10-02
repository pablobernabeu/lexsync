# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-02 16:47:41.024018
- Finished: 2026-10-02 16:48:09.095853

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 16:47:41.059129**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-02 16:47:43.531447**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 16:47:43.644691**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-02 16:47:46.454944**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-02 16:47:46.900796**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-02 16:47:46.951929**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-02 16:47:47.018017**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 2.13 [1.80, 2.46], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:47:47.027632**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.42 [-2.77, -2.08], TOST p = 1.000 (not shown equivalent)
- **2026-10-02 16:47:50.841627**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: 4d7fbe0cdfc7cee292f8eb3ddf8a6daa
- **2026-10-02 16:47:51.376963**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 8
    - md5: 7d78dd5a29280cabaf402ea59301a059
- **2026-10-02 16:47:51.719402**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 4
    - md5: 70c9db12a708fc06bf941740f3107481
- **2026-10-02 16:48:05.575558**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: d330eb5c72303ea33b91e95699543464
- **2026-10-02 16:48:05.628804**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: b95c22b0f149eae2036eb64000c22376
- **2026-10-02 16:48:05.703324**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: e8e07c918578b4c676700dc457b00e8b
- **2026-10-02 16:48:08.81054**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 2947efead3a70871ff5cfdeb6221b5d8
- **2026-10-02 16:48:08.966145**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 8e71cdab731ce0541ec3fd41206c822e
