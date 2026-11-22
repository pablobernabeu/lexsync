# Joint nearest-pair matching for a two-condition design

Selects the `n` best-matched pairs across the two conditions, keeping
only items that have a good counterpart. This equates the control
dimensions more tightly than per-anchor matching when the manipulation
is confounded with them (for example neighbourhood density with word
length). The costs are rounded, so the Python engine selects the same
pairs. Pairs of equal cost are taken in row order, which under
`tie_break = "hash"` is the hash rank of each word, and the same rule
breaks ties at the cap.

## Usage

``` r
match_joint(
  subpools,
  cond_names,
  match_on,
  center,
  scale_,
  n,
  cap = .PAIRWISE_CAP,
  tie_break = "bytes"
)
```
