# Corpus attribution

Lexical corpora used by lexsync, with their sources, licences and retrieval
dates. Bundled derivatives are distributed under CC BY-SA 4.0 (see LICENSE-DATA).

## Demonstration corpora (bundled)

- **English ('en')** — 30000 words, Zipf 2.95-7.73. Source: wordfreq (Speer, 2022; MIT), retrieved 2026-06-08. N and OLD20 computed by lexsync.
- **Spanish ('es')** — 30000 words, Zipf 3.11-7.81. Source: wordfreq (Speer, 2022; MIT), retrieved 2026-06-08. N and OLD20 computed by lexsync.
- **Chinese (Mandarin) ('zh')** — 20000 words, Zipf 3.31-6.56. Source: wordfreq (Speer, 2022; MIT), retrieved 2026-06-10. N and OLD20 computed over characters by lexsync. The logographic-script demonstration.
- **Spanish gender ('es_gender')** — 10185 words. A derivative of the 'es' corpus above, restricted to words with canonical Spanish gender endings (-a feminine, -o masculine; gerunds excluded) and tagged with a `gender` column. Used by the demonstration that reproduces the gender-assignment design of Gonzalez Alonso et al. (2025). Grammatical gender is approximated by word ending, not looked up in a lexical database (the original used EsPal; Duchon et al., 2013).

## Data currency and reproducibility

The bundled derived corpora above are a fixed, dated, checksummed snapshot, so the
demonstrations reproduce exactly with no network access or corpus download. The
optional `wordfreq` connector (used only to fetch further languages) draws on
wordfreq's frozen data: the package was retired in September 2024 and is no longer
updated, because generative-AI text had begun to distort web-derived word
frequencies (Speer, 2024, `SUNSET.md`). For lexsync this is a strength: `wordfreq`
3.x is a stable snapshot of human language usage through
roughly 2021, so a fetch today returns the same frequencies as a fetch next year,
and every derived corpus records its retrieval date and checksum. lexsync pins the
connector to the 3.x line for this reason.

## Citations

- Speer, R. (2022). rspeer/wordfreq: v3.0. Zenodo. https://doi.org/10.5281/zenodo.7199437
- van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). SUBTLEX-UK. Quarterly Journal of Experimental Psychology, 67(6), 1176-1190. https://doi.org/10.1080/17470218.2013.850521
- Cuetos, F., Gonzalez-Nosti, M., Barbon, A., & Brysbaert, M. (2011). SUBTLEX-ESP. Psicologica, 32(2), 133-143.
- See corpora/registry.yaml for the full list of curated, individually citable SUBTLEX/openlexicon corpora that lexsync supports.
