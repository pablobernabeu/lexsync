# cran-comments

## Submission

This is an update from lexsync 0.1.1, which CRAN published on 2026-09-25, to
0.2.0.

0.2.0 changes results and interfaces, which is why the minor version moves. For
the same design and seed, some selections differ: `matching.tie_break` defaults
to a keyed hash of each word, where ties went to the spelling that sorts first,
and matching leaves out candidates that lack a matched value. The generated
experiments present one counterbalancing version to each participant, and the
PsychoPy and OpenSesame experiments record each response. Some input that 0.1.1
accepted is refused, such as a probable typo in a design key or a trigger code
outside 1 to 255. The package also requires jsonlite 1.8.7 or later, where it
named no minimum. NEWS.md lists each of these changes under 'Upgrading from the
previous release (0.1.1)', in three parts: 'Changed results', 'Changed
interface' and 'Changed output'.

There are three new exports, `validate_design()`, `normalise_lexicon()` and
`design_stem()`. No export is removed.

## R CMD check results

<errors> errors | <warnings> warnings | <notes> notes

<Paste the status line of the local check below and explain every NOTE here.
More than a month has passed since 0.1.1, so the incoming check should report
no 'Days since last update' NOTE.>

## Test environments

* Local: Windows 11, R 4.6.1, on <date>. `R CMD check --as-cran` on the built
  tarball, with stand-in 'templates' and 'config' packages and a README beside
  the check directory, as CRAN's Linux hosts have the sources of other packages
  there.
* GitHub Actions, run <run id> on <date>, at commit <commit> on the main
  branch, the commit this tarball was built from. Each leg ran
  `R CMD check --as-cran --no-manual` beside the same stand-in neighbours,
  without the CRAN incoming checks, which r-lib/actions turns off:
  * macos-latest, R release
  * windows-latest, R release and R-devel
  * ubuntu-latest, R-devel, R release and R oldrel-1
* <Optional: win-builder, R-devel, on <date>, with its status.>

## Notes for the reviewer

* No compiled code and no external system requirements.
* Output-writing functions require a caller-supplied destination. They do not
  choose a working-directory output path. `fetch_corpus()` keeps downloaded
  corpora in a cache under `tools::R_user_dir()` unless it is given a `dest`,
  and nothing else in the package writes there. Nothing is written at load
  time. A download is refused above 200 MB, the directory is created only when
  a download into it starts, each such download first deletes stale partial
  downloads there, fetching a corpus again replaces the earlier copy and
  `lexsync_cache_clear()` removes one corpus or the whole cache.
  `?lexsync_cache_dir`, `?lexsync_cache_clear` and `?fetch_corpus` say where
  the cache lives, that it persists between sessions and how large it can grow.
* Examples are executable and offline. They read only files bundled in
  `inst/extdata`, located with `system.file()`, and write only under
  `tempdir()`. The example for `lexsync_cache_clear()` points
  `R_USER_CACHE_DIR` at a new directory under `tempdir()`, inside `local()`,
  and an `on.exit()` restores the variable, so neither the check nor
  `example()` touches a user's own cache. The package contains no
  `\dontrun{}`.
* Vignette display settings use knitr's scoped `R.options`, so rendering
  restores the caller's R options after each chunk.
* 'lexsync' generates text for 'PsychoPy', 'OpenSesame' and 'jsPsych' but never
  imports them. Those tools are needed only to run a generated experiment, so
  they are not dependencies.
* clue is in Suggests for `optimal` matching, which stops with a message when
  clue is absent. shiny, bslib, DT and zip are used only by the tests of the
  repository's Shiny app, which skip when one of them or the app is absent.
  spelling runs `tests/spelling.R`, which skips on CRAN. testthat runs the
  tests, and knitr and rmarkdown build the vignettes.
* The tests that compare the package with files of the repository find the
  repository through one helper, which accepts a directory only if it holds
  lexsync's own sources, and they skip on CRAN.
* No example, test or vignette downloads anything. The tests that reach a
  download in `fetch_corpus()` replace `download.file()` with a local stand-in,
  and those that use the default cache first point `R_USER_CACHE_DIR` at a
  directory under `tempdir()` and restore it afterwards.

## Bundled third-party data

The package bundles three small example lexica, `inst/extdata/en_example.csv`,
`es_example.csv` and `zh_example.csv`. They are derived from the 'wordfreq'
package (Speer, 2022), whose data files are redistributable under Creative
Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0),
<https://creativecommons.org/licenses/by-sa/4.0/>. `en_example.csv` keeps only
forms that pass a screen against SUBTLEX-US (Brysbaert & New, 2009), which is
distributed under the same licence. Those three files are therefore distributed
under CC BY-SA 4.0 and not under the package's MIT licence. The frequencies are
wordfreq's own, and lexsync adds a standard column layout and two orthographic
neighbourhood variables computed from the word list.

`inst/COPYRIGHTS` sets out the terms, the changes made and the credit owed to
the corpora, so that every installation, binary ones included, carries them.
`DESCRIPTION` has a `Copyright:` field pointing at that file, as Writing R
Extensions suggests, and `inst/CITATION` repeats the obligation for anyone
citing the software. The `License:` field stays `MIT + file LICENSE`, since MIT
is the code's licence. Everything else in the package, code and remaining data
alike, is MIT.

## Downstream dependencies

<State the result of
`tools::package_dependencies('lexsync', reverse = TRUE, db = available.packages())`.
If it lists none: There are no reverse dependencies on CRAN.>
