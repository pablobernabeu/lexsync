# Matching and designs

Selecting stimuli is the part of an experiment that most often decides what the experiment can
show, and it is the part that is least often written down. This guide follows a set from the corpus
to the finished selection: how a lexicon becomes a candidate pool, which dimensions can be equated,
what the four matching methods actually do, how to read the report that says whether the matching
worked, and what to do instead when dichotomising a predictor is the wrong move.

The examples run against the lexicon bundled with the package, so you can paste them into a session
and get the output shown. Only the norm-merging sketch needs a file of your own.

```python exec="1" source="material-block" session="matching"
from importlib.resources import files

import yaml

import lexsync

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))
lexicon = lexsync.load_lexicon(
    str(data / "en_example.csv"), schema, language="english"
)
```

## From lexicon to pool

`load_lexicon` reads a derived corpus and does rather more than parse a CSV. It checks the column
contract from the schema, which requires `word` and `freq_zipf` and nothing else. It drops rows with
a missing word or frequency, lower-cases and strips the rest, and removes duplicates. Then it sorts
the whole table by the UTF-8 bytes of the word and numbers the rows from one.

That sort is the quiet step everything else depends on. Byte order is stable where a platform's
collation is not, so the lexicon comes out in the same order on a German laptop and an English
continuous integration runner, and in the same order as the R engine, which sorts the same way.
Everything downstream inherits it, including the `id` column, which is the last tie-break in the
matcher.

Three columns are derived on the way in: `length` in characters, `n_syllables` from vowel runs, and
`frequency`, which is whatever column the schema's `dimensions.frequency.column` names, by default
`freq_zipf`.

```python exec="1" source="material-block" result="text" session="matching"
print(lexicon.head(3).to_string(index=False))
```

`build_pool` narrows that lexicon to the candidates a design will consider. A two-element numeric
range is read as an inclusive `[min, max]` band, and anything else is read as a set of allowed
values, compared as strings. Rows missing the filtered column are dropped, and a filter naming a
column the lexicon does not have is skipped without complaint.

```python exec="1" source="material-block" result="text" session="matching"
pool = lexsync.build_pool(lexicon, {"length": [3, 8], "frequency": [3.8, 7.0]})
print(len(pool))
```

The pool step is not optional even though nothing enforces it. `match_stimuli` never looks at a
design's `pool_filters`. It matches over whatever frame you hand it. A script that skips
`build_pool` therefore matches over the entire lexicon and silently ignores the design's bands, and
the selection will look plausible while answering a different question. The package's own test suite
pins this, checking that the README's example calls `build_pool` before matching.

## Supplied item pools

Narrowing a whole lexicon is the right way round when any word of the language will do. It is the
wrong way round when the candidate set is itself a research decision: a list from a previous study,
from a norming session, or one restricted to a semantic category that no lexical filter can express.
Such a list would otherwise have to masquerade as a lexicon, which means inventing a `freq_zipf`
column for it, or else skip matching entirely by going in as `items.source: table`.

`items.source: pool` takes the list as it is.

```yaml
items:
  source: pool
  path: items/pool_en_concrete_nouns.csv
  lexicon: corpora/derived/en.csv
```

The list needs only a `word` column. Length and the syllable estimate are derived from the form, and
`items.lexicon` supplies the rest, frequency above all, by lookup. A word the lexicon does not have
raises a hard error, because the tolerance windows drop rows with missing values silently and the
pool would then be smaller than it appears to be.

One subtlety would quietly invalidate the controls if it went the other way. `n_density` and `old20`
are properties of a word in its *language*, not among the 131 words of a supplied list, so they are
computed against the lexicon's words. A supplied pool with no lexicon falls back to itself, which is
why one is given above. `load_pool` returns both parts of that, `{"pool": ..., "reference": ...}`,
if you call it directly outside a design.

Everything downstream is unchanged: the same conditions, the same `match_on`, the same report, the
same datasheet. What differs is only where the candidates came from, and the datasheet records the
list's checksum so that is answerable later. `config/design_en_supplied_pool.yaml` is a worked
example.

## Relational designs, where the item is a pair

A priming study's theoretical variable is a property of the *pair*, such as distributional
similarity or associative strength, while its nuisance variables are properties of each *member*:
frequency, length, neighbourhood. Such a design needs matching and its own item table at once.

`items.members` promotes an ordinary item table to a pair-keyed one.

