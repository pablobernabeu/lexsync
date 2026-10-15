"""Cross-file agreement of the packaging and citation metadata.

The five metadata files (R DESCRIPTION, pyproject.toml, codemeta.json,
CITATION.cff, .zenodo.json) are maintained by hand, so nothing but a test
stops them drifting apart. These checks pin the facts that harvesters and
the README rely on: one version, one author with one ORCID, the DOIs that
name the repository and each package, one licence, and descriptions that
name every shipped generation target.
"""
import json
import re
from datetime import date

import pytest
import yaml
from helper_repo import REPO

# Every file read here sits at the repository root or in one of the two packages'
# directories there, so the whole module skips away from the repository.
pytestmark = pytest.mark.skipif(REPO is None, reason="the repository's metadata files are not in this tree")

ORCID = "0000-0003-1083-2460"

# The DOI CRAN assigned to the R package on publication, which the R package's
# citation gives, and the package page's address in the one form CRAN asks
# links to use.
CRAN_DOI = "10.32614/CRAN.package.lexsync"
CRAN_URL = "https://CRAN.R-project.org/package=lexsync"

# The Python package's page on PyPI, which assigns no DOI.
PYPI_URL = "https://pypi.org/project/lexsync/"

# Zenodo's concept DOI, which resolves to the latest archived GitHub release and
# so covers both packages. The Python package's citation gives it, and so do
# CITATION.cff and codemeta.json, which describe the whole repository.
ZENODO_DOI = "10.5281/zenodo.22906962"
ZENODO_FILES = ("CITATION.cff", "codemeta.json", "README.md", "CHANGELOG.md",
                "R_workflow/vignettes/about.Rmd", "python_workflow/README.md",
                "python_workflow/docs/index.md", "python_workflow/docs/about.md")

# The hand-maintained files that cite the DOI, and so must all carry it.
DOI_FILES = ("CITATION.cff", "codemeta.json", "README.md",
             "R_workflow/README.md", "R_workflow/inst/CITATION",
             "R_workflow/vignettes/about.Rmd", "R_workflow/_pkgdown.yml",
             "python_workflow/docs/about.md")


def _pyproject_text():
    return (REPO / "python_workflow" / "pyproject.toml").read_text(encoding="utf-8")


def _description_text():
    return (REPO / "R_workflow" / "DESCRIPTION").read_text(encoding="utf-8")


def _codemeta():
    return json.loads((REPO / "codemeta.json").read_text(encoding="utf-8"))


def _cff():
    return yaml.safe_load((REPO / "CITATION.cff").read_text(encoding="utf-8"))


def _zenodo():
    return json.loads((REPO / ".zenodo.json").read_text(encoding="utf-8"))


def test_versions_agree_across_all_metadata_files():
    py_version = re.search(r'^version = "([^"]+)"', _pyproject_text(), re.M).group(1)
    r_version = re.search(r"^Version: (\S+)", _description_text(), re.M).group(1)
    cm = _codemeta()
    assert py_version == r_version == cm["version"] == cm["softwareVersion"] \
        == _cff()["version"]
    # The three copies this test used not to reach. __version__ is what getting-started
    # tells users to print and what datasheet.py falls back to when the distribution is
    # not installed; mkdocs.yml's is shown on every page of the documentation site; and
    # the R fallback is what a datasheet records where packageVersion() fails.
    init = (REPO / "python_workflow/src/lexsync/__init__.py").read_text(encoding="utf-8")
    assert re.search(r'^__version__ = "([^"]+)"', init, re.M).group(1) == py_version
    mk = (REPO / "python_workflow/mkdocs.yml").read_text(encoding="utf-8")
    assert re.search(r'^\s+version: "([^"]+)"', mk, re.M).group(1) == py_version
    ds = (REPO / "R_workflow/R/datasheet.R").read_text(encoding="utf-8")
    fallback = re.search(r'error = function\(e\) "([\d.]+)"\)', ds)
    assert fallback is None or fallback.group(1) == py_version
    # codemeta.json's citation holds each package's formatted reference, version
    # included. The trailing ". " stops a longer version such as 0.1.0.9000 from
    # matching.
    r_reference, python_reference = cm["citation"]
    assert re.search(rf"R package version {re.escape(py_version)}\. ", r_reference)
    assert re.search(rf"Python package version {re.escape(py_version)}\. ", python_reference)


