# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-14 22:44:13.321495
- Finished: 2026-10-14 22:44:33.586331

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 22:44:13.347475**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-14 22:44:13.371502**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 22:44:13.38897**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-14 22:44:15.352746**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-14 22:44:15.399417**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-14 22:44:17.894697**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-14 22:44:19.21905**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-14 22:44:19.22926**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-14 22:44:19.243858**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.000 (not shown equivalent)
- **2026-10-14 22:44:19.251871**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.000 (not shown equivalent)
- **2026-10-14 22:44:19.279826**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-14 22:44:19.308015**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.997 (not shown equivalent)
- **2026-10-14 22:44:22.163137**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-10-14 22:44:22.662298**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-10-14 22:44:23.084737**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-10-14 22:44:32.622666**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 63967014cc401d205839a980d5558b58
- **2026-10-14 22:44:32.64675**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 0fbf8af2720d01862f213deaab1e4b7a
- **2026-10-14 22:44:32.715671**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: f5d9c36262588b3ec59b95ce4cb96cf0
- **2026-10-14 22:44:32.756609**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-10-14 22:44:32.790426**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-14 22:44:32.832547**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-10-14 22:44:33.49294**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: 2d46e15bdaa06ff728252a74ff256cb0
- **2026-10-14 22:44:33.550614**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 17e92edfab098ad5430ffde259fc981f