```yaml
items:
  source: table
  path: items/priming_pairs_en.csv
  members: [prime, target]          # the two word fields
  lexicon: corpora/derived/en.csv   # where each member's norms are looked up
  anchor_condition: related         # whose row represents the pair during selection
```

Each member's word-level norms are joined from the lexicon and prefixed, giving `prime.frequency`,
`target.length` and so on. The member name leads and the dimension follows, for a reason specific
to R: `prime.frequency` is safe because R's `df$prime` still exact-matches the bare `prime` column,
whereas `frequency.prime` would be a partial-matching hazard. Those prefixed names are then usable
wherever a dimension is: in `pool_filters`, in `match_on`, as a `continuous.predictor` or as a
control.

`pair.lev` is the Levenshtein distance between the two members and `pair.overlap`
is `1 - pair.lev / length of the longer form`, a normalised orthographic similarity. It scores edit
operations, so it is not a count of shared material: `abc` and `cba` share every letter but score
0.33. Orthographic overlap is the standard confound control in a priming design, since a related
pair that also shares letters confounds semantic relatedness with orthographic similarity. The
pipeline adds both automatically when the two members are named `prime` and `target`. Under any
other member names, call `add_pair_overlap` on the item table yourself. A predictor that cannot be
computed from the forms alone, such as cosine similarity or forward associative strength, arrives as
an extra column on the item table and is used like any other.

```yaml
n_per_condition: 8                  # counts PAIRS: 8 pairs, 16 rows, 8 per list over 2 lists
pool_filters:
  target.length: [3, 7]
  target.frequency: [3.0, 6.0]
continuous:
  predictor: target.frequency
  controls: [target.length, pair.overlap]
match_on: [target.length, pair.overlap]
```

Two rules follow from the item being a pair. A filter applies to a pair only if *every* one of its
rows passes, and selection runs over one row per pair, the `anchor_condition`, defaulting to the
byte-first condition, with the result re-expanded afterwards so every condition row of every chosen
pair survives. Neither is an optimisation. A filter on `prime.frequency` applied row by row would
keep a pair's related row and drop its unrelated one, leaving a set the Latin-square counterbalancer
cannot complete. Only a dimension that varies within the pair can split it that way, which the
prime-level and pair-level ones do and the target-level ones do not, since the target is the same
word in both rows.

A member name may not be one of `word`, `id`, `set`, `list`, `trial`, `condition`, `replicate` or
`item`, which the engines read directly, and a design using one is refused. The datasheet gains a
`relational` block recording the members, the pair count, the member lexicon and its checksum, and
the member-level dimensions separately from the relational ones.
`config/design_en_priming_continuous.yaml` is the worked example, and its own comments go further
into why each rule is there.

## The dimensions

Six dimensions are declared in the schema. Three arrive from `load_lexicon`: `length` and
`n_syllables` derived from the form, `frequency` read from the column the schema names. `n_density`
and `old20` are carried by every corpus lexsync distributes, so they too are usually present at load
time, and `add_neighbourhood` computes them only for a lexicon that lacks them. `bigram_freq` is the
one dimension that always needs a separate call.

