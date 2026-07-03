# Submission checklist (lexsync + the accompanying manuscript)

This file collects everything needed to publish 'lexsync' and submit the
accompanying manuscript. **No venue has been chosen yet, and the manuscript has
not been submitted.** *Behavior Research Methods* (BRM) is the leading candidate,
so the policy-specific steps below follow its requirements as a worked example;
adapt them if you choose a different journal. It is guidance, not an automated
step; some items require your account, your identity or a network service and
cannot be done from the build machine.

## Recommended sequence

If you submit to BRM (the candidate venue): it is a Psychonomic Society journal
that follows the TOP / Open Science Level 2 guidelines (materials and code must be
in a trusted repository, with an Open Practices Statement just before the
References) and uses masked (double-blind) review. That shapes the order:

1. **Public GitHub repository.** Create `github.com/<you>/lexsync`, push this
   repo, and update the URL placeholders (see below). This resolves the CRAN
   'possibly invalid URL' NOTE and lets reviewers read the code.
2. **Archive a release on Zenodo (or OSF) to mint a DOI.** Enable the
   GitHub–Zenodo integration and cut a `v0.1.0` release; `.zenodo.json` supplies
   the metadata. The DOI is the citable, FAIR artefact BRM expects, and it is
   what you cite in the manuscript and `CITATION.cff`.
3. **For review, use an anonymised link.** Because review is masked, do **not**
   reveal your name to reviewers: submit a blinded manuscript + separate title
   page, and give reviewers an anonymised OSF view-only link (or Zenodo with
   author masked) rather than the public GitHub repo. Reveal the repo on
   acceptance.
4. **Hold the CRAN and PyPI releases until acceptance (or near it).** Review may
   request an API change or even a rename; PyPI versions are immutable and CRAN
   updates require resubmission, so do not burn the name/version on something
   review might change. Run the pre-submission checks now (below) so you *know*
   it will pass when you do submit.

You do **not** need lexsync on CRAN/PyPI to submit to BRM — a public repo plus a
DOI'd archive satisfies the availability requirement.

## Before anything is public: update placeholders

- `R_workflow/DESCRIPTION`, `python_workflow/pyproject.toml`, `CITATION.cff`,
  `.zenodo.json`, `README.md`: real repository URL and ORCID.
- Confirm **authorship**. The metadata currently lists a single author for a
  general-purpose tool; decide the author/contributor list and the manuscript
  byline (one of the twelve reproduced designs is from a seven-author study,
  González Alonso et al., 2025, so weigh any contribution from that work).

## CRAN pre-submission checklist (R package, `R_workflow/`)

- [x] `R CMD check --as-cran` passes locally (Windows, R 4.5.1): 0 errors, 0
      warnings, 1 (new-submission) NOTE.
- [x] testthat suite passes; HTML vignette builds; roxygen docs complete.
- [ ] Run **win-builder** R-release and R-devel (`devtools::check_win_release()`,
      `check_win_devel()`), and the CI matrix (Ubuntu/macOS/Windows, R devel) —
      `.github/workflows/R-CMD-check.yaml`.
- [ ] Make the GitHub URL valid (repo public) so the URL NOTE clears.
- [ ] `cran-comments.md` is filled in (see `R_workflow/cran-comments.md`).
- [ ] Consider a spelling WORDLIST for 'PsychoPy', 'OpenSesame' and British
      spellings if the spelling check NOTEs.
- [ ] Submit via <https://cran.r-project.org/submit.html> from the maintainer
      address (`pcbernabeu@gmail.com`) and confirm the auto-email. Expect a
      manual review of the new submission.

## PyPI pre-submission checklist (Python package, `python_workflow/`)

- [x] Name `lexsync` is available on PyPI (checked: 404).
- [x] `python -m build` produces a wheel and sdist; `twine check` passes both;
      metadata is PEP 639 (`License-Expression: MIT`).
- [x] `requires-python = ">=3.10"` (narrowed from 3.9; only 3.13 was tested
      locally — the CI matrix tests 3.10–3.13 on three OSes).
- [ ] Upload to **TestPyPI** first (`twine upload --repository testpypi dist/*`)
      and `pip install` from there into a clean venv.
- [ ] Create a PyPI account + API token; `twine upload dist/*`.

## Manuscript (`manuscript/`)

- [ ] Add the Open Practices Statement (repository/DOI) before the References.
- [ ] Replace author/affiliation placeholders; prepare a blinded version + title
      page for masked review.
- [ ] `quarto render manuscript/manuscript.qmd` once more after URLs are final.

> Verify the current BRM author instructions before submitting — the
> masked-review and Open-Practices details above are the established policy but
> journals update their pages.
