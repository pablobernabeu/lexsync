# Optimal pairing for a two-condition design: the `n` pairs of least summed distance

Selecting n disjoint pairs from two pools at least total cost is the
k-cardinality assignment problem. It is solved exactly by padding the
cost matrix to a square assignment problem whose optimum uses exactly n
real pairs (Volgenant, 2004). Greedy `joint` matching takes the cheapest
disjoint pair at each step, so it can spend a hard item's only good
counterpart on an item that had alternatives. Pair matching of every
item in one condition is a different problem, for which optimal matching
was no better than greedy at balancing the controls (Gu & Rosenbaum,
1993). Needs the 'clue' package.

## Usage

``` r
match_optimal(
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

## Details

Both capped subpools are first put in tie-break order (see
`.tie_sort_order`), so the solver's preferences among equal costs follow
that order and not the spelling or the arrival order of the rows. Which
of several equally cheap sets of pairs the solver returns differs
between
[`clue::solve_LSAP()`](https://rdrr.io/pkg/clue/man/solve_LSAP.html) and
SciPy's `linear_sum_assignment()`, so the two engines agree on the
summed distance but not necessarily on the items. The pairs are numbered
by cost, then by the tie-break rank of each word.

When the conditions overlap, a word can sit in both subpools, and the
solve may pair it with itself or use one pair in both directions (x with
y and y with x). Those pairs are dropped, and the places left are filled
by solving again over the words not yet used, until `n` pairs are found
or no further pair exists. The selection is then no longer guaranteed to
have the least summed distance. For disjoint conditions, one solve
suffices.

## References

Gu, X. S., & Rosenbaum, P. R. (1993). Comparison of multivariate
matching methods: Structures, distances, and algorithms. *Journal of
Computational and Graphical Statistics, 2*(4), 405-420.
[doi:10.1080/10618600.1993.10474623](https://doi.org/10.1080/10618600.1993.10474623)

Volgenant, A. (2004). Solving the *k*-cardinality assignment problem by
transformation. *European Journal of Operational Research, 157*(2),
322-331.
[doi:10.1016/S0377-2217(03)00205-4](https://doi.org/10.1016/S0377-2217%2803%2900205-4)
