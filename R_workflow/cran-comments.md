# cran-comments

## Submission

New submission of 'lexsync' (version 0.1.0).

## R CMD check results

Local check with `R CMD check --as-cran` on a freshly built tarball, Windows 11,
R 4.6.1:

    Status: 1 NOTE

The whole of the NOTE is the standard new-submission report from the CRAN
incoming-feasibility check:

    * checking CRAN incoming feasibility ... NOTE
    Maintainer: 'Pablo Bernabeu <pcbernabeu@gmail.com>'

    New submission

Nothing else is reported. The URL check raises no findings, and the top-level
files, DESCRIPTION meta-information, examples, tests and vignette rebuilding all
pass.

## Bundled third-party data

The package bundles three small example lexica, `inst/extdata/en_example.csv`,
`es_example.csv` and `zh_example.csv`. They are derived from the 'wordfreq'
package (Speer, 2022), whose data files are redistributable under Creative
Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0),
<https://creativecommons.org/licenses/by-sa/4.0/>. Those three files are
therefore distributed under CC BY-SA 4.0 and not under the package's MIT
licence. lexsync standardises the columns and computes two orthographic
neighbourhood variables from the word list; the frequencies are wordfreq's own.

The terms, the changes made and the SUBTLEX credit that wordfreq's own
permission passes through are set out in the top-level `LICENSE.note` file,
which ships in the tarball. `DESCRIPTION` carries a `Copyright:` field pointing
at that file, and `inst/CITATION` repeats the obligation for anyone citing the
software. The `License:` field is left as `MIT + file LICENSE`, since MIT is the
code's licence and a compound `+ file` form is not canonical.

Everything else in the package, code and remaining data alike, is MIT.

## Test environments

- Local: Windows 11, R 4.6.1.

## Notes for the reviewer

- No compiled code and no external system requirements.
- The package writes only to paths supplied by the caller, plus an opt-in cache
  under `tools::R_user_dir()` for downloaded corpora. Nothing is written at load
  time, and no example writes anywhere. `?lexsync_cache_dir` and `?fetch_corpus`
  say where that cache lives, that it persists between sessions, how large it can
  grow and that it may be deleted at any time.
- Examples are executable and offline: they read only files bundled in
  `inst/extdata`, located with `system.file()`. The package contains no
  `\dontrun{}`.
- 'lexsync' *generates text* for PsychoPy, OpenSesame and jsPsych but never
  imports them. Those tools are needed only to run a generated experiment, not to
  use the package, so they are not dependencies.
- Full lexical corpora are fetched on demand into `tools::R_user_dir()`, and only
  the small example lexica described above are bundled. No example or CRAN-run
  test calls the fetching functions.
