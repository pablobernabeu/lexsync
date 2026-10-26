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

`load_lexicon` takes the lexicon as given and screens nothing for lexical status. The bundled
English slice loaded here is cut from the screened English lexicon. The screen leaves out the forms
SUBTLEX-US lacks or writes with a capital in more than 90% of their uses, such as proper names and
acronyms. The slice's N and OLD20 count only the forms it keeps. Taboo words and some
abbreviations pass the screen, and a lexicon of your own is loaded as it stands.
[Choosing and screening a lexicon](#choosing-and-screening-a-lexicon) below says what such forms do
to a selection and how to screen them out.

`build_pool` narrows that lexicon to the candidates a design will consider. A two-element numeric
range is read as an inclusive `[min, max]` band, and anything else, `[true, false]` included, is
read as a set of allowed values. A set of numbers is compared with a numeric column as numbers.
Any other set is compared as text, the cells and the values written as the R engine writes them,
so `true` matches TRUE in a logical column and never 1 in a 0/1 column. Rows missing the filtered
column are dropped, and a filter naming a column the lexicon does not have is skipped without
complaint. A design's filters are checked first: `run_pipeline` refuses a `pool_filters` key that
names neither a column of the lexicon, counting any columns its `norms:` tables add, nor a dimension
it derives (`n_density`, `old20` or `bigram_freq`), and `match_stimuli` refuses a `define_by` key
the pool lacks.

```python exec="1" source="material-block" result="text" session="matching"
pool = lexsync.build_pool(lexicon, {"length": [3, 8], "frequency": [3.8, 7.0]})
print(len(pool))
```

The pool step is not optional even though nothing enforces it. `match_stimuli` never looks at a
design's `pool_filters`. It matches over whatever frame you hand it. A script that skips
`build_pool` therefore matches over the entire lexicon and silently ignores the design's bands, and
the selection will look plausible while answering a different question. The package's own test suite
pins this, checking that the README's example calls `build_pool` before matching.

## Choosing and screening a lexicon

The lexica in the repository's `corpora/derived/` hold the most frequent forms wordfreq gives for a
language, and wordfreq lists names, acronyms and internet forms beside words. Such forms enter a
selection unevenly across conditions: when the `en_andrews_repro` demonstration read `en.csv`, they
made up 24 of its 36 low-frequency items and none of its 36 high-frequency ones. N and OLD20 count
them as neighbours too, so that `cat` has 32 neighbours in `en.csv`, among them `caa`, `cbt` and
`cdt`.

`corpora/derived/en_v2.csv` screens the English lexicon against SUBTLEX-US
([Brysbaert & New, 2009](references.md#brysbaert-2009)). It holds the 30,000 forms and frequencies
of `en.csv` and adds four columns. `in_subtlex_us` is 1 when SUBTLEX-US lists the form, and
`lowercase_share` is the share of its SUBTLEX-US uses that begin with a lower-case letter, empty
for a form SUBTLEX-US lacks. `nonstandard` is 1 for a form SUBTLEX-US lacks or whose share is below
0.10, which marks 6,565 forms, mostly names and acronyms, and `reference_member` is 1 for the other
23,435. The file's `n_density` and `old20` count neighbours among those only, so `cat` has 21, and
`n_density_raw` and `old20_raw` keep the values of `en.csv`. To select among the unmarked forms,
filter on the flag.

```yaml
lexicon: corpora/derived/en_v2.csv
pool_filters:
  nonstandard: [0, 0]
```

The threshold is low on purpose. A capital at the start of a sentence pulls ordinary words down, so
even `what`, `how`, `why`, `maybe`, `okay` and `yes` begin with a lower-case letter in under half
their uses. A filter such as `lowercase_share: [0.5, 1]` would drop them all. Even at 0.10 the flag
marks the days of the week, the months other than `march` and `may`, most nationality words, `god`,
`ok` and `tv`. It also marks every form the 2009 corpus lacks, such as `selfie`, `emoji` and
`covid`. A design that needs some of those can leave the flag unfiltered and remove what it does
not want by name. A range filter on `lowercase_share` would also drop every form SUBTLEX-US lacks,
whose share is empty.

`exclude_words` removes words by name. It lists them in the design, or names a UTF-8 file with one
word per line, in which blank lines and lines beginning `#` are skipped.

```yaml
exclude_words: [adams, dubai, espn]
# or, from a file: exclude_words: {path: config/exclude_en.txt}
```

The words are trimmed, lower-cased and put in NFC, as a lexicon's words are. They leave the
candidates of a corpus, pool or generated design after any `norms:` join and before the pool
filters. The neighbourhood reference still counts them, and a generated pseudoword still may not
equal one, because an excluded word is still a word of the language. A design with an item table
refuses the key, since its items are already a selection of your own. The datasheet records the
list as `materials_source.exclusions`, with its checksum, the number of words it lists and the
number of candidates it removed, and the Methods paragraph reports the removal.

`en.csv` keeps its bytes, so a design written for lexsync 0.1 selects what it selected once it sets
`matching.tie_break: bytes` ([How matching works](#how-matching-works)), unless it uses the `optimal`
method, whose selections differ from those of lexsync 0.1 under either rule, or its pool holds
candidates that lack a matched value, which are now left out. The English
demonstrations read `en_v2.csv` with the filter above. Their `exclude_words` file,
`config/exclude_en_demo.txt`, leaves out the taboo words and the forms that pass the screen without
being standard English words, such as abbreviations that subtitles write in lower case (`mph`,
`msg`). Its header states the criteria, and the list was made by reading what the demonstrations
selected. Spanish and Chinese have no screened lexicon, because no source of letter case or known
words with a verified licence exists for them. Read a selection in either language before a study
runs, and leave out what you find with `exclude_words`.

The datasheet credits the lexicon a corpus or generated design read. A lexicon lexsync ships is
credited to wordfreq, and `en_v2.csv` and the English example slice drawn from it to wordfreq
screened against SUBTLEX-US, with the rule. A corpus that `fetch_corpus` put in the cache is
credited by the registry's citation, and any other file by its name and the first twelve digits of
its checksum.

## Supplied item pools

Narrowing a whole lexicon is the right way round when any word of the language will do. It is the
wrong way round when the candidate set is itself a research decision: a list from a previous study,
from a norming session, or one restricted to a semantic category that no lexical filter can express.
Loaded as a lexicon, such a list would need an invented `freq_zipf` column, and, given as
`items.source: table`, it would skip matching.

`items.source: pool` takes the list as it is.

```yaml
items:
  source: pool
  path: items/pool_en_concrete_nouns.csv
  lexicon: corpora/derived/en_v2.csv
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
frequency, length, neighbourhood. A relational design therefore needs matching and its own item
table at once.

`items.members` promotes an ordinary item table to a pair-keyed one.

```yaml
items:
  source: table
  path: items/priming_pairs_en.csv
  members: [prime, target]             # the two word fields
  lexicon: corpora/derived/en_v2.csv   # where each member's norms are looked up
  anchor_condition: related            # whose row represents the pair during selection
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
| `n_syllables` | syllables | Derived at load time by counting maximal vowel runs, and missing outside the Latin script. |
| `bigram_freq` | mean bigram probability (type-based, non-positional) | `add_bigram_frequency`, a phonotactic-probability proxy. |

`add_neighbourhood` computes both neighbourhood measures against a reference word list, which
should normally be the full lexicon, since a word's neighbours do not stop
existing because your design excluded them. The pipeline passes the full lexicon for exactly that
reason. It computes `n_density`, `old20` and `bigram_freq` for a lexicon that lacks them whenever
the design refers to them, whether in `match_on`, a condition's `define_by`, `pool_filters`, a
continuous predictor or control, or `counterbalance.balance_on`. The filters the lexicon can answer
run first and those on a derived dimension after it is computed, so the calculation, quadratic in the
reference size, runs on the smaller pool. A lexicon can name the words that make up the reference
with a `reference_member` column (1 for a member, 0 otherwise). Passing `reference_words` to
`run_pipeline` recomputes N and OLD20, and `bigram_freq` where the lexicon carries it or the design
uses it, against that list instead, overriding the lexicon's columns. The datasheet's `selection.neighbourhood_reference`
then records the list with the columns it was applied to.

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

A vowel counts whatever its accent, since the word is decomposed and its diacritics set aside, so
Polish będę, Turkish kız, Czech dům and Vietnamese một count 2, 1, 1 and 1. The estimate is
defined for Latin orthographies only: a word holding a character outside the Latin script returns
`None`, and its `n_syllables` is NaN. `run_pipeline` refuses a design that refers to `n_syllables`
when such a word passes the other filters the lexicon can answer.
[Reproducibility and parity](reproducibility-and-parity.md) gives the exact letters and code points.

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
    join_on: word             # optional join key, default 'word'
    columns: [concreteness]   # optional; default every column but the key

pool_filters:
  concreteness: [2.0, 5.0]
match_on: [length, concreteness]
```

The join key is written `join_on`, because YAML reads a bare `on` as the boolean true. A bare
`on:` is read as the join key all the same, with a note in the run log, and any other key in an
entry is refused.

lexsync ships no norm data: licences vary, and the citation is yours to honour. What it does do is
record what you joined. Every table appears in the materials datasheet with its checksum and its
per-column coverage, because a norm table can supply the very variable a design manipulates, and a
selection over columns of unstated origin is not reproducible from the record that exists to make it
so. Coverage is recorded for a related reason: a word the table does not cover gets a missing value.
A filter on the column drops it, and the matcher excludes it before selecting whenever the column is a
matched dimension, a continuous predictor or a control. The run log and the datasheet count those
exclusions per condition.

## How matching works

`match_stimuli` runs in two stages, and understanding the split explains most of its behaviour.
Both need at least one dimension in `match_on`. Without one, every candidate lies at distance zero
from every anchor and the tie-break alone would choose the words, so a design with
conditions and no `match_on`, or an empty one, is refused before anything is selected.

First it standardises. Every matched dimension is z-scored against the whole pool's mean and sample
standard deviation, so a distance in letters and a distance in Zipf units become comparable. A
dimension with zero or undefined spread gets a scale of 1, which keeps the distance finite. A
candidate missing any matched dimension has no place in that space, so every condition's subpool is
cut to its complete rows before any method runs. The run log and the datasheet count what each
condition lost, and the `shortfall` policy below applies to what remains.

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
and 1.0 for `frequency`, and any other dimension takes 2. The design's values are merged over the
schema's as R's `modifyList()` merges two lists. A `null` in the schema is ignored, and a `null` in
the design removes the schema's value for that dimension, so either leaves *k* at 2. Each remaining
condition is filtered to its window, and then every anchor item is assigned its nearest unused
candidate by standardised distance.

The assignment is where determinism is bought. Distances are rounded to nine decimal places before
they are compared, which absorbs last-bit floating-point differences between the two engines. Each
anchor item chooses among the candidates not yet used, so no word can be assigned twice. A tie in
distance is broken by the rule that `matching.tie_break` names, and then by the lexicon id.

Exact ties are common, because lengths and neighbourhood counts are whole numbers and frequencies
carry two decimals. When `en_freqcontrast` read `en.csv`, 71 of its 80 anchored picks had another
candidate at exactly the chosen distance, with a median of eight tied candidates, and the tie-break
chose the word. Under `bytes`, the rule of lexsync 0.1, a tie goes to the word whose UTF-8 bytes
sort first, so a condition decided by ties fills with early-alphabet words. In that design, 61% of
the low-frequency words began with a or b, against 13% of their candidates, and in `en_ndensity`'s
dense condition every word did. A word's initial phoneme biases voice-key measures of naming
latency ([Kessler et al., 2002](references.md#kessler-2002)), and the realised-control report cannot
show such a skew, because it measures only the matched dimensions.

Under `hash`, the default, a tie goes to the smaller SHA-256 digest of `lexsync-tie-v1|` followed by
the word. The salt is fixed, so the rule does not depend on the seed, and the digests favour no part
of the alphabet. On `en.csv`, the low-frequency share fell to 12.5% and the dense share to 17.5%,
against 13% and 12% among the candidates, while Cohen's *d* on every matched dimension of every
shipped matched design was unchanged. Under either rule, `standardised_euclidean` and `joint` give
the same selection in the two engines, and `bytes` reproduces the selections of lexsync 0.1. The
even spreads that pick the anchor's items and a continuous design's items keep the byte order under
both rules.

```yaml
matching:
  tie_break: bytes   # hash (the default) or bytes, in a design or in the schema
```

Two guards are worth knowing about because they turn silent corruption into an error. If a condition
has fewer candidates inside its window than the anchor has items, the window is relaxed to the whole
subpool, and `verbose=True` says so. If even the relaxed subpool is too small, `match_stimuli` raises.
Without that check, an exhausted pool would leave an anchor item with no unused candidate to take.

Both behaviours are policies, and the schema's `matching` block names them.
`on_insufficient_tolerance` governs the window fallback. Its default of `relax` keeps the behaviour
just described, while `error` makes the matcher refuse and say so, which is the honest setting when
the window is itself the criterion, as it is when reproducing a published study's stated windows.
`shortfall` governs what happens when fewer sets than `n_per_condition` can be selected at all, and
it defaults to `error` deliberately, because a smaller set changes the design that was planned. A
design that can live with fewer sets says so with `shortfall: allow`. The datasheet then records
the items each condition holds, and the methods paragraph states them beside the request. Either
key may be overridden under the design's own `matching:` block, exactly as `tolerance_k` may be.

Windows are the place to reproduce a published study's stated criteria.
`config/design_es_gender_repro.yaml` sets `tolerance_k` to `0.111...` for `frequency`, the window of
the mean plus or minus SD/9 that [González Alonso et al. (2025)](references.md#gonzalez-alonso-2025)
used, and to 2 for `length`, the mean plus or minus 2 SD.

### The four methods

The method is set with `matching.method` in a design, or globally in the schema.

| Method | What it does | Conditions | Cross-engine |
| --- | --- | --- | --- |
| `standardised_euclidean` | Greedy nearest neighbour on z-scored dimensions, anchored on the first condition. The default. | Any number | Byte-identical |
| `joint` | Scores every cross-condition pair and greedily takes the cheapest disjoint ones. | Exactly two | Byte-identical |
| `mahalanobis` | Nearest neighbour under a covariance-aware distance that down-weights correlated dimensions. | Any number | Equivalent, byte-identity not guaranteed |
| `optimal` | Selects the *n* pairs of least summed distance, solved exactly as an assignment problem. | Exactly two | Equivalent, byte-identity not guaranteed |

`joint` differs from the default in what it is allowed to discard. The anchored matcher fixes the
first condition and then finds the best counterpart for each of its items, so a bad anchor item
drags a bad pair into the set. `joint` keeps only items that have a good counterpart, which matters
when the manipulation is confounded with a control, neighbourhood density with word length being the
standard case. Both conditions are first capped to the 1200 rows nearest the other condition's
centroid, which keeps the all-pairs cost matrix tractable, and the cap itself is applied to rounded
distances. Pairs of equal cost, and rows tied at the cap, are ordered by the same `tie_break` rule
as the anchored picks.

`mahalanobis` uses the inverse of the pool's correlation matrix in standardised space as its metric,
with a small ridge to survive near-collinear dimensions, so that two dimensions measuring much the
same thing are not counted twice ([Rubin, 1980](references.md#rubin-1980);
[Stuart, 2010](references.md#stuart-2010)). The correlations come from the pool's rows that are
complete on every matched dimension, and with *k* matched dimensions the pool needs at least *k* + 2
such rows. `optimal` selects the *n* disjoint pairs whose summed distance is smallest. Choosing *n*
pairs from two pools is the *k*-cardinality assignment problem, and lexsync solves it exactly by
padding the cost matrix with dummy rows and columns until every optimal assignment uses exactly *n*
real pairs ([Volgenant, 2004](references.md#volgenant-2004)). Greedy `joint` matching can spend a
hard item's only good counterpart on an item that had alternatives, and `optimal` cannot, although
on the pools tested `joint` came within a few per cent of the optimum. When the conditions overlap,
a word cannot be paired with itself or used twice. A pair lost that way is replaced by solving again
over the unused words, and the selection is then no longer guaranteed to have the least summed
distance. Gu and Rosenbaum ([1993](references.md#gu-1993)) compared optimal and greedy pair matching
of every treated unit, a related problem, and found optimal matching no better at balancing the
covariates.

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

## Reading the realised control

`match_report` is what turns a selection into a claim you can defend. It returns a dictionary with
two frames. `descriptives` gives n, mean, SD, minimum, median and maximum per condition per
dimension. `comparisons` contrasts every pair of conditions on each dimension. The rows against the
first condition, the anchor, come first, and every further pair follows in condition order, with
the earlier condition of the pair named in `reference`. A 2 x 2 design such as `en_andrews_repro`
therefore shows the contrasts within each factor, such as its two low-frequency cells, beside the
three against its first cell.

```python exec="1" source="material-block" result="text" session="matching"
stimuli = lexsync.match_stimuli(pool, design, schema)
report = lexsync.match_report(
    stimuli, ["length", "frequency", "n_density", "old20"], schema
)
print(report["comparisons"].to_string(index=False))
```

Each row carries the statistics below, each answering something the others cannot.

`cohens_d` is the standardised mean difference, using the pooled standard deviation. It is the mean
of the condition named in `reference` minus the mean of the condition in that row, so a positive
*d* means the reference scores higher. A condition with a single item has no spread, so *d* and its
interval are then left empty. `d_ci_low` and `d_ci_high` bound it with the 90%
interval that goes with a two one-sided tests decision at the .05 level
([Lakens, 2017](references.md#lakens-2017)), built from the large-sample standard error of *d*
([Hedges & Olkin, 1985](references.md#hedges-1985)). That standard error grows with *d*, so the
interval on the manipulated dimension is much wider than on a well-matched control. The interval is
reported alongside the verdict because it keeps the dependence on item count visible: with few items
it is wide, whatever the point estimate. Its upper limit is the largest imbalance still consistent
with the stimuli you have. TOST tests the raw mean difference, so the interval is slightly wider than
the one its decision implies, and for a limit close to the bound, `tost_p` is the verdict.

`tost_p` and `equivalent` come from two one-sided tests against the schema's `equivalence.bound_d`,
0.5 by default, at `equivalence.alpha`. A non-significant *t*-test says the data failed to show a
difference, which is not the same as showing there is none. TOST says the difference is smaller than
the bound you declared uninteresting ([Lakens, 2017](references.md#lakens-2017)). The bound of 0.5 is
a convention and not a default of Lakens's, who asks for the bound to be justified for the study at
hand, so set one you can defend. The verdict also depends on the number of items: at a bound of 0.5
and an alpha of .05, no dimension that varies can pass with fewer than 23 items per condition, even
when the conditions are identical.

Both statistics treat the selected items as a sample from a larger population, which they are not.
[Sassenhagen and Alday (2016)](references.md#sassenhagen-2016) point out that a test on stimuli
concerns a closed population (the items you chose). They recommend describing the stimuli, which the
descriptives do, and entering potential confounds in the analysis as covariates.

The datasheet's Methods paragraph follows that advice. It describes the realised control first: the
largest difference on a matched dimension, in that dimension's unit, with *d* and its interval. The
interval is labelled by the schema's alpha, 90% at .05 and 99% at .005. Raw differences in different
units cannot be ranked against each other, so the largest is the one with the largest |*d*|. The two
one-sided tests come second, as a check, with the number of matched comparisons they supported. When
every condition holds fewer items than the bound needs, the paragraph says that no dimension that
varies can pass, however well matched. It then names, largest first, up to five comparisons of a
dimension the design did not control whose |*d*| exceeds the bound, such as the syllable difference
in `en_ndensity`, or says that none does. The suggested model enters the matched dimensions as
centred covariates.

`var_ratio` is the condition's variance over the reference's. It is there because everything above
is about means, and two conditions can share a mean while differing in spread, which still confounds
([Armstrong et al., 2012](references.md#armstrong-2012);
[Austin, 2009](references.md#austin-2009)). A ratio near 1 is balanced. A common heuristic treats
anything outside roughly [0.5, 2] as unequal spread. It returns `None` when a variance is undefined.

`mean_diff` is the same contrast in the dimension's own unit: the reference mean minus the
condition mean, in letters, Zipf units, neighbours or syllables, to three places. It is defined
whenever each condition has an item, so it remains when *d* is left empty.

`role` says what the design did with the dimension in that pair. A dimension is `manipulated` when
the two conditions' `define_by` windows on it differ, `controlled` when the design matches on it,
and `uncontrolled` otherwise. The role belongs to the pair: in `en_andrews_repro`, frequency is
manipulated between a high- and a low-frequency cell and uncontrolled between the two
high-frequency cells, which share the window [5, 7]. `run_pipeline` derives the roles from the
design and passes them to `match_report` as `roles`, a function of the row's condition, reference
and dimension. Called without it, as above, `match_report` leaves `role` empty.

The pipeline reports every dimension lexsync knows for the items, whether or not the design matches
on it. Length, frequency, N, OLD20, syllables and bigram frequency come first, then the matched
dimensions, every `define_by` dimension and every joined norm column, so a norm that defines the
conditions appears as the manipulated dimension it is. Bigram frequency is computed for the report when the stimuli
lack it, which leaves the stimuli file and the selection as they were. A dimension with no numeric
value among the items, such as `n_syllables` for Chinese words, is left out. The uncontrolled rows
are where a confound shows. In `en_ndensity`, the dense words have fewer estimated syllables than
the sparse ones (*d* = -0.53, 90% CI [-0.79, -0.26]), which a report of the matched dimensions
alone could not reveal.

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
`conditions` with a `continuous` block, and select a set that spreads over the predictor's ranks
while windows trim the controls' tails, for analysis by regression or a mixed model.

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
spread over the predictor's ranks across the whole pool sets a tolerance window on each control. The
pool is then filtered to those windows, and a second even spread over the ranks of the filtered pool
is the selection. Because
both passes reuse the matcher's even-spread primitive, the two engines select byte-identical stimuli
here as well.

Because the spread is over ranks and not values, the selection follows the pool's distribution of
the predictor. In the `en_freqcontinuous` demonstration its quantiles lie within 0.06 of the pool's,
and 95% of the items fall in the lower half of the frequency range, since frequent words are rare in
any lexicon. The windows trim the controls' tails without holding the controls constant.

`match_report_continuous` returns the same `{descriptives, comparisons}` shape as `match_report`, so
the pipeline and the datasheet stay uniform, but the comparisons describe a predictor. Its realised
span replaces the effect size, and each control's Pearson
correlation with the predictor replaces the equivalence verdict. Those correlations are what you
report: at *k* = 1.5 the three controls sit between −0.248 and 0.069, and a control that stays
correlated belongs in the model as a covariate. Tightening *k* does not reliably lower the
correlations. In `en_freqcontinuous`, *k* = 1.0 gives *r* = 0.070 between frequency and
`n_density`, against 0.301 at *k* = 1.5, but on the unscreened `en.csv` it gave 0.213 against
−0.049. At *k* = 0.25 only 30 items fall within the windows, fewer than the 80 the design needs, so
the selector relaxes them to the whole pool.

Each row also gives the dimension's realised SD as `sd`. For the predictor, `sd_ratio` sets it
against the SD of as many values spaced evenly over the same range. That SD is
`(max - min) * sqrt(n * (n + 1) / 12) / (n - 1)`, which approaches `(max - min) / sqrt(12)` as *n*
grows, so an even spread has a ratio of 1 at any size. A ratio below 1 means the items bunch
together more than an even spread would: `en_freqcontinuous` has 0.59, an SD of 0.53 against 0.90.
A ratio above 1 means they gather towards the ends of the range. For a control, `sd_ratio` sets the
realised SD against the SD of the pool the selector drew from, and `window_low` and `window_high`
give the window its first pass set. In `en_freqcontinuous`, length keeps 0.76 of the pool's SD, so
the window trims the tails of a control and leaves much of its spread. The windows come from the
audit `select_continuous_stimuli` attaches to its result, which `match_report_continuous` reads
unless it is given one as `audit`. A window that held too few items and was widened to the whole
pool is recorded in the datasheet's `window_relaxations`. The datasheet's Methods paragraph sets the
predictor's SD against that of an even spread, gives each control's window and its realised SD
against the pool's, and says when the windows were widened.

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
every resulting bigram must be attested in the corpus, the form must not be in the reference list or
already generated, and the length must be preserved exactly. Single substitutions are searched
first, then pairs as a fallback. Among the legal candidates the most bigram-typical wins, with a
byte-order tie-break.

`subsyllabic` splits each word into onset, nucleus and coda constituents and swaps whole
constituents for attested alternatives of the same role and length, so the pseudowords keep their
syllabic structure. Codas and nuclei are changed before onsets, which carry the most identifying
orthography. Up to ceil(2*k*/3) of a word's *k* constituents are replaced, each swap preserves
length, and a word with no legal swap falls back to letter substitution, so every word yields a
pseudoword. It is a deterministic orthographic approximation of Wuggy
([Keuleers & Brysbaert, 2010](references.md#keuleers-2010)), and it differs from Wuggy in more than
the phonological model. Wuggy matches the template's transition frequencies, matches letter length
by default and has orthographic modules for several languages, and by default it keeps two thirds of
the segments where lexsync replaces up to two thirds. What lexsync gains is cross-engine
reproducibility.

```python exec="1" source="material-block" session="matching"
subsyllabic = lexsync.build_lexdec_stimuli(
    pool, n=8, reference_words=lexicon["word"].tolist(), method="subsyllabic")
```

In both methods, the scoring picks the most bigram-typical candidate and does not match the base word,
so the pseudowords come out more bigram-typical than their words. The difference in mean bigram
probability is about *d* = −1.0, words minus pseudowords, in `en_lexdec` and `en_lexdec_wuggy` alike.
Read the generated forms before a study runs.

Both generators process base words in byte order, so the set of already-used pseudowords evolves
identically in R and Python, and both select byte-identical stimuli. Their alphabet is derived from
the reference. It is the set of letters the reference words attest, in UTF-8 byte order, so a
Spanish lexicon lends them `á`, `é`, `í`, `ó`, `ú`, `ü` and `ñ`, which one word in six carries in a
typical Spanish band. `build_lexdec_stimuli` keeps the pool's words written wholly in those
letters, and a generated design's datasheet counts these words in the band as its candidates. A
word with a hyphen, an apostrophe or a digit is left out. `segment_subsyllabic` takes its nuclei
from the vowels of the syllable estimate, whatever their accent, and a word without one, such as a
Russian or Greek word, goes down the letter-substitution path. Chinese is refused, since Unicode
counts its characters as letters but a form made by swapping one character for another is of
unknown validity as a pseudoword. In the Spanish demonstration, `design_es_lexdec.yaml`, 8 of the 60 words and 4 of
the pseudowords hold a letter outside a to z, and the pseudowords are checked against wordfreq's
Spanish word list.

The stimuli give each pseudoword its `base` word and its `edit_distance` from it, the Levenshtein
distance, and give a word its own form and 0. A generated design's report compares the words with
their pseudowords on length, which they share by construction, and on bigram frequency, N and
OLD20, which the generator does not hold. The report marks length as controlled and the other
three as uncontrolled, and it computes those three against the lexicon on a copy of the stimuli.
Since the most bigram-plausible candidate wins, the pseudowords tend to be more bigram-typical than
their words: in `en_lexdec` the difference is *d* = -0.97 (90% CI [-1.29, -0.65]).

A pseudoword is a non-word only relative to the reference words, so a real word too rare for the
lexicon can still come out as one. The bundled English and Spanish lexica stop at Zipf 2.95 and
3.11, and with the English lexicon alone the generators can produce real words such as crier and
pall. `exclude` names further known word forms that no pseudoword may equal. They are trimmed,
lower-cased and put in NFC like the lexicon's words, and they take no part in the bigram
statistics. In a design the list goes under `items.generation.exclude`, and each entry is a file
with one form per line, a CSV file with a `word` column, or a registry corpus already fetched into
the cache:

```yaml
items:
  source: generate
  lexicon: corpora/derived/en_v2.csv
  generation:
    exclude: [corpora/derived/en_known_forms.txt]
```

Each file must be UTF-8 text, and no form in a one-form-per-line file may hold a tab, a comma or a
semicolon. Such a file is a table whose rows would each be kept whole as a form that matches nothing,
so it is refused. The datasheet records each list with its checksum and the number of forms it
holds, and the Methods paragraph names it. In the repository, `python corpora/fetch_corpora.py --known-forms en es` writes
wordfreq's fuller lists to `corpora/derived/` (289,023 English and 334,625 Spanish forms at Zipf 1.0
or above). They are not shipped in the package.

A long list costs the pseudowords some of their form. The generators' only check on form is that
each letter pair occurs somewhere in the lexicon, so with fewer candidates left the most
bigram-typical one can be ill-formed. In the English demonstrations, 13 of the 140 pseudowords are
ill-formed, among them fdes, gngs and ntena. Each lacks a vowel or opens or closes on a letter pair
that opens or closes no screened English word of three letters or more with a vowel. Without the
list, the same designs give 5 such pseudowords. Read the generated forms before a study runs.

`generate_pseudowords` and `make_pseudoword` are available directly if you want the forms without the
lexical-decision scaffolding around them.

```python exec="1" source="material-block" result="text" session="matching"
pairs = lexsync.generate_pseudowords(
    ["house", "table"], lexicon["word"].tolist()
)
print(pairs.to_string(index=False))
```
