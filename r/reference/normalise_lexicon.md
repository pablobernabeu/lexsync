# Turn a corpus file in its publisher's layout into a lexicon

Reads a tab- or comma-separated corpus file, such as SUBTLEX-US or
Lexique as they are published, and returns a lexicon that
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
reads, writing it to `out` when given.

## Usage

``` r
normalise_lexicon(
  path,
  columns = NULL,
  entry = NULL,
  delimiter = NULL,
  out = NULL
)
```

## Arguments

- path:

  Path to the corpus file.

- columns:

  Optional named list mapping lexsync's column names to the file's, as a
  registry entry's `columns` does: `word`, one of `freq_zipf` and
  `freq_permillion`, and optionally `pos`. Without a map, the entry's is
  used, and without either the file's own `word`, `freq_zipf` or
  `freq_permillion`, and `pos` columns are read.

- entry:

  Optional registry entry, as a list, or the name of one in the registry
  lexsync finds by default (see
  [`list_corpora()`](https://pablobernabeu.github.io/lexsync/r/reference/list_corpora.md)).
  It supplies the map when `columns` is `NULL`, and the `duplicates`
  rule.

- delimiter:

  `","` or a tab character. Left `NULL`, it is taken from the extension
  (`.tsv` and `.tab` are tab-separated, `.csv` comma-separated) and
  otherwise from the header line, which is tab-separated when it holds a
  tab. A tab-separated file is read with no quoting.

- out:

  Optional path to write the lexicon to, comma-separated with LF line
  endings.

## Value

The lexicon, invisibly when `out` is given: a data frame with `word`,
`freq_zipf`, then `freq_permillion` when Zipf was derived from it, and
`pos` when the file has one, in the UTF-8 byte order of `word`. Its
attribute `normalisation` holds
`list(n_read, n_forms, n_merged, duplicates, zipf_derived, near_boundary)`.

## Details

Words are trimmed, lower-cased and put in Unicode NFC, as
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
keys them, and rows missing a word or a frequency are dropped. A form
that then appears more than once is resolved by the entry's `duplicates`
rule: `"first"` (the default) keeps the first row in file order, and
`"sum"` adds its rows' frequencies per million, as Lexique needs, since
it splits a homograph's frequency between its rows. Frequencies per
million are converted with Zipf = log10(per million) + 3, rounded to
three places by lexsync's shared rounder. A value of 0 or below has no
Zipf value and is refused. Zipf values read as they are must lie between
0 and 9.

A message gives the number of forms and, for derived Zipf values, the
number that lay within 1e-9 of a rounding boundary after scaling. That
is the only step at which the two engines' `log10` could round a value
apart, and the count is expected to be 0. A run over the lexicon records
the count in its run log and datasheet.

## See also

[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md),
which downloads a registered corpus and normalises it the same way.

## Examples

``` r
# A SUBTLEX-US-like table, written to a temporary file.
path <- tempfile(fileext = ".tsv")
writeLines(c("Word\tSUBTLWF\tDom_PoS_SUBTLEX", "the\t29449.18\tArticle",
             "Dog\t192.76\tNoun"), path)
normalise_lexicon(path, columns = list(word = "Word", freq_permillion = "SUBTLWF",
                                       pos = "Dom_PoS_SUBTLEX"))
#> lexsync: normalised 2 forms from 'file18c667545047.tsv'; 0 of the Zipf values derived from frequencies per million lay within 1e-9 of a rounding boundary.
#>   word freq_zipf freq_permillion     pos
#> 1  dog     5.285          192.76    Noun
#> 2  the     7.469        29449.18 Article
unlink(path)
```
