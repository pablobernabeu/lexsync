# The app

Not every design has to be written as code. The repository carries a Streamlit front-end over this
package which drives the whole workflow through a browser tab, from choosing a paradigm to
downloading the stimuli, the realised-control report and the materials datasheet. It is a front-end
and nothing more. Every number it shows comes from the installed `lexsync` package, never from a
re-implementation, and the design it assembles is an ordinary YAML file that you can save,
share and run from a script afterwards.

This page describes the app without running it, since the app needs a live server.

## Launching it

The app is not part of the package. It lives in the repository, under `apps/python_streamlit`,
beside the corpora and the example item tables that it reads, so launch it from a clone. Streamlit
itself is the only extra dependency, and it also comes with the `dev` extra, because the test suite
covers the app. The first of the three commands below installs lexsync from the clone, the second
installs Streamlit and the third starts the app.

```bash
pip install -e python_workflow
pip install "streamlit>=1.49"
streamlit run apps/python_streamlit/lexsync_app.py
```

The app needs Streamlit 1.49 or later, the first release whose tables accept the `width` setting it
passes. Naming the version makes pip upgrade an older Streamlit that is already installed, which a
bare `pip install streamlit` reports as satisfied.

Run that from the root of the clone. The app looks for `corpora/derived/` in the working directory
and then in the two directories above it, and it finds the example item tables under `items/` the
same way. Launched from somewhere else it still opens, warns that it found no bundled corpora and
falls back to whatever lexicon you upload. It opens at <http://localhost:8501>.

## The sidebar

Whatever the paradigm, the same few fields sit in the sidebar. 'Paradigm' chooses between a
factorial word contrast drawn from a corpus, lexical decision with generated pseudowords, priming
and self-paced reading, the last two reading prepared items from a table. 'Design name' and
'Language label' become the slug that every written file is named after, exactly as in a design
file, so `my_design` plus `english` gives `my_design_english_stimuli_py.csv` and its companions.
'Stimulus font' overrides the presentation font, which matters for a non-Latin script, and it
reaches the design only when it differs from the `Courier New` default, leaving the schema in
charge otherwise.

Under those the sidebar prints the version of lexsync that is running, with the reminder that the
app runs the installed package. If that line disagrees with the version you expect, the app is
reading a different install.

## Describing the design

The main panel changes with the paradigm, since a corpus-matched contrast and a prepared item table
need different things.

### A factorial word contrast

