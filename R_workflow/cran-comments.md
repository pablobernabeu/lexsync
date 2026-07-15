# cran-comments

## Submission

New submission of 'lexsync' (version 0.1.0).

## R CMD check results

Local check with `R CMD check --as-cran` on Windows 11, R 4.6.1:

    0 errors | 0 warnings | 1 note

The NOTE is the standard new-submission note from the CRAN incoming-feasibility
check. It also reports the package URL as 'possibly invalid'; the GitHub
repository will be public before submission, which resolves this.

## Test environments

- Local: Windows 11, R 4.6.1 (no errors, warnings, or unexpected notes).

## Notes for the reviewer

- No compiled code and no external system requirements.
- The package writes only to paths supplied by the caller; examples use
  `tempdir()` and any network access is wrapped in `\dontrun{}`.
- 'lexsync' *generates text* for PsychoPy and OpenSesame but never imports them;
  those tools are needed only to run a generated experiment, not to use the
  package. They are therefore not dependencies.
- Full lexical corpora are fetched on demand into `tools::R_user_dir()`; only
  small example lexica are bundled.
