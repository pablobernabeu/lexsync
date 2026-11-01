<!-- Thank you for contributing to lexsync. -->

**What does this change do?**
A short description, and a link to the issue it addresses if there is one.

**Checklist**

R package (`R_workflow/`):

- [ ] `devtools::document("R_workflow")` has been run if the roxygen comments changed.
- [ ] `devtools::test("R_workflow")` passes, and new behaviour has tests.
- [ ] `devtools::check("R_workflow")` is clean.

Python package (`python_workflow/`):

- [ ] `pytest` passes, and new behaviour has tests.
- [ ] `ruff check .` is clean.
- [ ] The docs build (`mkdocs build --strict`).

Both:

- [ ] Behaviour changes are made in both engines, with a cross-engine regression test in each suite, and `python tools/compare_engines.py` reports that the engines agree.
- [ ] Documentation, `CHANGELOG.md` and `R_workflow/NEWS.md` are updated where relevant.
- [ ] No secret (API key, token) appears anywhere in the diff.