def test_orcid_recorded_in_every_file_that_can_carry_one():
    # PEP 621 has no ORCID field, so pyproject.toml is exempt.
    assert ORCID in _description_text()
    cm = _codemeta()
    assert cm["author"][0]["@id"] == f"https://orcid.org/{ORCID}"
    assert cm["maintainer"][0]["@id"] == f"https://orcid.org/{ORCID}"
    assert _cff()["authors"][0]["orcid"] == f"https://orcid.org/{ORCID}"
    assert _zenodo()["creators"][0]["orcid"] == ORCID


def test_every_copy_of_the_cran_doi_is_the_same():
    # The DOI is typed by hand into each file that cites it, and a slip in any
    # one of them sends a reader to a dead link. R CMD check --as-cran reaches
    # only the copies inside the R package, and nothing else checks the rest.
    # A file can hold the DOI more than once: in a link and in a badge's alt
    # text, or in two places. An autolink (<https://doi.org/...>) is one copy,
    # serving as both text and link. Every DOI that starts 10.32614/CRAN or
    # names lexsync is collected, so a slip in any one copy shows up beside a
    # correct one. The bare 10.32614 prefix would also collect The R Journal's
    # DOIs, which the R Foundation issues under it. The pattern ends before a
    # full stop, which belongs to the sentence. The <wbr> tags that break the
    # DOI link in the pkgdown sidebar are markup, so they are removed first.
    doi = re.compile(r"10\.\d{4,9}/[\w./-]*[\w/-]")
    for rel in DOI_FILES:
        text = (REPO / rel).read_text(encoding="utf-8").replace("<wbr>", "")
        found = {d for d in doi.findall(text)
                 if d.lower().startswith("10.32614/cran") or "lexsync" in d.lower()}
        assert found == {CRAN_DOI}, f"{rel}: {sorted(found)}"


def test_the_repository_records_name_both_packages_alike():
    # CITATION.cff and codemeta.json describe the repository, which holds both
    # packages, so they cite it by the Zenodo concept DOI, which archives both,
    # and mark each package's own identifiers. They used to give the CRAN DOI,
    # which names the R package alone, as the DOI of the whole of lexsync.
    # repository-artifact takes a single address, so CRAN and PyPI are both
    # listed among the identifiers instead.
    cff = _cff()
    assert cff["doi"] == ZENODO_DOI
    assert "repository-artifact" not in cff
    assert [(i["type"], i["value"]) for i in cff["identifiers"]] == [
        ("doi", ZENODO_DOI), ("doi", CRAN_DOI), ("url", CRAN_URL), ("url", PYPI_URL)]
    cm = _codemeta()
    assert cm["identifier"] == f"https://doi.org/{ZENODO_DOI}"
    r_reference, python_reference = cm["citation"]
    assert r_reference.endswith(f"https://doi.org/{CRAN_DOI}")
    assert python_reference.endswith(f"https://doi.org/{ZENODO_DOI}")
    assert {CRAN_URL, f"https://doi.org/{CRAN_DOI}", PYPI_URL} <= set(cm["relatedLink"])


def test_every_copy_of_the_zenodo_doi_is_the_concept_doi():
    # Zenodo mints a DOI for each release as well as the concept DOI. A version
    # DOI here would pin a reader to one release, and a slip in the digits sends
    # them to someone else's record. The pattern takes any registrant prefix, so
    # a slip in 10.5281 is caught as well.
    dois = [i["value"] for i in _cff()["identifiers"] if i["type"] == "doi"]
    assert dois == [ZENODO_DOI, CRAN_DOI]
    for rel in ZENODO_FILES:
        text = (REPO / rel).read_text(encoding="utf-8")
        found = set(re.findall(r"10\.\d{4,9}/zenodo\.\d+", text))
        assert found == {ZENODO_DOI}, f"{rel}: {sorted(found)}"


def test_every_link_to_cran_uses_the_canonical_address():
    # The same slip in the address of the CRAN page would go unnoticed too, and
    # CRAN asks for this one form of it. The pattern is case-blind, so a
    # lower-case, http:// or /web/packages/ variant is caught, as is a slip in
    # the path. A slip in the host name escapes the pattern.
    assert CRAN_URL in [i["value"] for i in _cff()["identifiers"]]
    assert CRAN_URL in _codemeta()["relatedLink"]
    url = re.compile(r"https?://[\w.-]*r-project\.org(?:/[\w.=?&/-]*[\w=/])?", re.I)
    for rel in DOI_FILES + ("R_workflow/vignettes/lexsync.Rmd",):
        found = set(url.findall((REPO / rel).read_text(encoding="utf-8")))
        assert found <= {CRAN_URL}, f"{rel}: {sorted(found)}"


