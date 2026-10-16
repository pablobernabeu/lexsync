# Export a browser-runnable jsPsych experiment

The rendered events and the trial data are embedded in one HTML file, so
anyone can reproduce the procedure online from the same materials. The
jsPsych library and stylesheet are loaded from a CDN, so the machine
running the file needs an internet connection; the trial data are
embedded and the responses are saved locally, so no server is required
either to run it or to collect them. Each of the three files carries its
SHA-384 as Subresource Integrity, so a browser refuses a copy that
differs from the published release. Stimuli are drawn
`presentation.text_height_px` pixels high, 48 by default. Onset triggers
are recorded in each trial's data (a browser cannot drive a parallel
port). A stimulus that collects its response is one trial, recorded as
`target`: it accepts the keys from its onset, shows the stimulus for its
duration and stays open for the timeout after it, a key ends it, and
`rt` runs from the onset.

## Usage

``` r
export_jspsych(stimuli, design, schema, outdir, base = NULL)
```

## Arguments

- stimuli:

  Stimuli with trigger columns (see
  [`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)).

- design:

  A parsed design configuration.

- schema:

  The parsed global schema (trigger and presentation settings).

- outdir:

  Output directory.

- base:

  Optional file-name stem. By default the design's
  [`design_stem()`](https://pablobernabeu.github.io/lexsync/r/reference/design_stem.md).

## Value

The path to the generated `.html`, invisibly.

## Details

The page embeds every presentation version of the design, one per
(replicate, list) pair, and runs one, named in its address:
`?version=K`, `?list=K` when there are no replicates, or
`?participant=N`, whose version is `((N - 1) mod V) + 1`. A page with
more than one version, opened with none of these, shows a screen naming
them and runs nothing. With `counterbalance.orders: m` the page presents
the version in order `(((N - 1) div V) mod m) + 1`, or in order 1
without a participant number, and every data row carries the order. Its
welcome screen shows the version's instructions, the design's
`instructions` or lexsync's for its task, and waits for the space bar.
The data rows carry the participant, the version, the list and the
replicate, and the data file is named after the participant and the
version. The page names the keys as the browser does, `arrowleft` for
`left`, in its events and in each trial's `answer`, so a recorded
response can be compared with the answer as it stands.