| Dimension | Unit | Where it comes from |
| --- | --- | --- |
| `length` | letters | Derived at load time from the word. |
| `frequency` | Zipf | The lexicon's `freq_zipf` column ([van Heuven et al., 2014](references.md#van-heuven-2014)). |
| `n_density` | neighbours | `add_neighbourhood`: Coltheart's N, same-length single substitutions ([Coltheart et al., 1977](references.md#coltheart-1977)). |
| `old20` | mean Levenshtein distance | `add_neighbourhood`: the mean distance to the 20 nearest words ([Yarkoni et al., 2008](references.md#yarkoni-2008)). |
| `n_syllables` | syllables | Derived at load time by counting maximal vowel runs. |
| `bigram_freq` | mean bigram probability (type-based, non-positional) | `add_bigram_frequency`, a phonotactic-probability proxy. |

`add_neighbourhood` computes both neighbourhood measures against a reference word list, which
should normally be the full lexicon, since a word's neighbours do not stop
existing because your design excluded them. The pipeline passes the full lexicon for exactly that
reason, and computes these only when the design's `match_on` asks for them, because the calculation
is quadratic in the reference size and easily the slowest step in a run.

`add_bigram_frequency` averages, over a word's adjacent letter bigrams, the corpus probability of
each. It works from integer counts and rounds the result to nine decimal places, which keeps
it identical in the two engines to the last decimal place.

`count_syllables` is honest about being an estimate. It counts maximal runs of Latin vowels, an
orthographic approximation with no pronunciation model behind it.

```python exec="1" source="material-block" result="text" session="matching"
print(
    [lexsync.count_syllables(w) for w in ["cat", "banana", "strength", "idea"]]
)
```

`strength` returning 1 and `idea` returning 2 shows both the method and its limits in one line.

The set of dimensions is not closed. `merge_norms` left-joins any word-keyed norm table, which is
the connector for anything the corpus does not carry: concreteness, age of acquisition, valence, or
the English Lexicon Project's behavioural measures. The norm data are fetched separately, because
their licensing varies, and merged here so the matcher can equate on the new column as if it had
been there all along.

```python
# illustrative: needs a norm table of your own at norms/concreteness_en.csv
lexicon = lexsync.merge_norms(lexicon, "norms/concreteness_en.csv", on="word",
                              columns=["concreteness"])
# then: match_on: [length, frequency, concreteness]
```

The join drops missing keys, takes the first row per key, and is case- and whitespace-insensitive on
both sides. The result is the lexicon itself with columns appended, in its own row and column order,
which is what makes the two engines agree by construction: `pandas.merge` and R's `merge()` disagree
about where the key column lands and about how they disambiguate a name clash. A clash is refused,
because a silent rename leaves the dimension the design matches on under a name nothing looks for.

In a design you do not call this yourself. Name the tables in a `norms:` block and the pipeline joins
them before the pool is built, so a norm column can be filtered on, matched on or spanned like any
other dimension.

```yaml
norms:
  - path: norms/concreteness_en.csv
    on: word                  # optional join key, default 'word'
    columns: [concreteness]   # optional; default every column but the key

pool_filters:
  concreteness: [2.0, 5.0]
match_on: [length, concreteness]
```

lexsync ships no norm data: licences vary, and the citation is yours to honour. What it does do is
record what you joined. Every table appears in the materials datasheet with its checksum and its
per-column coverage, because a norm table can supply the very variable a design manipulates, and a
selection over columns of unstated origin is not reproducible from the record that exists to make it
so. Coverage is recorded for a related reason: a word the table does not cover gets a missing value,
and the tolerance windows then drop it from the pool.

## How matching works

`match_stimuli` runs in two stages, and understanding the split explains most of its behaviour.

First it standardises. Every matched dimension is z-scored against the whole pool's mean and sample
standard deviation, so a distance in letters and a distance in Zipf units become comparable. A
dimension with zero or undefined spread gets a scale of 1, which keeps the distance finite.

Then it picks an anchor. The first condition in the design is the anchor, and its subpool is sorted
by the first dimension its `define_by` mentions, with a byte-order tie-break, after which the
selection is an even spread across that sorted subpool. Taking the top *n* would pile the anchor
into one corner of its own band. The even spread makes the anchor representative of the condition it
is meant to define.

The anchor's realised mean and standard deviation on each matched dimension then set a tolerance
window, mean ± *k* × SD, where *k* comes from `matching.tolerance_k` in the schema and may be
overridden per dimension by the design. This is the anchored path, so it is what
`standardised_euclidean` and `mahalanobis` do. `joint` and `optimal` score cross-condition pairs
directly and never read `tolerance_k` at all. The defaults are 2.0 for `length`, `n_density` and `old20`,
and 1.0 for `frequency`. Each remaining condition is filtered to its window, and then every anchor
item is assigned its nearest unused candidate by standardised distance.

The assignment is where determinism is bought. Distances are rounded to nine decimal places before
they are compared, which absorbs last-bit floating-point differences between the two engines. Ties
are broken by the word's UTF-8 bytes and then by its lexicon id. Candidates already used are pushed
to infinity, and candidates whose matched dimensions are missing rank last rather than first, which
is what R's `order(na.last = TRUE)` does and what a naive `min()` over NaN would get wrong.

Two guards are worth knowing about because they turn silent corruption into an error. If a condition
has fewer candidates inside its window than the anchor has items, the window is relaxed to the whole
subpool, and `verbose=True` says so. If even the relaxed subpool is too small, or if too few of its
rows are complete on the matched dimensions, `match_stimuli` raises. Without
the second check an exhausted pool would let the tie-break re-pick the same word into several sets.

Both behaviours are policies, and the schema's `matching` block names them.
`on_insufficient_tolerance` governs the window fallback. Its default of `relax` keeps the behaviour
just described, while `error` makes the matcher refuse and say so, which is the honest setting when
the window is itself the criterion, as it is when reproducing a published study's stated windows.
`shortfall` governs what happens when fewer sets than `n_per_condition` can be selected at all, and
it defaults to `error` deliberately: the datasheet and the generated methods paragraph state the
requested n, so a set that silently shrank would leave the record misstating the materials. A
design that can live with fewer sets says so with `shortfall: allow`, and either key may be
overridden under the design's own `matching:` block, exactly as `tolerance_k` may be.

### The four methods

The method is set with `matching.method` in a design, or globally in the schema.

| Method | What it does | Conditions | Cross-engine |
| --- | --- | --- | --- |
| `standardised_euclidean` | Greedy nearest neighbour on z-scored dimensions, anchored on the first condition. The default. | Any number | Byte-identical |
| `joint` | Scores every cross-condition pair and greedily takes the cheapest disjoint ones. | Exactly two | Byte-identical |
| `mahalanobis` | Nearest neighbour under a covariance-aware distance that down-weights correlated dimensions. | Any number | Equivalent, byte-identity not guaranteed |
| `optimal` | Solves the linear-assignment problem globally, minimising total pair distance. | Exactly two | Equivalent, byte-identity not guaranteed |

`joint` differs from the default in what it is allowed to discard. The anchored matcher fixes the
first condition and then finds the best counterpart for each of its items, so a bad anchor item
drags a bad pair into the set. `joint` keeps only items that have a good counterpart, which matters
when the manipulation is confounded with a control, neighbourhood density with word length being the
standard case. Both conditions are first capped to the 1200 rows nearest the other condition's
centroid, which keeps the all-pairs cost matrix tractable, and the cap itself is applied with the
same rounded-distance and byte-rank tie-breaks as everything else.

`mahalanobis` uses the inverse of the pool's correlation matrix in standardised space as its metric,
with a small ridge to survive near-collinear dimensions, so that two dimensions measuring much the
same thing are not counted twice ([Rubin, 1980](references.md#rubin-1980);
[Stuart, 2010](references.md#stuart-2010)). `optimal` minimises the summed pair distance over all
pairings at once, which produces fewer badly matched pairs than taking the locally cheapest pair at
each step ([Gu & Rosenbaum, 1993](references.md#gu-1993)).

Both of these carry the parity caveat. A matrix inverse and an assignment solver are the two places
where the R and Python linear-algebra backends can disagree in their last bits, and an assignment
solver's tie handling differs outright. The engines agree closely, and `mahalanobis` usually agrees
exactly, but neither is guaranteed byte-for-byte. `optimal` in particular tends to select an equally
optimal but different set. Each run's datasheet records which case applies.

Comparing them on the same pool shows how little separates them when the pool is generous:

```python exec="1" source="material-block" result="text" session="matching"
pool = lexsync.build_pool(lexicon, {"length": [4, 8], "frequency": [3.5, 7.0]})
design = {
    "name": "methods", "language": "english", "n_per_condition": 40,
    "conditions": [
        {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
        {"name": "low_frequency", "define_by": {"frequency": [3.5, 4.4]}},
    ],
    "match_on": ["length", "n_density", "old20"],
}

for method in ["standardised_euclidean", "joint", "mahalanobis", "optimal"]:
    stimuli = lexsync.match_stimuli(
        pool, {**design, "matching": {"method": method}}, schema
    )
    report = lexsync.match_report(
        stimuli, ["length", "n_density", "old20"], schema
    )
    print(method, [round(d, 3) for d in report["comparisons"]["cohens_d"]])
```

The two pairwise methods reach exact equality on all three controls here, because a pool of this size
contains, for most anchor words, a low-frequency counterpart with the same length, the same
neighbourhood count and the same OLD20. The default and the covariance-aware method leave a
standardised difference in the second decimal place. None of these differences would matter to a
result. The default remains the default because it is byte-identical across engines and generalises
past two conditions, and that is the trade lexsync makes: an algorithm is adopted as a default only
if it can keep the guarantee.

## Reading the report

`match_report` is what turns a selection into a claim you can defend. It returns a dictionary with
two frames. `descriptives` gives n, mean, SD, minimum, median and maximum per condition per
dimension. `comparisons` contrasts every other condition against the first on each dimension.

```python exec="1" source="material-block" result="text" session="matching"
stimuli = lexsync.match_stimuli(pool, design, schema)
report = lexsync.match_report(
    stimuli, ["length", "frequency", "n_density", "old20"], schema
)
print(report["comparisons"].to_string(index=False))
```

Four numbers per row, each answering something the others cannot.

`cohens_d` is the standardised mean difference, using the pooled standard deviation. `d_ci_low` and
`d_ci_high` bound it with the 90% interval that corresponds exactly to a two one-sided tests
decision at the .05 level ([Lakens, 2017](references.md#lakens-2017)). The interval is reported
alongside the verdict because it keeps the dependence on item count visible: with few items the
interval is wide, so a small point estimate cannot be read as evidence that the true difference is
small ([Sassenhagen & Alday, 2016](references.md#sassenhagen-2016)). Its upper limit is the largest
imbalance still consistent with the stimuli you have.

`tost_p` and `equivalent` come from two one-sided tests against the schema's `equivalence.bound_d`,
0.5 by default, at `equivalence.alpha`. This is the test that matches what a matched design is
claiming. A non-significant *t*-test says the data failed to show a difference, which is not the same
as showing there is none. TOST says the difference is smaller than the bound you declared uninteresting.

`var_ratio` is the condition's variance over the reference's. It is there because everything above
is about means, and two conditions can share a mean while differing in spread, which still confounds
([Armstrong et al., 2012](references.md#armstrong-2012);
[Austin, 2009](references.md#austin-2009)). A ratio near 1 is balanced. A common heuristic treats
anything outside roughly [0.5, 2] as unequal spread. It returns `None` when a variance is undefined.

Two smaller functions round this out. `describe_stimuli` gives the descriptives alone, grouped by any
column you like, `condition` included. `balance_check` reports columns whose value counts are
unequal, which is how the pipeline notices an unbalanced condition and writes it into the run log.

```python exec="1" source="material-block" result="text" session="matching"
print(lexsync.balance_check(stimuli, "condition"))    # empty when balanced
```

## Continuous designs

Splitting a continuous predictor into high and low conditions throws away information, costs power
and can introduce selection artefacts ([Kuperman, 2015](references.md#kuperman-2015);
[Liben-Nowell et al., 2019](references.md#liben-nowell-2019)). A design can replace its
`conditions` with a `continuous` block, and select a set that spans the predictor evenly while
holding the controls near-constant, for analysis by regression or a mixed model.

```python exec="1" source="material-block" result="text" session="matching"
design = {
    "name": "continuous", "language": "english", "n_per_condition": 60,
    "continuous": {
        "predictor": "frequency",
        "controls": ["length", "n_density", "old20"]
    },
    "match_on": ["length", "n_density", "old20"],
    "matching": {
        "tolerance_k": {"length": 1.5, "n_density": 1.5, "old20": 1.5}
    },
}
pool = lexsync.build_pool(lexicon, {"length": [3, 8], "frequency": [3.8, 7.0]})
stimuli = lexsync.select_continuous_stimuli(pool, design, schema)
report = lexsync.match_report_continuous(
    stimuli, "frequency", ["length", "n_density", "old20"], schema
)
print(report["comparisons"].to_string(index=False))
```

The selection is two deterministic passes, with no per-item matching and no random numbers. An even
spread over the predictor across the whole pool sets a tolerance window on each control. The pool is
then filtered to those windows, and a second even spread over the filtered pool is the selection.
Because
both passes reuse the matcher's even-spread primitive, the two engines select byte-identical stimuli
here as well.

`match_report_continuous` returns the same `{descriptives, comparisons}` shape as `match_report`, so
the pipeline and the datasheet stay uniform, but the comparisons describe a predictor. Its realised
span replaces the effect size, and each control's Pearson
correlation with the predictor replaces the equivalence verdict. Those correlations are what you
report: at *k* = 1.5 the three controls sit between −0.195 and 0.100, which is the sense in which
they are held constant. Tightening *k* pushes them nearer zero at the cost of a smaller eligible
pool.

`match_on` must equal `continuous.controls`, the predictor must not appear among the controls, and
there must be at least one control. All three are checked, and a design that breaks one of them
raises.

## Items as a random factor

A stimulus set is a sample from a language, not a fixed property of it, and analysing one set as if
it were fixed over-generalises ([Clark, 1973](references.md#clark-1973);
[Yarkoni, 2022](references.md#yarkoni-2022)). `resample_stimuli` produces several disjoint,
independently matched sets from one pool, so a study can run a different sample per participant
group, or show that an effect survives a change of items.

```python exec="1" source="material-block" result="text" session="matching"
pool = lexsync.build_pool(lexicon, {"length": [4, 8], "frequency": [3.5, 7.0]})
design = {
    "name": "resample", "language": "english", "n_per_condition": 20,
    "conditions": [
        {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
        {"name": "low_frequency", "define_by": {"frequency": [3.5, 4.4]}},
    ],
    "match_on": ["length", "n_density", "old20"],
}
stimuli = lexsync.resample_stimuli(pool, design, schema, n_sets=3)
print(stimuli["word"].nunique(), len(stimuli))
```

Each replicate is fully matched in its own right, drawn from the pool with every earlier replicate's
items removed, and marked with a `replicate` column. No word is reused, which the equal counts above
confirm. In a design file this is `resample: {n_sets: 3}`, and the counterbalancer then treats each
replicate as an independent set and numbers trial order within it. The whole thing stays
deterministic because the matcher is deterministic and the used-item set evolves identically in both
engines.

Expect this to exhaust a small pool. Three sets of 20 per condition need 120 distinct words that all
satisfy their bands, and a pool that comfortably supports one set may raise on the third.

## Pseudowords

Lexical decision needs non-words, and the usual difficulty is that they must be orthographically
plausible without being real. `build_lexdec_stimuli` draws real words by an even spread across the
byte-ordered pool, then generates a length-matched pseudoword for each.

```python exec="1" source="material-block" result="text" session="matching"
pool = lexsync.build_pool(lexicon, {"length": [4, 7], "frequency": [3.5, 6.0]})
stimuli = lexsync.build_lexdec_stimuli(
    pool, n=8, reference_words=lexicon["word"].tolist()
)
print(
    stimuli[["target", "condition", "length", "set"]]
    .head(3).to_string(index=False)
)
```

The presented string is `target`, the conditions are `word` and `pseudoword`, and `set` pairs each
word with its non-word twin. `reference_words` should be the full lexicon: it supplies the bigram
statistics and the list of real forms a pseudoword must avoid, and defaults to the pool when
omitted, which is rarely what you want.

Two methods are available, chosen per design under `items.generation.method`.

`letter_substitution`, the default, changes as few letters as possible subject to three constraints:
every resulting bigram must be attested in the corpus, the form must not be a real word or one
already generated, and the length must be preserved exactly. Single substitutions are searched
first, then pairs as a fallback. Among the legal candidates the most bigram-plausible wins, with a
byte-order tie-break.

`subsyllabic` splits each word into onset, nucleus and coda constituents and swaps whole
constituents for attested alternatives of the same role and length, so the pseudowords keep their
syllabic structure. Codas and nuclei are changed before onsets, which carry the most identifying
orthography. Roughly two thirds of a word's constituents are targeted, each swap preserves length,
and a word with no legal swap falls back to letter substitution, so every word yields a pseudoword.
It is a deterministic orthographic approximation of Wuggy
([Keuleers & Brysbaert, 2010](references.md#keuleers-2010)), trading Wuggy's phonological model for
exact length matching and cross-engine reproducibility.

```python exec="1" source="material-block" session="matching"
subsyllabic = lexsync.build_lexdec_stimuli(
    pool, n=8, reference_words=lexicon["word"].tolist(), method="subsyllabic")
```

Both generators process base words in byte order, so the set of already-used pseudowords evolves
identically in R and Python, and both select byte-identical stimuli. Both are also orthographic
models defined for a–z words: `build_lexdec_stimuli` filters the pool to those, and
`segment_subsyllabic` returns nothing for a word with an accent, a hyphen or a digit, which sends it
down the letter-substitution path. That is why lexical decision is demonstrated on the English
designs and never on the Chinese one.

`generate_pseudowords` and `make_pseudoword` are available directly if you want the forms without the
lexical-decision scaffolding around them.

```python exec="1" source="material-block" result="text" session="matching"
pairs = lexsync.generate_pseudowords(
    ["house", "table"], lexicon["word"].tolist()
)
print(pairs.to_string(index=False))
```
