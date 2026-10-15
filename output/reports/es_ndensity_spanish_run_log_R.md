# lexsync run log: es_ndensity

- Engine: R 4.6.1
- Started: 2026-10-15 03:29:58.070596
- Finished: 2026-10-15 03:30:03.628173

## Run metadata

- design: es_ndensity
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-15 03:29:58.082749**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-15 03:29:58.093091**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-15 03:29:58.100656**: loading lexicon 'corpora/derived/es.csv'
- **2026-10-15 03:29:59.158453**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-15 03:29:59.177849**: pool after filters: 4002 words
    - pool: 4002
- **2026-10-15 03:30:01.547427**: matched 160 items across 2 conditions
    - conditions: dense_neighbourhood, sparse_neighbourhood
- **2026-10-15 03:30:02.529079**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'length': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-15 03:30:02.541552**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'frequency': d = 0.00 [-0.26, 0.26], TOST p = 0.001 (equivalent)
- **2026-10-15 03:30:02.553185**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_density': d = 3.06 [2.67, 3.44], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 03:30:02.562807**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'old20': d = -2.57 [-2.92, -2.21], TOST p = 1.000 (not shown equivalent)
- **2026-10-15 03:30:02.570772**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'n_syllables': d = 0.05 [-0.21, 0.31], TOST p = 0.002 (equivalent)
- **2026-10-15 03:30:02.578327**: equivalence sparse_neighbourhood vs dense_neighbourhood on 'bigram_freq': d = 0.94 [0.67, 1.22], TOST p = 0.997 (not shown equivalent)
- **2026-10-15 03:30:02.653231**: wrote 'es_ndensity_spanish_stimuli_R.csv'
    - path: output/stimuli/es_ndensity_spanish_stimuli_R.csv
    - rows: 160
    - md5: d2ccfa6a4f92fd113536fc9fa2cea732
- **2026-10-15 03:30:02.684951**: wrote 'es_ndensity_spanish_descriptives_R.csv'
    - path: output/reports/es_ndensity_spanish_descriptives_R.csv
    - rows: 12
    - md5: bafaffe29d74437d95fc7d47f1688d67
- **2026-10-15 03:30:02.710719**: wrote 'es_ndensity_spanish_comparisons_R.csv'
    - path: output/reports/es_ndensity_spanish_comparisons_R.csv
    - rows: 6
    - md5: 935efd702f4a1d1bdcaa1cf275b35e8a
- **2026-10-15 03:30:03.228684**: wrote 'es_ndensity_spanish_psychopy.py'
    - path: output/experiments/es_ndensity_spanish_psychopy.py
    - rows: NA
    - md5: 4c17d8df6f5897df0f81e78b32e38133
- **2026-10-15 03:30:03.242137**: wrote 'es_ndensity_spanish.osexp'
    - path: output/experiments/es_ndensity_spanish.osexp
    - rows: NA
    - md5: 0fbf8af2720d01862f213deaab1e4b7a
- **2026-10-15 03:30:03.255546**: wrote 'es_ndensity_spanish.html'
    - path: output/experiments/es_ndensity_spanish.html
    - rows: NA
    - md5: d7f32ef5e098226458e3e7d5645b04bb
- **2026-10-15 03:30:03.27349**: wrote 'es_ndensity_spanish_psychopy.csv'
    - path: output/experiments/es_ndensity_spanish_psychopy.csv
    - rows: NA
    - md5: 93b8d65df86e5849266de4ff36448b17
- **2026-10-15 03:30:03.288327**: wrote 'es_ndensity_spanish_opensesame.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame.csv
    - rows: NA
    - md5: 10d00e0ed94b42e55bcde65c6122e822
- **2026-10-15 03:30:03.3018**: wrote 'es_ndensity_spanish_opensesame_text.csv'
    - path: output/experiments/es_ndensity_spanish_opensesame_text.csv
    - rows: NA
    - md5: d1b530d52a88147ed8bc2011ad240508
- **2026-10-15 03:30:03.574388**: wrote 'es_ndensity_spanish_datasheet_R.json'
    - path: output/reports/es_ndensity_spanish_datasheet_R.json
    - rows: NA
    - md5: b00f7b1f8edc164d8c93b32ae36ef844
- **2026-10-15 03:30:03.598848**: wrote 'es_ndensity_spanish_datasheet_R.md'
    - path: output/reports/es_ndensity_spanish_datasheet_R.md
    - rows: NA
    - md5: 17e92edfab098ad5430ffde259fc981f
