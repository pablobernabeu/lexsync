# cran-comments

## Submission

Update of 'lexsync' from 0.1.0 to 0.1.1. It fixes the test ERROR that the CRAN
checks report for 0.1.0 on r-devel-linux-x86_64-debian-gcc,
r-patched-linux-x86_64 and r-devel-linux-x86_64-fedora-clang. It follows 0.1.0
closely for that reason.

## The check problems in 0.1.0

The note on the Debian results attributed the failures to attempts to write to
the read-only user library. No code that the checks run writes outside
`tempdir()`. The two failures and the one warning came from a test that read
from outside the check directory. `tests/testthat/test-templates.R` compared the
installed templates with `../../../templates`, meant to be the repository's
copy. On the Linux check hosts that path is the unpacked source of the CRAN
package 'templates', so the file lists differed, and the warning is the failed
attempt to open `<library>/lexsync/templates/DESCRIPTION`, a file that does not
exist, for reading. The same failure occurs on fedora-clang.

In 0.1.1 every test that compares the package with repository files finds the
repository through one helper, `tests/testthat/helper-repo.R`. It accepts a
directory only if it holds lexsync's own `DESCRIPTION` under `R_workflow/` and
the Python package beside it, and those tests skip on CRAN.

To confirm the cause, I checked 0.1.0 against a library locked against writes,
with a stand-in 'templates' package beside the check directory. The tests gave
CRAN's result exactly, `[ FAIL 2 | WARN 1 | SKIP 23 | PASS 991 ]`. After the
full check every installed file was unchanged, and nothing had been written
under HOME or the R user directories. The same check of 0.1.1, with stand-in
'templates' and 'config' packages and a README beside it, passes with no failure
or warning and again leaves the library unchanged.

## R CMD check results

Local check with `R CMD check --as-cran` on a freshly built tarball, Windows 11,
R 4.6.1, with the stand-in neighbours described above:

    Status: 1 NOTE

The whole of the NOTE is the incoming-feasibility report of the short interval
since 0.1.0, which this fix explains:

    * checking CRAN incoming feasibility ... NOTE
    Maintainer: 'Pablo Bernabeu <pcbernabeu@gmail.com>'

    Days since last update: 2

The URL check, top-level files, examples, tests and vignette rebuilding all
pass.

## Other changes in 0.1.1

- `cohens_d_ci()` now includes the d^2 term in the standard error of d, so the
  interval on a large effect is no longer too narrow.
- EEG condition codes follow the order of the design's conditions, not the
  shuffled trial order.
- `citation("lexsync")` gives the CRAN DOI.
- Suggests asks for testthat 3.1.8, which the corpus tests' mocking of an
  imported function needs.

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

- Local: Windows 11, R 4.6.1, as above.

## Notes for the reviewer

- No compiled code and no external system requirements.
- Output-writing functions require a caller-supplied destination; they do not
  choose a working-directory output path. `fetch_corpus()` uses an opt-in cache
  under `tools::R_user_dir()` for downloaded corpora, a permitted cache location.
  Nothing is written at load time, and no example writes outside `tempdir()`.
  `?lexsync_cache_dir` and `?fetch_corpus` say where that cache lives, that it
  persists between sessions, how large it can grow and that it may be deleted at
  any time.
- Vignette display settings use knitr's scoped `R.options`, so rendering restores
  the caller's R options after each chunk.
- Examples are executable and offline: they read only files bundled in
  `inst/extdata`, located with `system.file()`. The package contains no
  `\dontrun{}`.
- 'lexsync' *generates text* for PsychoPy, OpenSesame and jsPsych but never
  imports them. Those tools are needed only to run a generated experiment, not to
  use the package, so they are not dependencies.
- Full lexical corpora are fetched on demand into `tools::R_user_dir()`, and only
  the small example lexica described above are bundled. No example or CRAN-run
  test calls the fetching functions.