'Lexicon' lists the derived corpora the clone holds under `corpora/derived/`, which are English,
English screened against SUBTLEX-US (`en_v2`, described in
[Matching and designs](matching-and-designs.md#choosing-and-screening-a-lexicon)), Spanish, a
Spanish lexicon carrying grammatical gender, and Mandarin Chinese, and the first rows of
whichever one you pick are shown beside the selector so you can see what you are working with. The
last entry in the list uploads a lexicon of your own instead, which needs at least a `word` and a
`freq_zipf` column. Two sliders then narrow the lexicon
to the candidate pool the design will consider at all, one for length in letters or characters and
one for frequency in Zipf. They are the design's `pool_filters`, and they are a step that matters,
because matching never re-reads them.

The app opens on `en_v2`, the lexicon the shipped English designs use. A lexicon with a
`nonstandard` column, such as `en_v2`, also brings a 'Screened forms only' checkbox, ticked from
the start. It adds `nonstandard: [0, 0]` to the pool filters and so keeps only the forms the screen
leaves unmarked. Clearing it lets the marked forms, such as names and acronyms, back into the pool.

The conditions are an editable table that rows can be added to and removed from. Each row names a
condition and carves it out of the pool, either by a numeric window through the `dimension`,
`lower` and `upper` columns or by a set of comma-separated values through `categories`, which is
what a categorical column such as the gender of the Spanish lexicon needs. The optional
`dimension2`, `lower2` and `upper2` columns add a second factor to the same row, so one row can
define a full cell of a 2 × 2. Three presets fill the table in one click, a high versus low
frequency contrast, a dense versus sparse neighbourhood contrast and a 2 × 2 of frequency by
neighbourhood. A preset also sets the matched dimensions and the matching method that suit it, so
the neighbourhood contrast arrives matched on length and frequency by the `joint` method and the
2 × 2 arrives matched on length alone. Every control stays editable afterwards, so a preset is
only a starting point.

Below the table sit the choices that govern the match itself. 'Items per condition' sets how many
stimuli each condition should hold. 'Match on' picks the dimensions to equate across conditions,
from length, frequency, neighbourhood N, OLD20, syllable count and bigram frequency. A warning
appears beneath it when it names a dimension whose windows differ between conditions, because
matching on a dimension the conditions manipulate works against the contrast they define.
A window that every condition shares only narrows the pool and draws no warning. With nothing
chosen, the app says so and keeps 'Run design' disabled. 'Matching method' offers the four the
engine implements, `standardised_euclidean`, `joint`, `mahalanobis` and `optimal`, and its help
says that the last two agree only closely between the engines. 'Resampled disjoint sets' draws
several matched sets that share no item, which is what lets items be treated as a random factor,
and zero switches it off. 'Counterbalancing lists' sets how many lists the items are rotated across.

The advanced panel underneath holds one tolerance window per matched dimension, the half-width in
standard deviations of the band a candidate must fall inside. It is collapsed by default because
the schema already carries a sensible default for every dimension, and a zero there leaves that
default alone, where you might expect it to pin the window to nothing. Reproducing the exact
window of a published study is the usual reason to touch the panel at all, and the panel itself
gives the worked example that [Matching and designs](matching-and-designs.md#how-matching-works) discusses, a
frequency k of 0.1111111111111111 for a band of the mean plus or minus a ninth of a standard
deviation.

### Lexical decision

A lexical-decision design takes the same lexicon and pool filters and then asks only for the number
of items per condition, words and pseudowords being equal in number, and for the generator.
`letter_substitution`, the engine default, changes as few single letters as it can while keeping
every bigram attested. `subsyllabic` swaps whole onset, nucleus and coda constituents in the manner
of Wuggy ([Keuleers & Brysbaert, 2010](references.md#keuleers-2010)). Both are deterministic, so the pseudowords are the same ones
the package would generate from a script.

### Priming and self-paced reading

These two paradigms read prepared items instead of selecting any, so no corpus and no matching
are involved. The app offers the bundled example table for the paradigm,
`items/priming_pairs_en.csv` or `items/spr_sentences_en.csv`, and shows its first rows. Clearing
that checkbox uploads a table of your own instead. A priming table needs `item`, `condition`,
`prime` and `target`, and a self-paced reading table needs `item`, `condition`, `question` and
`sentence`, with its regions split by `|`, and may add `critical_region` to give the number of the
region that carries the condition marker. Either way
the design needs only the number of counterbalancing lists.

## Running it

'Run design' assembles the design and lays out a temporary folder the way the download will be laid
out. The design goes in under the name the 'Reproducible code' tab gives it, with the schema that
ships inside the package at `config/schema.yaml` and the lexicon or item table at the path the
design names. The app then runs the exported command line there as a separate process,
`python -m lexsync run "<name>.yaml" --schema config/schema.yaml --outdir output`. The run
therefore reads only relative paths, and its datasheet checksums the files the bundle holds. A
separate process leaves the working directory of the app alone, which every browser session
shares. The button stays disabled while a factorial design has nothing to
match on. Three conditions are checked first, that a lexicon has been chosen
or uploaded where the paradigm needs one, that a factorial design defines at least two conditions,
and that an item-table paradigm has a table, and anything the pipeline itself refuses comes back as
the error the pipeline raised, in its own words. A successful run reports how many rows were
selected and opens the results.

## Reading the results

The results arrive as six tabs, which between them cover what was selected, whether it is any good,
what it will present and how to reproduce it.

'Stimuli' is the selected set as a table, the same one the run wrote to disk.

'Realised control' is the part that decides whether the set is usable. It covers every pair of
conditions on every dimension the report includes. Each row gives the dimension's role
(manipulated, controlled or uncontrolled), the raw difference, Cohen's *d* with its confidence
interval, the variance ratio and the verdict of the two one-sided tests procedure. The interval
matches the tests at the schema's alpha, covering 100(1 - 2 alpha) per cent, and its heading takes
that level from the run's datasheet, so it reads 90% at the default alpha of .05. The tab then
draws the absolute standardised mean difference per dimension and pair as a bar chart. Manipulated
dimensions stand high and matched dimensions sit near zero, so the chart shows immediately whether
the matching worked. An uncontrolled dimension that stands high is a difference the design did not
hold. The per-condition descriptive statistics follow underneath. A design drawn from an item table
produces no corpus-matching report, and the tab says as much where an empty table would otherwise
sit.

'Datasheet' renders the materials datasheet for the run, carrying the provenance of the corpus, the
checksums, the realised control and the pre-registration skeleton.

'Experiment scripts' offers one download per presentation target, each compiled from the same
trial description. The PsychoPy download is a zip archive holding the script and the conditions
file it loads from its own folder. The OpenSesame download is a zip archive holding the `.osexp`,
one per counterbalancing version when the design has several, with the loop and text tables each
one reads. Unzip either and run the experiment from the folder it makes. The jsPsych page carries
its trials and runs in a browser as it stands.

'Reproducible code' is what stops a session in the app from being a dead end. It shows the design
configuration as YAML, with repository-relative paths such as `corpora/derived/en.csv`, the same
paths the run read, followed by the one-line Python, R and command-line calls
that reproduce the same operation. Saving the YAML under the name the panel gives it and running
any of those three lines repeats the run outside the app. The command lines quote the design file's
name, and their quoting holds in bash, `cmd.exe` and PowerShell. The sentence under them is taken
from the datasheet's cross-engine record. Under the deterministic methods it says that the two
engines select byte-identical stimuli and trial order, and under `mahalanobis` and `optimal` that
they select equivalent but not byte-identical stimuli. Where the design names a file you
uploaded, which the repository does not hold, the panel says so and points at the bundle that
carries it.

'Download' archives the folder the run ran in, under the design's name. It holds the design, the
schema at `config/schema.yaml`, the lexicon or item table at the path the design names, uploads
included, and every output under `output/`. The datasheet inside records the checksum of the design
file beside it and no path outside the folder. Running the exported Python call, or either
`lexsync run` command line, in the unzipped folder repeats the run. It rewrites every output with
the same bytes, apart from the run logs, which record when they were written. The R lines write the
R engine's files beside them.

## What you leave with

A session in the app ends with the same artefacts a scripted run produces, which is why it was
built as a front-end over the package and not as a tool of its own. The design YAML is portable
across both engines, so a set assembled here can be reproduced by a collaborator working in R,
byte for byte
under the deterministic matching methods. [Reproducibility and
parity](reproducibility-and-parity.md) covers what that guarantee promises and where it stops, and
[Matching and designs](matching-and-designs.md) reads the realised-control report column by column.
