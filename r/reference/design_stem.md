# The stem every file a design writes is named after

The slug of the design's `name` and `language`, which keeps letters and
digits only. Two designs whose names differ only outside ASCII (two
Chinese names, both with the language `chinese`) would share a slug and
overwrite each other's files, and an all-Chinese name and language would
give no slug at all. Whenever the name or the language holds a non-ASCII
character, the stem therefore gains `_` and the first eight hexadecimal
digits of the SHA-256 of the NFC-normalised UTF-8 text `name|language`.
An empty slug is replaced by those eight digits. NFC keeps a precomposed
and a decomposed accented letter on one stem. A design whose name and
language hold no letter or digit at all is refused. Mirrors
`design_stem()` in the Python package.

## Usage

``` r
design_stem(design)
```

## Arguments

- design:

  A parsed design configuration.

## Value

The file stem, such as `"en_lexdec_english"` or `"chinese_14aadfa7"`.

## Examples

``` r
design_stem(list(name = "en_lexdec", language = "english"))
#> [1] "en_lexdec_english"
# Two Chinese characters, written as code points to keep this file ASCII.
design_stem(list(name = intToUtf8(c(0x8bcd, 0x9891)), language = "chinese"))
#> [1] "chinese_14aadfa7"
```