def test_licences_agree():
    # MIT for the code, CC BY-SA 4.0 for the wordfreq-derived example lexica that
    # both distributions ship. Every format states both in whatever form it has.
    # The R DESCRIPTION keeps the bare stub because CRAN's template check
    # constrains that field; its Copyright field carries the disclosure instead.
    assert "License: MIT + file LICENSE" in _description_text()
    assert "LICENSE.note" in _description_text()
    assert 'license = "MIT AND CC-BY-SA-4.0"' in _pyproject_text()
    assert _codemeta()["license"] == ["https://spdx.org/licenses/MIT.html",
                                      "https://spdx.org/licenses/CC-BY-SA-4.0.html"]
    assert _cff()["license"] == ["MIT", "CC-BY-SA-4.0"]
    # Zenodo takes one licence identifier, so the deposit is MIT and the data
    # terms are stated in the description instead.
    assert _zenodo()["license"] == "MIT"
    assert "CC BY-SA 4.0" in _zenodo()["description"]


def test_no_licence_classifier_beside_the_expression():
    # PEP 639 deprecates the "License ::" classifiers and lets a build backend
    # refuse one beside a License-Expression, as setuptools does. PyPI accepts
    # the pairing today, so nothing but this test stops one being added.
    text = _pyproject_text()
    classifiers = re.search(r"^classifiers = \[\n(.*?)^\]", text, re.M | re.S).group(1)
    assert "License ::" not in classifiers
    # The comment above the list gives the reason. It used to say that PyPI
    # rejects any upload carrying both, which Warehouse does not. It also pointed
    # at scopusflow's pyproject.toml as a file that still paired them, which
    # stops being true once that file drops its classifier.
    block = re.search(r"((?:^#.*\n)+)classifiers = \[", text, re.M).group(1)
    comment = " ".join(block.replace("#", " ").split())
    assert "PEP 639 deprecates licence classifiers" in comment
    assert "PyPI accepts the pairing" in comment
    assert "PyPI rejects" not in comment
    assert "scopusflow" not in comment


def test_the_bundled_data_terms_ship_with_both_packages():
    # The CSVs under inst/extdata and src/lexsync/data are the same wordfreq
    # derivatives, so a user of either package must be able to find the terms
    # without the repository. R CMD check knows LICENSE.note as a top-level file,
    # and pyproject declares it under license-files.
    for note in (REPO / "R_workflow" / "LICENSE.note",
                 REPO / "python_workflow" / "LICENSE.note"):
        text = note.read_text(encoding="utf-8")
        assert "CC BY-SA 4.0" in text
        assert "https://creativecommons.org/licenses/by-sa/4.0/" in text
        assert "SUBTLEX" in text
        for name in ("en_example.csv", "es_example.csv", "zh_example.csv"):
            assert name in text
        # The English slice keeps only forms SUBTLEX-US lists in lower case often enough,
        # so the list is a direct source of it.
        assert "is therefore a direct source of en_example.csv" in " ".join(text.split())


def test_no_dead_analysis_extra():
    # matplotlib is imported nowhere in the repository, so an `analysis`
    # extra would install a dependency the package never uses.
    text = _pyproject_text()
    assert "analysis" not in text
    assert "matplotlib" not in text


def test_codemeta_date_modified_covers_latest_feature_commits():
    cm = _codemeta()
    created = date.fromisoformat(cm["dateCreated"])
    modified = date.fromisoformat(cm["dateModified"])
    assert modified >= created
    # The continuous-design and pseudoword features landed on 2026-07-06;
    # dateModified must not claim the software is older than that.
    assert modified >= date(2026, 7, 6)


def test_citation_metadata_names_every_generation_target():
    # jsPsych and pseudoword generation ship in 0.1.0 (CHANGELOG.md), so the
    # citation records must not advertise a narrower tool than the code.
    for text in (_cff()["abstract"], _zenodo()["description"],
                 _codemeta()["description"]):
        for feature in ("PsychoPy", "OpenSesame", "jsPsych", "pseudoword"):
            assert feature in text, f"{feature!r} missing from: {text[:60]}..."
    for keywords in (_cff()["keywords"], _zenodo()["keywords"],
                     _codemeta()["keywords"]):
        assert "jsPsych" in keywords
        assert "pseudoword generation" in keywords


def test_citation_cff_declares_cff_1_2_0_with_required_fields():
    cff = _cff()
    assert cff["cff-version"] == "1.2.0"
    # The fields CFF 1.2.0 requires of every record.
    for field in ("message", "title", "authors"):
        assert field in cff
