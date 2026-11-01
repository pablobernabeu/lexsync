# A length-matched pseudoword for each base word (byte-order processing)

A length-matched pseudoword for each base word (byte-order processing)

## Usage

``` r
generate_pseudowords(base_words, reference_words, exclude = NULL)
```

## Arguments

- base_words:

  Character vector of words to derive pseudowords from.

- reference_words:

  Character vector (typically the full lexicon) that supplies the bigram
  statistics and the real word forms to avoid.

- exclude:

  Optional character vector of further word forms no pseudoword may
  equal, such as low-frequency words the reference lacks. They are
  trimmed, lower-cased and put in Unicode NFC, as a lexicon's words are,
  and play no part in the bigram statistics.

## Value

A data frame with columns `base_word` and `pseudoword`.

## Details

The letters substituted in are those the reference words attest, so a
Spanish reference lends the generator its accented vowels. A base word
in a logographic script, such as Chinese, is refused.
