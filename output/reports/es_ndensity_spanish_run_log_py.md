# lexsync run log: es_ndensity

- Engine: Python 3.13.7
- Started: 2026-10-13T18:19:20
- Finished: 2026-10-13T18:19:22

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13T18:19:20**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-13T18:19:20**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-13T18:19:20**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-13T18:19:20**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13T18:19:20**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-13T18:19:21**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.0009 (equivalent)
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.0 (not shown equivalent)
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.0 (not shown equivalent)
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.0025 (equivalent)
- **2026-10-13T18:19:22**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.9971 (not shown equivalent)
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_stimuli_py.csv'
    - path: output\stimuli\es_ndensity_spanish_stimuli_py.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_descriptives_py.csv'
    - path: output\reports\es_ndensity_spanish_descriptives_py.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_comparisons_py.csv'
    - path: output\reports\es_ndensity_spanish_comparisons_py.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output\experiments\es_ndensity_spanish_psychopy.py
    - rows: None
    - md5: 18766842968b9f2ad8c14f3fdb476ba4
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish.osexp'
    - path: output\experiments\es_ndensity_spanish.osexp
    - rows: None
    - md5: 8c8eebc14629634a183de1c163694b22
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish.html'
    - path: output\experiments\es_ndensity_spanish.html
    - rows: None
    - md5: 82ab9057a71eba46e95048fa4d88b7e6
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output\experiments\es_ndensity_spanish_psychopy.csv
    - rows: None
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame.csv
    - rows: None
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output\experiments\es_ndensity_spanish_opensesame_text.csv
    - rows: None
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_datasheet_py.json'
    - path: output\reports\es_ndensity_spanish_datasheet_py.json
    - rows: None
    - md5: 38ca00df2a9a096133187eb22345b939
- **2026-10-13T18:19:22**: wrote 'es_ndensity_spanish_datasheet_py.md'
    - path: output\reports\es_ndensity_spanish_datasheet_py.md
    - rows: None
    - md5: 50b0ec6156f881f005f534c40856259a
