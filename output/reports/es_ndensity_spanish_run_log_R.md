# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-11-02 21:29:09.24805
- Finished: 2026-11-02 21:29:11.877012

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-11-02 21:29:09.248994**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-11-02 21:29:09.249154**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-11-02 21:29:09.249353**: loading lexicon 'corpora/derived/es.csv'
- **2026-11-02 21:29:09.688301**: lexicon loaded: 30000 words
    - words: 30000
- **2026-11-02 21:29:09.692021**: pool after filters: 4002 words
    - pool: 4002
- **2026-11-02 21:29:10.893937**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-11-02 21:29:11.487331**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-11-02 21:29:11.487766**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-11-02 21:29:11.48832**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.000 (not shown equivalent)
- **2026-11-02 21:29:11.488746**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.000 (not shown equivalent)
- **2026-11-02 21:29:11.489106**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-11-02 21:29:11.489463**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.997 (not shown equivalent)
- **2026-11-02 21:29:11.528408**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-11-02 21:29:11.533169**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-11-02 21:29:11.536628**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-11-02 21:29:11.817861**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: ad4ed2b863a2b3bd852257d8f2050899
- **2026-11-02 21:29:11.818259**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 0fbf8af2720d01862f213deaab1e4b7a
- **2026-11-02 21:29:11.818609**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: d70c046cb334be2f6b147ad5e0bc9e95
- **2026-11-02 21:29:11.818984**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-11-02 21:29:11.819296**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-11-02 21:29:11.819598**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-11-02 21:29:11.876096**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 65b1582ba89f3f8591c39249b0638f24
- **2026-11-02 21:29:11.876486**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: ffc14aab589f1a792bdb554212f702c3
