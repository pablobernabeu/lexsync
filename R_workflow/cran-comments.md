# cran-comments

## Submission

New submission of 'lexsync' (version 0.1.0).

## R CMD check results

Local check with `R CMD check --as-cran` on a freshly built tarball, Windows 11,
R 4.6.1:

    0 errors | 0 warnings | 1 note

The NOTE is the standard new-submission note from the CRAN incoming-feasibility
check. Within it, the URL check reports links that resolve only once the current
development branch is merged and the documentation site is rebuilt from it: the
contributing guide and code of conduct under `.github/`, the Python package's
references page, and the licence page. Each was verified to build and resolve
from the branch, and all will be live before submission.

## Test environments

- Local: Windows 11, R 4.6.1.

## Notes for the reviewer

- No compiled code and no external system requirements.
- The package writes only to paths supplied by the caller, plus an opt-in cache
  under `tools::R_user_dir()` for downloaded corpora. Nothing is written at load
  time, and no example writes anywhere.
- Examples are executable and offline: they read only files bundled in
  `inst/extdata`, located with `system.file()`. The package contains no
  `\dontrun{}`.
- 'lexsync' *generates text* for PsychoPy, OpenSesame and jsPsych but never
  imports them. Those tools are needed only to run a generated experiment, not to
  use the package, so they are not dependencies.
- Full lexical corpora are fetched on demand into `tools::R_user_dir()`; only
  small example lexica are bundled. No example or CRAN-run test calls the
  fetching functions.
