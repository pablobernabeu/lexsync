"""Materials datasheet and pre-registration template.

A *materials datasheet* is a machine- and human-readable provenance record for a
design. It records where the items came from, how they were selected, matched and
counterbalanced, the realised control, and the seeds, versions and checksums needed
to reproduce them exactly. It is the shareable materials record whose scarcity
motivates lexsync (Bochynska et al., 2023; Roettger, 2019). The
module also emits an auto-filled Methods paragraph and a pre-registration
skeleton. Mirrors R_workflow/R/datasheet.R.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re

import pandas as pd
import yaml
from scipy import stats

# The cache and the registry, for crediting a lexicon fetch_corpus fetched.
from . import corpora as _corpora

# The recipe, the rotation check and the trial-order record come from the module that
# counterbalances, so the record describes the counterbalancing that ran.
from .counterbalancing import _recipe, _trial_order_record
from .counterbalancing import counterbalance_check as _counterbalance_check

# The tolerance windows and the number of items as the selectors resolve them: one
# resolver each, so the record cannot drift from the selection.
from .design import (
    _INT_MAX,
    N_DEFAULT_CONTINUOUS,
    N_DEFAULT_GENERATED,
    N_DEFAULT_MATCHED,
    _resolve_n,
    _resolve_tolerance_k,
)
from .io_utils import _fmt_dp, _fmt_g, _is_continuous, _round_dp, sha256_file

# The cap the pairwise (joint, optimal) matchers apply before pairing, and the
# tie-break rule and its salt. Imported from matching so the datasheet can only ever
# record the values the selection used.
from .matching import PAIRWISE_CAP, TIE_SALT, _resolve_tie_break
from .paradigms import resolve_events

# The versions, the response windows and the response mapping come from the module that
# writes the experiments, so the record counts the versions the participants are given
# and states the windows they respond in and the keys they press.
from .scripting import (
    _key_label,
    _refresh_hz,
    _response_keys,
    _response_mapping,
    _response_windows,
    _rotates,
    presentation_versions,
)

# 1.1 added `materials_source["norms"]` (the design's joined norm tables, with their
# checksums and per-column coverage) and, for a pair-keyed design, a `relational`
# block plus an honest `selection["cross_engine"]`. Both were required by the rule
# that anything affecting item selection is recorded here: a norm table can carry the
# manipulated variable itself, and the pair path performs a real selection that the
# record used to describe as "n/a (user-supplied items)".
#
# 1.2 records the counterbalancing that ran. Each later field of 1.2 adds a line here.
#   counterbalancing.recipe     the recipe counterbalance() applied (1.1 inferred it
#                               from the item source)
#   counterbalancing.lists      the lists the stimuli table holds (1.1 copied
#                               counterbalance.lists, with a default of 1)
#   counterbalancing.complete   whether a Latin-square rotation is complete
#   counterbalancing.issues     what leaves it incomplete
#   counterbalancing.cells      the trials per list and condition
#   materials_source["input_normalisation"]   what NFC normalisation did to the inputs
#                                             ({changed, collapsed}), present only when
#                                             it changed something
#   selection.incomplete_dropped  the candidates each condition lost for missing a
#                               matched dimension, present only when it lost any
#   counterbalancing.versions   the presentation versions, one per (replicate, list)
#   counterbalancing.assignment the rule that gives each participant one version
#   selection.neighbourhood_reference.applied_to
#                               the derived columns a supplied reference_words list
#                               recomputed. The record is now written only when one
#                               ran.
#   selection["generation_exclude"]   the known-form lists a generated pseudoword was
#                                     checked against ({source, sha256, n_forms} each),
#                                     present only when the design names any
#   selection.tie_break        the rule that broke exact ties between equally close
#                               candidates ({rule, salt}, the salt only for hash),
#                               present for a matched corpus or pool design
#   presentation.response_windows  each response event's window, {event, from,
#                               window_ms}; window_ms is null, with duration_column and
#                               timeout_ms, when the stimulus's duration varies by trial
#                               (analysis.response now says where a reaction time starts)
#   materials_source["exclusions"]    the design's exclude_words ({path, sha256,
#                                     n_listed, n_removed}), present only when the
#                                     design has the key
#   materials_source["provenance"]    for a corpus or generated design, the credit of
#                                     the lexicon read (see _lexicon_provenance).
#                                     Earlier records credited wordfreq for any file.
#   reproducibility.schema_path   the schema file the run read, in POSIX form
#   realised_control[].condition, realised_control[].reference
#                               the pair a row compares. Every pair is reported, the
#                               anchor rows first
#   realised_control[].mean_diff  the reference mean minus the condition mean, in the
#                               dimension's own unit
#   realised_control[].role     manipulated, controlled or uncontrolled for the pair
#                               (1.1 wrote "manipulated/free" for every unmatched row)
#   realised_control[].sd, .sd_ratio, .window_low, .window_high
#                               a continuous design's realised SDs, set against an even
#                               spread (the predictor) or the pool (a control), and each
#                               control's window
#   items.n_per_condition_realised  the items each condition holds, as {condition, n},
#                               or {replicate, condition, n} for resampled sets
#   design.n_per_condition      the request the selector applied, its default when the
#                               design gives none (1.1 copied the design's key, or null)
#   presentation.response_mapping  the key each condition takes, {conditions, keys,
#                               rotate_by_list, source}, present only when a mapping
#                               applies: the design's own or a lexical decision's default
#   materials_source["zipf_derivation"]   for a lexicon carrying freq_permillion, the
#                                     positive rates it holds and how many of them put
#                                     Zipf within 1e-9 of a rounding boundary
#                                     ({n_values, near_boundary})
#   counterbalancing.max_run    the run limit ({k, run_on, longest}), longest giving the
#                               longest run realised in each presentation version as
#                               {replicate, list, longest_run}, present only when the
#                               design sets counterbalance.max_run
#   counterbalancing.orders     the trial orders per list ({m, rule}), present only when
#                               the design sets counterbalance.orders above 1
DATASHEET_VERSION = "1.2"

# Datasheet labels for the pseudoword generators in generation.py, keyed by the
# items.generation.method token. Kept character-for-character identical to
# .GENERATION_LABELS in datasheet.R so the two engines' records stay comparable.
_GENERATION_LABELS = {
    "letter_substitution": "constrained letter substitution (deterministic pseudowords)",
    "subsyllabic": "subsyllabic constituent swap (Wuggy-style, deterministic pseudowords)",
}

# The credit the datasheet and the Methods paragraph give a lexicon lexsync ships.
# Kept character-for-character identical to the strings in datasheet.R.
_PROVENANCE_WORDFREQ = (
    "wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at "
    "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
_PROVENANCE_SCREENED = (
    "wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data "
    "CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in "
    "under 10% of their uses are marked nonstandard, and N and OLD20 count only the "
    "unmarked forms; full corpus licence and citation at "
    "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
# The English example slice holds only forms that en_v2.csv keeps, so it marks none.
_PROVENANCE_SCREENED_SLICE = (
    "wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data "
    "CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in "
    "under 10% of their uses are left out, and N and OLD20 count neighbours only among "
    "the forms the screen keeps; full corpus licence and citation at "
    "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")

# The lexica lexsync ships, the repository's derived lexica and the example slices both
# packages bundle. Each is keyed by the SHA-256 of its bytes with CRLF line ends read as
# LF (see _lf_sha256) and maps to its file and its credit. A rebuilt file needs its new
# key here and in .BUNDLED_LEXICA in datasheet.R, and the tests in
# test_lexicon_provenance.py fail until it has one.
_BUNDLED_LEXICA = {
    "575833489e04d6a4001fda56a56e3daa383811dece1f819c44060ee79ca56976":
        ("corpora/derived/en.csv", _PROVENANCE_WORDFREQ),
    "46815cd56ac036cb841460a2ea6205ac374eddb6ca26275bb1a2fbafc7c5d626":
        ("corpora/derived/en_v2.csv", _PROVENANCE_SCREENED),
    "e9f93013c16ec9745c0d02f82c697f2488c328365b95b57c5f04ac2565c123ea":
        ("corpora/derived/es.csv", _PROVENANCE_WORDFREQ),
    "0f77aec3fe307ed38f1e69e69f7c80ee93e38ffb8c0622b817fd2c26d15114d5":
        ("corpora/derived/es_gender.csv", _PROVENANCE_WORDFREQ),
    "74666b257c1ad7bce4694a4b172796fbdc08c1414183bea5f28faa5ed3ab2fc4":
        ("corpora/derived/zh.csv", _PROVENANCE_WORDFREQ),
    "34a3c81cb559a42918864f5ecd2bcea93647cc4b0058dd03132ffe8723f4c310":
        ("en_example.csv", _PROVENANCE_SCREENED_SLICE),
    "7afbdd7db2d84e3f252a40baafe1e53fa4fde1e4ae5256497cb1ac79f28947ec":
        ("es_example.csv", _PROVENANCE_WORDFREQ),
    "d42f5afdc16d0f23ec5fc12dd58afbd1e639e9191f2c4611d9262eabbb982aca":
        ("zh_example.csv", _PROVENANCE_WORDFREQ),
}


def _lf_sha256(path) -> str:
    """The SHA-256 of a file's bytes with every CRLF read as LF.

    Git stores the lexica with LF line ends. A checkout that converts them to CRLF, as
    one OneDrive copy of this repository did, holds the same lexicon under another
    checksum of its raw bytes. Mirrors .lf_sha256 in datasheet.R.
    """
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read().replace(b"\r\n", b"\n")).hexdigest()


def _file_name(path) -> str:
    return str(path).replace("\\", "/").rsplit("/", 1)[-1]


def _registry_citation(path):
    """The registry's citation for a lexicon fetch_corpus put in the cache, or None.

    The file must lie in lexsync's cache, and its name less `.csv` must name a corpus
    in the registry, or be ``<language>_wordfreq`` for a language the wordfreq
    connector lists. Those are the names fetch_corpus gives what it fetches. Mirrors
    .registry_citation in datasheet.R.
    """
    name = _file_name(path)
    if not name.endswith(".csv"):
        return None
    try:
        here = os.path.normcase(os.path.realpath(os.path.dirname(os.path.abspath(path))))
        cache = os.path.normcase(os.path.realpath(_corpora.cache_dir()))
        if here != cache:
            return None
        with open(_corpora._registry_path(None), encoding="utf-8") as handle:
            reg = yaml.safe_load(handle)
    except (OSError, ValueError, yaml.YAMLError):
        return None
    if not isinstance(reg, dict):
        return None
    stem = name[:-len(".csv")]
    corpora = reg.get("corpora")
    entry = corpora.get(stem) if isinstance(corpora, dict) else None
    if isinstance(entry, dict) and isinstance(entry.get("citation"), str):
        return entry["citation"]
    connector = reg.get("wordfreq_connector")
    if (isinstance(connector, dict) and isinstance(connector.get("citation"), str)
            and stem.endswith("_wordfreq")
            and stem[:-len("_wordfreq")] in (connector.get("languages") or [])):
        return connector["citation"]
    return None


def _lexicon_provenance(path) -> str:
    """The credit for the lexicon a corpus or generated design read.

    A lexicon lexsync ships is recognised by the checksum _lf_sha256 gives, and is
    credited to wordfreq, or for en_v2.csv and the English example slice drawn from it
    to wordfreq screened against SUBTLEX-US with the screening rule stated. A corpus
    fetch_corpus put in the cache is credited by
    the registry's citation. Any other file is the user's own and is named by its file
    name and the first twelve hexadecimal digits of its SHA-256, which
    ``materials_source["sha256"]`` holds in full. Every lexicon used to be credited to
    wordfreq, so a study selecting from SUBTLEX-US, or from a lexicon of its own, would
    have cited the wrong corpus. Mirrors .lexicon_provenance in datasheet.R.
    """
    if not path:
        return "a user-supplied lexicon"
    name = _file_name(path)
    if not os.path.isfile(path):
        return f"a user-supplied lexicon ({name})"
    bundled = _BUNDLED_LEXICA.get(_lf_sha256(path))
    if bundled is not None:
        return bundled[1]
    cited = _registry_citation(path)
    if cited is not None:
        return cited
    return f"a user-supplied lexicon ({name}, sha256 {sha256_file(path)[:12]})"


def _lexsync_version() -> str:
    """The installed lexsync version, mirroring datasheet.R's packageVersion lookup."""
    try:
        from importlib.metadata import version
        return version("lexsync")
    except Exception:
        # Deferred: __init__ imports this module before it binds __version__.
        from . import __version__
        return __version__


def _versions(engine: str) -> dict:
    out = {"engine": engine, "lexsync": _lexsync_version()}
    if engine == "python":
        import numpy as np
        import pandas as pd
        out["python"] = platform.python_version()
        out["pandas"] = pd.__version__
        out["numpy"] = np.__version__
        try:
            import scipy
            out["scipy"] = scipy.__version__
        except Exception:
            pass
        # Distribution metadata, because neither package exports __version__.
        from importlib.metadata import version
        for pkg in ("rapidfuzz", "pyyaml"):
            try:
                out[pkg] = version(pkg)
            except Exception:
                pass
    # The OS completes the environment record; per-engine, like the rest of the block.
    out["os"] = platform.system() + " " + platform.machine()
    return out


def _cross_engine(method, source: str, selected: bool = False) -> str:
    """Whether the R and Python engines select byte-identical materials.

    The deterministic methods are byte-identical; ``mahalanobis`` and ``optimal``
    are the exception, because they use a covariance-matrix inverse and an
    assignment solver whose last bits differ between the two linear-algebra
    backends (see matching.py).

    ``selected`` distinguishes the two things an item table can now mean. A plain
    table design does no selection, so there is nothing for the engines to agree on
    and "n/a" is the whole story. A pair-keyed continuous design selects over that
    table, and that selection was measured to be byte-identical, so answering "n/a"
    there understated the guarantee on the one path where a reader most needs it.
    """
    if source == "table" and not selected:
        return "n/a (user-supplied items)"
    if method in ("mahalanobis", "optimal"):
        return "approximate (platform linear algebra)"
    return "byte-identical"


def _relational_record(design: dict, stimuli) -> dict | None:
    """The pair-keyed part of the record, or None for a design that is not pair-keyed.

    Derived from the design and the realised stimuli rather than passed in, so both
    engines compute it from the same two objects and cannot disagree about it.

    Three of these fields answer questions the rest of the datasheet gets wrong for a
    pair design. ``n_pairs`` is stated because ``items["n_total"]`` counts ROWS, which
    is one per pair per condition, so a reader comparing it against the design's
    ``n_per_condition`` would find it doubled. The member lexicon is named and
    checksummed because it is where every member-level control came from, and nothing
    else in the record mentions it. ``materials_source`` names the item table. And
    the member dimensions are separated from the relational ones because they are
    different kinds of variable: ``target.frequency`` is a property of one word,
    ``pair.overlap`` is a property of the pair, and only the second is unavailable
    from any word-level norm database. Mirrors datasheet.R.
    """
    items_cfg = design.get("items") or {}
    members = list(items_cfg.get("members") or [])
    if not members:
        return None
    cols = list(stimuli.columns)
    # The union over members, not the first member's alone. join_member_norms gives
    # every member the same dimensions, so the sets coincide in anything the pipeline
    # produced; taking the union means a hand-built frame cannot report an empty list
    # merely because the first member happens to carry no prefixed column.
    # startswith, not a regex: a member name is user-supplied and may contain a
    # character a regex would read as syntax.
    member_dims = set()
    for m in members:
        prefix = m + "."
        member_dims.update(c[len(prefix):] for c in cols if c.startswith(prefix))
    lexicon = items_cfg.get("lexicon") or design.get("lexicon")
    return {
        "members": members,
        "n_pairs": int(stimuli["set"].nunique()),
        "member_lexicon": lexicon,
        "member_lexicon_sha256": sha256_file(lexicon),
        "member_dimensions": sorted(member_dims, key=lambda s: s.encode("utf-8")),
        "relational_dimensions": sorted((c for c in cols if c.startswith("pair.")),
                                        key=lambda s: s.encode("utf-8")),
    }


def _controlled(design: dict, source: str) -> list:
    # A supplied pool goes through the same matcher as a corpus, so it controls the same
    # dimensions; only the origin of the candidate words differs.
    if source in ("corpus", "pool"):
        return list(design.get("match_on") or [])
    if source == "generate":
        return ["length"]
    return []


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _same_window(a, b) -> bool:
    """Whether two conditions' ``define_by`` entries on one dimension select alike.

    Absent from both is alike, and absent from one only is not. A two-number entry is
    a range compared bound by bound, numerically, so [5, 7] and [5.0, 7.0] are alike.
    Any other entry is a set of permitted values, compared as a set: numerically when
    both hold only numbers, and otherwise as text. Mirrors .same_window in
    R_workflow/R/datasheet.R.
    """
    if a is None or b is None:
        return a is None and b is None
    a = list(a) if isinstance(a, (list, tuple)) else [a]
    b = list(b) if isinstance(b, (list, tuple)) else [b]
    if len(a) != len(b):
        return False
    if all(_is_number(v) for v in a + b):
        a, b = [float(v) for v in a], [float(v) for v in b]
        return a == b if len(a) == 2 else sorted(a) == sorted(b)
    return sorted(str(v) for v in a) == sorted(str(v) for v in b)


def _comparison_roles(design: dict, controlled):
    """The role of a realised-control row, as a function of (condition, reference,
    dimension).

    A row is ``manipulated`` when the two conditions' ``define_by`` entries on the
    dimension differ, or when the dimension is a continuous design's predictor. It is
    ``controlled`` when the dimension is among ``controlled``, the dimensions the
    selection matched on (``match_on``, or ``length`` for generated pseudowords), and
    ``uncontrolled`` otherwise. In a 2 x 2 design, frequency is manipulated between a
    high- and a low-frequency cell but not between two cells that share its window.
    ``run_pipeline`` passes this to ``match_report``, and ``build_datasheet`` falls
    back on it for a report without roles. Mirrors .comparison_roles in
    R_workflow/R/datasheet.R.
    """
    windows = {}
    for cond in design.get("conditions") or []:
        if isinstance(cond, dict) and isinstance(cond.get("define_by"), dict):
            windows[str(cond.get("name"))] = cond["define_by"]
    cont = design.get("continuous")
    predictor = cont.get("predictor") if isinstance(cont, dict) else None
    controlled = set(controlled)

    def role(condition, reference, dimension):
        a = windows.get(str(condition)) or {}
        b = windows.get(str(reference)) or {}
        if dimension == predictor or not _same_window(a.get(dimension), b.get(dimension)):
            return "manipulated"
        return "controlled" if dimension in controlled else "uncontrolled"

    return role


def _response_text(windows: list, events: list) -> str:
    """The response the analysis models, with where its reaction time starts.

    From the first response window: a reaction time from the onset of the stimulus
    the response answers, or from the opening of a window after it. A design without a
    response event keeps the generic outcome. Mirrors .response_text in datasheet.R.
    """
    if not windows:
        return "the trial outcome (e.g. reaction time or accuracy)"
    w = windows[0]
    if w["from"] == "offset":
        return ("reaction time from the opening of a response window after the stimulus; "
                "responses collected for %d ms; a response ends the trial" % w["window_ms"])
    target = str(events[w["event"] - 2].get("content", ""))
    span = ("for %d ms" % w["window_ms"] if w["window_ms"] is not None
            else "until %d ms after its offset" % w["timeout_ms"])
    return ("reaction time from the onset of `%s`; responses collected %s; a response "
            "ends the trial" % (target, span))


def _response_note(ds: dict) -> str:
    """The response window, for the Methods text.

    From the first response window the record holds. Empty without one, and for a
    record written before the field existed. Mirrors .response_note in datasheet.R.
    """
    windows = (ds.get("presentation") or {}).get("response_windows") or []
    if not windows:
        return ""
    w = windows[0]
    if w["from"] == "offset":
        return (" Responses were collected in a %d ms window that opened after the "
                "stimulus, and a response ended the trial." % int(w["window_ms"]))
    if w.get("window_ms") is None:
        return (" Responses were collected from target onset until %d ms after its "
                "offset, and a response ended the trial." % int(w["timeout_ms"]))
    return (" Responses were collected from target onset until %d ms after it, and a "
            "response ended the trial." % int(w["window_ms"]))


def _response_mapping_record(design: dict):
    """The response mapping the experiments score against, as the record keeps it.

    ``{conditions, keys, rotate_by_list, source}``: the key each condition takes in list
    1, the keys the response event allows in their order, whether the mapping rotates
    across lists and whether it is the design's own or a lexical decision's default.
    None when no mapping applies. Mirrors .response_mapping_record in datasheet.R.
    """
    mapping = _response_mapping(design)
    if mapping is None:
        return None
    return {"conditions": dict(mapping), "keys": list(_response_keys(design)),
            "rotate_by_list": _rotates(design),
            "source": "default" if design.get("response_mapping") is None else "design"}


def _mapping_note(ds: dict) -> str:
    """The response mapping, for the Methods text: which key the participants pressed for
    which condition, and how it rotated across lists.

    The keys come in the response event's order and the conditions that share a key in
    code-point order, so a record read back from its JSON, whose objects this engine
    writes with sorted keys, renders the same text. A rotation is mentioned only when the
    record holds more than one list. Empty without a mapping, and for a record written
    before the field existed. Mirrors .mapping_note in datasheet.R.
    """
    rec = (ds.get("presentation") or {}).get("response_mapping")
    if not rec:
        return ""
    named = {"word": "words", "pseudoword": "pseudowords"}
    phrases = []
    for key in dict.fromkeys(rec["keys"]):
        conds = sorted(c for c, k in rec["conditions"].items() if k == key)
        if conds:
            what = (named[conds[0]] if len(conds) == 1 and conds[0] in named
                    else _and_join(conds) + " trials")
            phrases.append("%s for %s" % (_key_label(key), what))
    text = " Participants pressed " + _and_join(phrases)
    lists = int((ds.get("counterbalancing") or {}).get("lists") or 1)
    if rec.get("rotate_by_list") and lists > 1:
        if len(rec["keys"]) == 2:
            text += " in odd-numbered lists and the reverse in even-numbered lists"
        else:
            text += " in list 1, and the keys rotated by one place in each further list"
    return text + "."


def _and_join(parts) -> str:
    """Words or phrases joined as a list in prose: "a", "a and b", "a, b and c"."""
    parts = [str(p) for p in parts]
    if len(parts) < 2:
        return "".join(parts)
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def _requested_n(design: dict, source: str, is_continuous: bool):
    """The items per condition the selector was asked for: the design's
    ``n_per_condition``, else the default of the selector that ran, the matcher's,
    the continuous selector's or the generator's. An item table without a continuous
    block selects nothing, so it has a request only when the design states one. The
    record used to copy the design's key, and gave null when a design left the number
    to the matcher. Mirrors .requested_n in datasheet.R.
    """
    if is_continuous:
        default = N_DEFAULT_CONTINUOUS
    elif source in ("corpus", "pool"):
        default = N_DEFAULT_MATCHED
    elif source == "generate":
        default = N_DEFAULT_GENERATED
    else:
        default = None
    return _resolve_n(design, default)


def _realised_counts(stimuli, conditions) -> list:
    """The items each condition holds in the stimuli, as ``{condition, n}`` records in
    the order of ``items.conditions``. Resampled stimuli are counted per replicate, as
    ``{replicate, condition, n}``, replicates in ascending order, since each replicate
    is a set of its own. A pair design holds one row per pair in each condition, so it
    counts pairs. Mirrors .realised_counts in datasheet.R.
    """
    labels = stimuli["condition"].astype(str).to_numpy()
    if "replicate" not in stimuli.columns:
        return [{"condition": str(c), "n": int((labels == str(c)).sum())} for c in conditions]
    out = []
    reps = stimuli["replicate"].to_numpy()
    for rep in sorted(set(stimuli["replicate"])):
        for c in conditions:
            n = int(((reps == rep) & (labels == str(c))).sum())
            if n:
                out.append({"replicate": int(rep), "condition": str(c), "n": n})
    return out


def _covariates(design: dict, source: str, stimuli) -> tuple:
    """The matched dimensions the suggested model adjusts for, and those it leaves out.

    A corpus or pool design's ``match_on`` dimensions enter, in their order, when they
    vary among the selected items. One that is the same for every item, as length is
    among two-character Chinese words, would give the model a column of zeros, so it
    is left out, as is one the stimuli do not hold. Any other design has none. Mirrors
    .covariates in datasheet.R.
    """
    if source not in ("corpus", "pool"):
        return [], []
    kept, left_out = [], []
    for dim in design.get("match_on") or []:
        values = (set(pd.to_numeric(stimuli[dim], errors="coerce").dropna())
                  if dim in stimuli.columns else set())
        (kept if len(values) > 1 else left_out).append(dim)
    return kept, left_out


# The sentences the notes of the suggested models share. Kept character-for-character
# identical to the strings in .analysis_R in datasheet.R.
_NOTE_CROSSED = ("Crossed random effects for subjects and items guard against the "
                 "language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008).")
_NOTE_SIMPLIFY = ("If the model is singular or fails to converge, simplify it as "
                  "Matuschek et al. (2017) describe.")
_NOTE_SYNTAX = ("The formula is lme4 syntax, for lme4 in R or pymer4 in Python; "
                "statsmodels MixedLM cannot take it directly and needs the random effects "
                "restated in its own arguments.")
_NOTE_DIAGNOSTICS = ("The equivalence tests in the realised control are post-selection "
                     "diagnostics on deterministically selected items, not inferential "
                     "tests over a sample.")


def _analysis(design: dict, source: str,
              response: str = "the trial outcome (e.g. reaction time or accuracy)",
              recipe: str = "factorial", n_conditions: int = 2, covariates=(),
              left_out=()) -> dict:
    """A suggested crossed mixed-model formula for the design, and a note on it.

    Handing the user an items-crossed model guards against the
    language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008): items are
    a random sample of the language, so an analysis that treats them as fixed
    over-generalises. The factor is the stimuli's ``condition`` column, which in a
    lexical decision codes lexicality. Every participant sees every condition, so
    subjects take a random slope for it. Items take one too when the counterbalancing
    recipe that ran rotates the conditions over the items by a Latin square, which
    shows each item in more than one condition across the lists. ``covariates`` are a matched
    design's matched dimensions that vary among its items, entered centred on the
    stimuli file's own columns, since matching leaves residual differences and
    Sassenhagen and Alday (2016) recommend adjusting for potential confounds;
    ``left_out`` are those that do not vary. A design with more than two conditions is
    told how to recode crossed factors.

    A continuous design regresses on its predictor and controls. A pair design with
    more than one condition crosses the condition with the predictor, and its items,
    which carry every condition, take the condition slope. The predictor is a property
    of the item, so they take no slope for it.

    The note calls the structure maximal (Barr et al., 2013) only when every fixed
    effect that varies within subjects or items has a random slope there. A covariate
    or a control varies within subjects and enters as a fixed effect only, so a design
    with one is described by its slopes. Mirrors .analysis_R in datasheet.R.
    """
    cont = design.get("continuous")
    if cont:
        predictor = cont["predictor"]
        controls = list(cont.get("controls") or [])
        tail = "".join(" + " + c for c in controls)
        if (design.get("items") or {}).get("members") and n_conditions > 1:
            model = (f"response ~ condition * {predictor}{tail} + "
                     f"(1 + condition * {predictor} | subject) + (1 + condition | item)")
            slopes = (f"Begin with random slopes for condition, {predictor} and their "
                      "interaction by subject and for condition by item (Barr et al., "
                      "2013); the controls enter as fixed effects only. Centre "
                      f"{predictor} and sum-code condition, so that each main effect is "
                      "estimated at the average of the other.")
        else:
            model = f"response ~ {predictor}{tail} + (1 + {predictor} | subject) + (1 | item)"
            slopes = (f"Begin with a random slope for {predictor} by subject (Barr et al., "
                      "2013); the controls enter as fixed effects only.")
        note = ("The predictor is kept continuous and analysed by regression or a mixed "
                "model rather than dichotomised (Kuperman, 2015; Liben-Nowell et al., "
                "2019); the controls enter as covariates. " + _NOTE_CROSSED + " " + slopes
                + " " + _NOTE_SIMPLIFY)
        # A pair design's member-prefixed terms carry a dot, which R formulas accept
        # but Patsy reads as syntax, so the Python analyst needs the quoting stated.
        if any("." in t for t in [predictor] + controls):
            note += (" Dotted dimension names are valid in R formulas but must be "
                     "quoted as Q(\"...\") in Patsy-style Python interfaces.")
        return {"response": response, "suggested_model": model, "note": note}
    fixed = "condition" + "".join(" + scale(%s, scale = FALSE)" % d for d in covariates)
    item_re = "(1 + condition | item)" if recipe == "latin_square_target" else "(1 | item)"
    note = [_NOTE_CROSSED]
    if source == "generate" or design.get("paradigm") == "lexical_decision":
        note.append("The condition column codes lexicality, word or pseudoword.")
    if covariates:
        note.append("The matched dimensions enter as centred covariates, computed from the "
                    "stimuli file's own columns, because matching leaves residual "
                    "differences that the analysis can adjust for (Sassenhagen & Alday, "
                    "2016).")
    if left_out:
        one = len(left_out) == 1
        note.append("The matched %s %s %s constant among the selected items, so %s left out."
                    % ("dimension" if one else "dimensions", _and_join(left_out),
                       "is" if one else "are", "it is" if one else "they are"))
    if covariates:
        note.append("Begin with random slopes for condition, the manipulated factor, by "
                    "subject and, where it varies within items, by item (Barr et al., "
                    "2013); the matched covariates enter as fixed effects only.")
    else:
        note.append("Begin with this maximal structure (Barr et al., 2013).")
    note.append(_NOTE_SIMPLIFY)
    if n_conditions > 2:
        note.append("If the conditions cross two or more factors, recode condition into "
                    "those factors (for example frequency * neighbourhood) with sum coding.")
    note += [_NOTE_SYNTAX, _NOTE_DIAGNOSTICS]
    return {"response": response,
            "suggested_model": f"response ~ {fixed} + (1 + condition | subject) + {item_re}",
            "note": " ".join(note)}


def build_datasheet(design, schema, report, stimuli, source_path, artifacts,
                    seed, engine="python", candidate_pool=None, norms=None,
                    balance=None, blocks=None, design_path=None, schema_path=None,
                    selection_audit=None, neighbourhood_reference=None,
                    counterbalance_check=None, input_normalisation=None,
                    generation_exclude=None, exclusions=None, zipf_derivation=None,
                    trial_order=None) -> dict:
    """Assemble the datasheet dictionary from the pipeline's objects.

    For a corpus or generated design, ``materials_source["provenance"]`` credits the
    lexicon that ``source_path`` names. A lexicon lexsync ships is credited by its
    source, a corpus fetched into the cache by the registry's citation, and any other
    file by its file name and checksum (see ``_lexicon_provenance``).

    ``candidate_pool`` (optional) is a list of ``{"condition", "n_candidates"}``
    recording how many items satisfied each condition's window before matching,
    the size of the discretionary pool the selection drew from, reported so that
    item-selection bias is auditable (Forster, 2000; Simmons et al., 2011).

    ``norms`` (optional) is a list of norm-table provenance records from the design's
    ``norms:`` block. Each names a file, its sha256, the join key and the per-column
    coverage. Recorded because a norm table can supply the very variable a design
    manipulates, so a record that omitted it would describe a selection over columns
    of unstated origin.

    ``balance`` (optional) is the balance-optimiser report from ``balance_lists``.
    Recorded because it decides which items each participant sees.

    ``design_path`` / ``schema_path`` (optional) are the design and schema files the
    run read; when given, their sha256 checksums complete the reproducibility
    record, because those two files decide everything the seed does not. The
    schema's path is recorded too, in POSIX form, since an unnamed schema is chosen
    from several candidates.

    ``selection_audit`` (optional) is the matcher's audit record; its
    ``window_relaxations`` entries are recorded because a relaxed window changes
    what "matched" means for that condition. Its ``incomplete_dropped`` entries
    (``{"condition", "n"}``) count the candidates excluded for missing a matched
    dimension, which ``candidate_pool`` still includes. They are recorded because
    the selection drew on a smaller pool than the window holds.

    ``neighbourhood_reference`` (optional) records a supplied reference the derived
    dimensions were recomputed against (``{"source", "n_words", "sha256",
    "applied_to"}``, where ``applied_to`` lists the recomputed columns), verbatim.

    ``counterbalance_check`` (optional) is the pipeline's ``counterbalance_check``
    report on the counterbalanced table. Without it, the check is run here on
    ``stimuli``. The record gives the recipe that ran and the lists the table holds,
    or for a table without a ``list`` column the lists counterbalance() would deal. It
    says whether a Latin-square rotation is complete and counts the trials per list
    and condition. It also gives the presentation versions, one per (replicate, list)
    pair, and the rule that assigns each participant one of them.

    ``input_normalisation`` (optional) is ``{"changed", "collapsed"}``: how many text
    keys the run's inputs held that Unicode NFC normalisation rewrote, and how many
    duplicates the rewriting created and removed. Recorded only when given, which the
    pipeline does only when either count is above zero, because a merged spelling
    changes the candidate pool.

    ``artifacts`` names the files written for the design: ``stimuli``,
    ``descriptives``, ``comparisons`` and ``experiments``, the result of
    ``export_experiments``. Each file is recorded with its sha256: the three tables,
    then every file in ``experiments["files"]``, the loop and text tables included,
    or the three experiment paths of a result that has no ``files``.

    ``generation_exclude`` (optional, generated designs) lists the known-form lists
    of ``items.generation.exclude`` as ``{"source", "sha256", "n_forms"}`` records.
    A pseudoword was refused for equalling any form in them, so they decide which
    pseudowords a run produces, as the lexicon does.

    ``exclusions`` (optional, corpus, pool and generated designs) records the design's
    ``exclude_words`` as ``{"path", "sha256", "n_listed", "n_removed"}``. It gives the
    file, or "inline" for a list in the design, its checksum, the number of distinct
    words it lists and the number of candidates it removed. Recorded as
    ``materials_source["exclusions"]``, because the words decide which candidates the
    selection could draw.

    ``zipf_derivation`` (optional) is ``{"n_values", "near_boundary"}`` for a lexicon
    carrying ``freq_permillion``, as ``normalise_lexicon`` writes one: how many positive
    rates it holds, and how many put Zipf = log10(per million) + 3 within 1e-9 of a
    three-place rounding boundary, where the two engines' log10 could round a derived
    value apart. Recorded as ``materials_source["zipf_derivation"]``.

    ``trial_order`` (optional) is the trial-order record of the presented trials, which
    the pipeline passes. Without it, the record is taken from ``stimuli``. It gives
    ``counterbalancing["max_run"]`` (``{"k", "run_on", "longest"}``, the longest run
    realised in each presentation version) when the design limits runs, and
    ``counterbalancing["orders"]`` (``{"m", "rule"}``) when it asks for more than one
    trial order.

    ``design["n_per_condition"]`` is the request the selector applied, the selector's
    default when the design gives none, and ``items["n_per_condition_realised"]``
    counts the items each condition holds in ``stimuli``, per replicate for resampled
    sets, so a selection that fell short of the request under ``shortfall: allow``
    shows it. The suggested analysis keys its by-item slope on the recipe that ran and
    adds a matched design's matched dimensions that vary among its items as covariates.
    """
    source = (design.get("items") or {}).get("source", "corpus")
    is_continuous = _is_continuous(design)
    controlled = _controlled(design, source)
    relational = _relational_record(design, stimuli)
    conditions = list(dict.fromkeys(stimuli["condition"]))
    covariates, left_out = (([], []) if is_continuous
                            else _covariates(design, source, stimuli))
    # The response windows the generated experiments open, and with them where a
    # reaction time starts, which the analysis has to know.
    events = resolve_events(design)
    windows = _response_windows(events, design.get("timing") or {}, _refresh_hz(schema))
    incomplete = (selection_audit or {}).get("incomplete_dropped") or []
    dropped = {d["condition"]: int(d["n"]) for d in incomplete}

    realised = []
    if report is not None:
        # A report the pipeline wrote carries each row's role. One from a direct call
        # of match_report may not, and its roles are then taken from the design.
        role_of = _comparison_roles(design, controlled)
        for _, r in report["comparisons"].iterrows():
            if is_continuous:
                realised.append({
                    "dimension": r["dimension"], "role": r["role"],
                    "pearson_r": _num(r.get("pearson_r")),
                    "predictor_span": _num(r.get("predictor_span")),
                    "sd": _num(r.get("sd")), "sd_ratio": _num(r.get("sd_ratio")),
                    "window_low": _num(r.get("window_low")),
                    "window_high": _num(r.get("window_high")),
                })
            else:
                role = r.get("role")
                if not isinstance(role, str):
                    role = role_of(r["condition"], r["reference"], r["dimension"])
                realised.append({
                    "condition": r["condition"], "reference": r["reference"],
                    "dimension": r["dimension"], "role": role,
                    "cohens_d": _num(r["cohens_d"]),
                    "ci_low": _num(r.get("d_ci_low")), "ci_high": _num(r.get("d_ci_high")),
                    "var_ratio": _num(r.get("var_ratio")),
                    "tost_p": _num(r.get("tost_p")), "equivalent": _bool(r.get("equivalent")),
                    "mean_diff": _num(r.get("mean_diff")),
                })

    if is_continuous:
        # The controls are banded by the same tolerance windows the matcher uses, so
        # the record states them here too; without them the banding is unreproducible.
        selection = {"method": "continuous even-spread (predictor spanned, controls banded)",
                     "predictor": design["continuous"]["predictor"],
                     "controls": list(design["continuous"].get("controls") or []),
                     "tolerance_k": _resolve_tolerance_k(design, schema)}
    elif source in ("corpus", "pool"):
        method = ((design.get("matching") or {}).get("method")
                  or (schema.get("matching") or {}).get("method")
                  or "standardised_euclidean")
        selection = {"method": method, "match_on": controlled}
        if method in ("joint", "optimal"):
            # The pairwise methods rank whole pairs and never consult the tolerance
            # windows; recording tolerance_k here would claim a filter that was not
            # applied. They get the cap they do apply instead, with a per-condition
            # verdict on whether it fired. The candidates excluded for a missing
            # matched value never reach the cap, so the verdict counts the rest.
            selection["candidate_cap"] = {
                "cap": int(PAIRWISE_CAP),
                "applied": {c["condition"]: bool(c["n_candidates"]
                                                 - dropped.get(c["condition"], 0)
                                                 > PAIRWISE_CAP)
                            for c in (candidate_pool or [])
                            if c.get("condition") is not None
                            and c.get("n_candidates") is not None},
            }
        else:
            selection["tolerance_k"] = _resolve_tolerance_k(design, schema)
        # Exact ties decide most picks when the matched dimensions are whole numbers, so
        # the rule that broke them is part of the selection. The salt goes with the
        # hash, which makes every tie key recomputable from the record.
        rule = _resolve_tie_break(design, schema)
        selection["tie_break"] = ({"rule": rule, "salt": TIE_SALT} if rule == "hash"
                                  else {"rule": rule})
    elif source == "generate":
        gen_method = ((design.get("items") or {}).get("generation") or {}).get(
            "method", "letter_substitution")
        selection = {"method": _GENERATION_LABELS.get(
            gen_method, f"{gen_method} (deterministic pseudowords)"),
            "generation_method": gen_method,
            "matched_on": ["length"]}
    else:
        selection = {"method": "item table (user-supplied)"}
    if candidate_pool is not None and source in ("corpus", "pool", "generate"):
        selection["candidate_pool"] = candidate_pool
    # A pair-keyed continuous design does select, over the item table.
    selection["cross_engine"] = _cross_engine(
        selection.get("method"), source, selected=is_continuous and relational is not None)
    # A relaxed window changes what "matched" means for that condition, so the
    # matcher's audit trail belongs in the record, not only in the run narration.
    # Integers only, so both engines serialise the counts identically.
    relaxations = (selection_audit or {}).get("window_relaxations") or []
    if relaxations:
        selection["window_relaxations"] = [
            {"condition": r["condition"],
             "n_within_tolerance": int(r["n_within_tolerance"]),
             "n_needed": int(r["n_needed"])} for r in relaxations]
    # The candidates excluded for missing a matched dimension, which candidate_pool
    # still counts: the selection drew on a smaller pool than the windows hold.
    if incomplete:
        selection["incomplete_dropped"] = [
            {"condition": d["condition"], "n": int(d["n"])} for d in incomplete]
    if neighbourhood_reference is not None:
        selection["neighbourhood_reference"] = neighbourhood_reference
    if generation_exclude and source == "generate":
        selection["generation_exclude"] = [
            {"source": r["source"], "sha256": r["sha256"], "n_forms": int(r["n_forms"])}
            for r in generation_exclude]

    if source in ("corpus", "generate"):
        provenance = _lexicon_provenance(source_path)
    elif source == "pool":
        provenance = "user-supplied word pool, matched by lexsync"
    else:
        provenance = "user-supplied item table"
    materials_source = {
        "type": source, "path": _posix(source_path), "sha256": sha256_file(source_path),
        "provenance": provenance,
    }
    # A supplied pool usually draws its dimensions from a corpus lexicon, and that
    # lexicon is where every matched value came from, so it is named and checksummed
    # here: `path` above records only the word list itself.
    if source == "pool":
        dim_lex = (design.get("items") or {}).get("lexicon") or design.get("lexicon")
        materials_source["dimensions_from"] = (
            dim_lex if dim_lex else "the supplied pool's own columns (no lexicon given)")
        if dim_lex:
            materials_source["dimensions_sha256"] = sha256_file(dim_lex)
    # Added only when present, so a design with no `norms:` block gets no key at all
    # rather than a "norms": null that every datasheet would then carry. Matches the R
    # engine, where assigning NULL to a list element removes it.
    if norms:
        materials_source["norms"] = norms
    # The words the design took out of the candidates, after the norms and before the
    # pool filters. Integers as integers, so both engines write the same JSON.
    if exclusions is not None and source in ("corpus", "pool", "generate"):
        materials_source["exclusions"] = {
            "path": exclusions["path"], "sha256": exclusions["sha256"],
            "n_listed": int(exclusions["n_listed"]),
            "n_removed": int(exclusions["n_removed"])}
    if input_normalisation is not None:
        materials_source["input_normalisation"] = {
            "changed": int(input_normalisation["changed"]),
            "collapsed": int(input_normalisation["collapsed"])}
    if zipf_derivation is not None:
        materials_source["zipf_derivation"] = {
            "n_values": int(zipf_derivation["n_values"]),
            "near_boundary": int(zipf_derivation["near_boundary"])}

    # A corpus design draws on every schema dimension, and so does a pair-keyed
    # design: every lexicon dimension is joined onto each member. A generate or plain
    # table design reports only the ones it controlled, so the record does not claim
    # dimensions that played no part in the selection.
    all_dims = source in ("corpus", "pool") or relational is not None
    # `or {}`, not a default argument, for the reason load_lexicon carries the same
    # guard: an empty `dimensions:` key parses to None here, which is not iterable,
    # while the R twin's schema$dimensions[keep] returns NULL and the record simply
    # carries no dimensions.
    schema_dims = schema.get("dimensions") or {}
    dims = {d: schema_dims[d] for d in schema_dims if all_dims or d in controlled}

    # The recipe comes from the resolver counterbalance() dispatches on, and the lists
    # from the table. The record used to infer the recipe from the item source and to
    # copy counterbalance.lists with a default of 1, though a Latin square without
    # that key deals one list per condition.
    recipe = _recipe(design)
    check = (counterbalance_check if counterbalance_check is not None
             else _counterbalance_check(stimuli, design, recipe))
    versions = _version_count(stimuli, int(check["lists"]))
    counterbalancing = {
        "recipe": recipe,
        "lists": int(check["lists"]),
        "complete": bool(check["complete"]),
        "issues": list(check["issues"]),
        "cells": list(check["cells"]),
        "versions": versions,
        "assignment": (f"version = ((participant - 1) mod {versions}) + 1 unless a version "
                       "is given at launch"),
    }
    # The balance report is added only when the optimiser ran, for the same reason the
    # norms record is: a key that is null on every design that does not use the feature
    # is noise in a research artefact.
    if balance:
        counterbalancing["optimise"] = balance
    # Practice and filler trials change what a participant sees but not what is
    # analysed, so the record has to state both counts: a reader comparing the stimuli
    # file against the experiment would otherwise find them a different length with no
    # explanation.
    if blocks:
        counterbalancing["blocks"] = blocks
    # The run limit and the trial orders, recorded only when the design sets them, so a
    # design without either keeps the record it had.
    if trial_order is None:
        trial_order = _trial_order_record(stimuli, design)
    if trial_order.get("max_run"):
        counterbalancing["max_run"] = trial_order["max_run"]
    if trial_order.get("orders"):
        m = int(trial_order["orders"])
        counterbalancing["orders"] = {
            "m": m, "rule": (f"order = (((participant - 1) div {versions}) mod {m}) + 1; a "
                             "run without a participant number presents order 1")}

    # The equivalence settings the report's TOST verdicts were computed against,
    # recorded so the Methods prose can state the bound it actually ran with.
    equivalence = {"bound_d": (schema.get("equivalence") or {}).get("bound_d", 0.5),
                   "alpha": (schema.get("equivalence") or {}).get("alpha", 0.05)}

    # The key the participants pressed for each condition, recorded only when a response
    # mapping applies: the design's own, or a lexical decision's default.
    presentation = {"response_windows": windows}
    mapping = _response_mapping_record(design)
    if mapping is not None:
        presentation["response_mapping"] = mapping

    reproducibility = {"seed": seed, "versions": _versions(engine)}
    # The design and schema decide everything the seed does not, so their checksums
    # complete the reproducibility record when the pipeline names them.
    if design_path is not None:
        reproducibility["design_sha256"] = sha256_file(design_path)
    if schema_path is not None:
        # The path as well as the checksum: when no schema was named, the run chose
        # one of several files, and the record has to say which.
        reproducibility["schema_path"] = _posix(schema_path)
        reproducibility["schema_sha256"] = sha256_file(schema_path)

    return {
        "lexsync_datasheet_version": DATASHEET_VERSION,
        "design": {
            "name": design["name"], "language": design["language"],
            "paradigm": design.get("paradigm", "factorial"), "source": source,
            "description": design.get("description"),
            "n_per_condition": _requested_n(design, source, is_continuous),
        },
        "materials_source": materials_source,
        "dimensions": dims,
        "selection": selection,
        "relational": relational,
        "analysis": _analysis(design, source, _response_text(windows, events), recipe=recipe,
                              n_conditions=len(conditions), covariates=covariates,
                              left_out=left_out),
        "equivalence": equivalence,
        "realised_control": realised,
        "counterbalancing": counterbalancing,
        "presentation": presentation,
        "resampling": ({"n_sets": (design.get("resample") or {}).get("n_sets"),
                        "disjoint": True} if design.get("resample") else None),
        "items": {
            "n_total": int(len(stimuli)), "n_conditions": len(conditions),
            "conditions": conditions,
            "n_per_condition_realised": _realised_counts(stimuli, conditions),
            "stimuli_file": _posix(artifacts.get("stimuli")),
            "stimuli_sha256": sha256_file(artifacts.get("stimuli")),
        },
        "reproducibility": reproducibility,
        "artifacts": [{"file": _posix(p), "sha256": sha256_file(p)}
                      for p in _artifact_paths(artifacts) if p],
    }


def _posix(path):
    """Record a path in POSIX form, as R's file.path() already produces.

    os.path.join gives backslashes on Windows, which would make the datasheet, a
    record meant to travel with the materials and be read anywhere, describe the
    machine that happened to build it, and disagree with the R engine's record of the
    same file.
    """
    return path.replace("\\", "/") if isinstance(path, str) else path


def _artifact_paths(artifacts: dict) -> list:
    """The files the record checksums: the three tables, then every experiment file.

    ``export_experiments`` lists every file it wrote under ``files``, the loop and text
    tables that hold the trial order and the trigger codes among them. A result without
    ``files`` contributes its three experiment paths. Mirrors .artifact_paths in
    datasheet.R.
    """
    paths = [artifacts.get(k) for k in ("stimuli", "descriptives", "comparisons")]
    exps = artifacts.get("experiments") or {}
    files = exps.get("files")
    paths += list(files) if files is not None else list(exps.values())
    return paths


def _version_count(stimuli, lists: int) -> int:
    """The presentation versions the trials give, one per (replicate, list) pair.

    A table without a ``list`` column has the lists counterbalance() would deal in
    each replicate, ``lists`` of them, as the record's ``lists`` does. Mirrors
    .version_count in datasheet.R.
    """
    if "list" in stimuli.columns:
        return len(presentation_versions(stimuli))
    replicates = int(stimuli["replicate"].nunique()) if "replicate" in stimuli.columns else 1
    return max(replicates, 1) * int(lists)


def _versions_note(ds: dict) -> str:
    """How participants met the presentation versions, for the Methods text.

    Empty for a single version, and for a record written before the field existed.
    Mirrors .versions_note in datasheet.R.
    """
    n = (ds.get("counterbalancing") or {}).get("versions")
    if not n or n < 2:
        return ""
    unit = ("presentation versions (one list of one item set)" if ds.get("resampling")
            else "lists")
    return (f" Each participant was presented one of the {n} {unit}, assigned in rotation "
            "by participant number.")


def _trial_order_note(ds: dict) -> str:
    """The trial orders and the run limit, for the Methods text.

    Empty for a design with one order and no limit, and for a record written before
    the fields existed. Mirrors .trial_order_note in datasheet.R.
    """
    cb = ds.get("counterbalancing") or {}
    out = ""
    orders = cb.get("orders")
    if orders:
        out += (f" Each list was presented in {orders['m']} trial orders, assigned in "
                "rotation by participant number.")
    limit = cb.get("max_run")
    if limit:
        what = ("condition" if limit["run_on"] == "condition"
                else f"value of {limit['run_on']}")
        out += (f" Runs of consecutive trials with the same {what} were limited to "
                f"{limit['k']} (van Casteren & Davis, 2006).")
    return out


def _num(v):
    try:
        return None if v is None or v != v else _round_dp(float(v), 4)
    except (TypeError, ValueError):
        return None


def _fmt_tost_p(p) -> str:
    """The TOST p as the Markdown shows it.

    Four places, the precision the comparisons report stores, through _fmt_dp like
    every other number. It was printed raw, so this engine wrote 0.0009 and 1.0 where
    R wrote 9e-04 and 1. A p that rounds to zero at four places is shown as the bound
    it is below. Mirrors .fmt_tost_p in datasheet.R.
    """
    s = _fmt_dp(p, 4)
    return "< 0.0001" if s == "0.0000" else s


def _bool(v):
    return None if v is None or (isinstance(v, float) and v != v) else bool(v)


def _norms_note(ds: dict) -> str:
    """The norm tables named in the Methods prose.

    Basenames only: the full paths and checksums are in the datasheet, and a paper's
    Methods section wants the source, not the directory it happened to sit in on one
    machine. Mirrors .norms_note in datasheet.R.
    """
    norms = (ds.get("materials_source") or {}).get("norms")
    if not norms:
        return ""
    files = ", ".join(str(t["path"]).replace("\\", "/").rsplit("/", 1)[-1] for t in norms)
    return (" Norm dimensions were joined from %s, whose checksums and per-column "
            "coverage are recorded in the datasheet." % files)


def _known_forms_note(ds: dict) -> str:
    """The known-form lists a generated design checked its pseudowords against, for the
    Methods prose, by basename like the norm tables. Empty when it named none. Mirrors
    .known_forms_note in datasheet.R.
    """
    recs = (ds.get("selection") or {}).get("generation_exclude") or []
    if not recs:
        return ""
    parts = ["%d known word form%s (%s)"
             % (r["n_forms"], "" if r["n_forms"] == 1 else "s",
                str(r["source"]).replace("\\", "/").rsplit("/", 1)[-1]) for r in recs]
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return ". Besides the lexicon, pseudowords were checked against " + listed


def _exclusions_note(ds: dict) -> str:
    """The design's exclusion list, for the Methods prose: how many candidates it
    removed, and its file by name like the norm tables. A sentence without its final
    full stop, or empty without a list. Mirrors .exclusions_note in datasheet.R.
    """
    ex = (ds.get("materials_source") or {}).get("exclusions")
    if not ex:
        return ""
    n = int(ex["n_removed"])
    where = ("in the design" if ex["path"] == "inline"
             else "(%s)" % _file_name(ex["path"]))
    return ("An exclusion list %s removed %d word%s from the candidates before selection"
            % (where, n, "" if n == 1 else "s"))


def _recipe_label(cb: dict) -> str:
    """The counterbalancing recipe as the Methods text names it.

    A Latin square the check found incomplete is called incomplete, since the bare
    label would claim a rotation the lists or the item sets did not complete. A
    record without the check, written before datasheet 1.2, keeps the bare label.
    Mirrors .recipe_label in datasheet.R.
    """
    if cb["recipe"] == "latin_square_target":
        return ("an incomplete Latin-square rotation" if cb.get("complete") is False
                else "a Latin-square rotation")
    return {"factorial": "a factorial split"}.get(cb["recipe"], cb["recipe"])


def _ci_pct(alpha) -> str:
    """The confidence level of the interval beside a TOST at ``alpha``, 1 - 2 * alpha,
    as a percentage: "90" at .05 and "99" at .005. The text and the table said 90%
    whatever the schema's alpha. Mirrors .ci_pct in datasheet.R."""
    return _fmt_g((1 - 2 * float(alpha)) * 100)


def _tost_min_n(bound_d, alpha):
    """The fewest items per condition with which two one-sided tests at ``bound_d`` and
    ``alpha`` can support equivalence, infinity when no request either engine accepts
    would do, or None for a bound or an alpha that admits none.

    Two conditions of n items with equal means give the test its best case, a t of
    bound_d / sqrt(2 / n) on 2n - 2 degrees of freedom, which passes when it exceeds
    t(1 - alpha, 2n - 2). The fewest items with which a dimension that varies can pass
    is therefore the smallest n with t(1 - alpha, 2n - 2) * sqrt(2 / n) < bound_d: 23 at
    a bound of 0.5 and an alpha of .05. The left side falls as n grows, so the search
    doubles n until the test can pass and then bisects, ``lo`` never passing and ``hi``
    always passing. It stops at the largest n_per_condition the engines accept, where
    R's integers end. Without that stop, a bound below about 5e-5 SD gave R an NA, which
    stopped its Methods text, and a smaller one a bisection that never ended, because
    doubles that large cannot hold the midpoint. Mirrors .tost_min_n in datasheet.R.
    """
    try:
        bound, a = float(bound_d), float(alpha)
    except (TypeError, ValueError):
        return None
    if not (bound > 0 and 0 < a < 0.5):
        return None

    def passes(n):
        return stats.t.ppf(1 - a, 2 * n - 2) * math.sqrt(2 / n) < bound

    # One item leaves the test no degrees of freedom, so 1 is the first n that fails.
    lo, hi = 1, 2
    while not passes(hi):
        if hi >= _INT_MAX:
            return math.inf
        lo, hi = hi, min(2 * hi, _INT_MAX)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if passes(mid):
            hi = mid
        else:
            lo = mid
    return hi


def _int_text(v) -> str:
    """A count as the Methods text prints it, or "NA" when there is none. Mirrors
    .int_text in datasheet.R."""
    return "NA" if v is None or v != v else "%d" % int(v)


def _realised_range(ds) -> tuple:
    """The fewest and the most items a condition holds, from
    ``items.n_per_condition_realised``, or the request twice for a record written before
    that field existed. Mirrors .realised_range in datasheet.R."""
    recs = (ds.get("items") or {}).get("n_per_condition_realised")
    if recs:
        ns = [int(r["n"]) for r in recs]
        return min(ns), max(ns)
    n = (ds.get("design") or {}).get("n_per_condition")
    return n, n


def _pooled_counts(ds) -> list:
    """The items each condition holds over every replicate, the samples its equivalence
    tests compared, or the request for a record without the realised counts. Mirrors
    .pooled_counts in datasheet.R."""
    recs = (ds.get("items") or {}).get("n_per_condition_realised")
    if recs:
        totals = {}
        for r in recs:
            totals[str(r["condition"])] = totals.get(str(r["condition"]), 0) + int(r["n"])
        return list(totals.values())
    n = (ds.get("design") or {}).get("n_per_condition")
    return [n] if isinstance(n, (int, float)) and not isinstance(n, bool) else []


def _count_text(lo, hi, noun) -> str:
    """A count, or a range when the conditions differ, with its noun: "1 item",
    "15 items", "18 to 20 items". Mirrors .count_text in datasheet.R."""
    count = (_int_text(lo) + " to " + _int_text(hi)) if lo != hi else _int_text(lo)
    return count + " " + noun + ("" if hi == 1 else "s")


def _requested_note(ds, lo) -> str:
    """The request, as " (of 20 requested)", when the conditions hold fewer items than
    the design asked for, which only ``shortfall: allow`` lets a run do. Empty
    otherwise. Mirrors .requested_note in datasheet.R."""
    req = (ds.get("design") or {}).get("n_per_condition")
    if (not (ds.get("items") or {}).get("n_per_condition_realised") or lo is None
            or not isinstance(req, (int, float)) or isinstance(req, bool) or lo >= req):
        return ""
    return " (of %d requested)" % int(req)


def _unit(ds, dim) -> str:
    """A dimension's unit as the Methods text gives it: the schema's unit, which the
    record's ``dimensions`` carry, less a closing parenthesis such as "(orthographic
    estimate)". Empty for a dimension the record gives no unit, such as a joined norm.
    Mirrors .unit in datasheet.R."""
    unit = (((ds.get("dimensions") or {}).get(dim)) or {}).get("unit")
    if not isinstance(unit, str):
        return ""
    return re.sub(r" *\([^()]*\)$", "", unit)


def _defined(row) -> bool:
    d = row.get("cohens_d")
    return d is not None and d == d


def _raw_text(ds, row) -> str:
    """A row's raw difference in its unit, or empty when the row has none.

    The comparisons store the difference to three places, so a bigram probability,
    whose differences lie in the fourth, can be stored as 0 beside a d that is not. That
    zero is a rounding residue and is given as "under 0.001". Mirrors .raw_text in
    datasheet.R.
    """
    v = row.get("mean_diff")
    if v is None or v != v:
        return ""
    text = _fmt_dp(v, 3)
    if text == "0.000" and _defined(row) and row["cohens_d"] != 0:
        text = "under 0.001"
    unit = _unit(ds, row["dimension"])
    return text + (" " + unit if unit else "")


def _pair_text(row) -> str:
    """The pair a row compares, the reference first, since d and the raw difference are
    the reference mean minus the condition mean. Empty for a record without the pair."""
    ref, cond = row.get("reference"), row.get("condition")
    return "" if ref is None or cond is None else "%s against %s" % (ref, cond)


def _d_text(row, pct) -> str:
    return "d = %s, %s%% CI [%s, %s]" % (_fmt_dp(row["cohens_d"], 2), pct,
                                         _fmt_dp(row.get("ci_low"), 2),
                                         _fmt_dp(row.get("ci_high"), 2))


# The names a lexical decision's Methods sentence gives the dimensions its report sets
# words against pseudowords on. Kept identical to .LEXDEC_NAMES in datasheet.R.
_LEXDEC_NAMES = {"bigram_freq": "bigram frequency", "n_density": "N", "old20": "OLD20"}


def _control_note(ds) -> str:
    """What the Methods text says about the realised control of a matched or generated
    design, as sentences each beginning with ". ".

    The description comes first. A matched design gives the largest difference on a
    matched dimension, in that dimension's unit, with its pair, d and interval. Raw
    differences in different units cannot be ranked against each other, so the largest
    is the one with the largest |d|. A generated lexical decision says that its words
    and pseudowords were matched on length only, and how they differ on the dimensions
    the generator does not hold. Comparisons whose d is undefined are counted. The two
    one-sided tests follow as a secondary check, with the number they passed, and say
    so when every condition holds fewer items than any test at the bound can pass with.
    A matched design then names, largest first, up to five comparisons of a dimension it
    did not control whose |d| exceeds the bound, or says that none does. Tests on a
    selected set describe a closed population, so the stimuli are described first
    (Sassenhagen & Alday, 2016). Mirrors .control_note in datasheet.R.
    """
    rows = ds.get("realised_control") or []
    eq = ds.get("equivalence") or {}
    bound, alpha = eq.get("bound_d", 0.5), eq.get("alpha", 0.05)
    pct = _ci_pct(alpha)
    ctrl = [r for r in rows if r.get("role") == "controlled"]
    unc = [r for r in rows if r.get("role") == "uncontrolled"]
    generated = (ds.get("materials_source") or {}).get("type") == "generate"
    out = ""
    if generated:
        parts = ["%s (%s)" % (_LEXDEC_NAMES.get(r["dimension"], r["dimension"]),
                              _d_text(r, pct) if _defined(r) else "d undefined")
                 for r in unc]
        out += ". Words and pseudowords were matched on length only"
        if parts:
            out += ", and the words differed from the pseudowords in " + _and_join(parts)
    else:
        known = [r for r in ctrl if _defined(r)]
        if known:
            # max() keeps the first of equal |d|, as R's which.max() does.
            worst = max(known, key=lambda r: abs(r["cohens_d"]))
            raw = _raw_text(ds, worst)
            inner = "; ".join(x for x in (_pair_text(worst), _d_text(worst, pct)) if x)
            out += ". The largest difference on a matched dimension was %s%s (%s)" % (
                raw + " in " if raw else "in ", worst["dimension"], inner)
    undefined = [r for r in ctrl if not _defined(r)]
    if undefined:
        share = ("every matched comparison" if len(undefined) == len(ctrl)
                 else "%d of the %d matched comparisons" % (len(undefined), len(ctrl)))
        out += (". Cohen's d is undefined for %s, and the realised-control table gives "
                "their raw differences" % share)
    if ctrl:
        passed = sum(1 for r in ctrl if r.get("equivalent") is True)
        out += (". Two one-sided tests at a bound of %s SD (alpha %s) supported equivalence "
                "on %d of %d matched comparisons" % (_fmt_g(bound), _fmt_g(alpha), passed,
                                                    len(ctrl)))
        counts = _pooled_counts(ds)
        n_min = _tost_min_n(bound, alpha)
        if counts and n_min is not None and max(counts) < n_min:
            out += ("; with %s per condition no dimension that varies can pass this test, "
                    "however well matched" % _count_text(min(counts), max(counts), "item"))
    if not generated and unc:
        # A stable sort, so comparisons of equal |d| keep the record's order.
        big = sorted((r for r in unc if _defined(r) and abs(r["cohens_d"]) > bound),
                     key=lambda r: -abs(r["cohens_d"]))
        if big:
            parts = []
            for r in big[:5]:
                head = ": ".join(x for x in (_pair_text(r), _raw_text(ds, r)) if x)
                inner = "; ".join(x for x in (head, _d_text(r, pct)) if x)
                parts.append("%s (%s)" % (r["dimension"], inner))
            out += ". Dimensions the design did not control differed: " + _and_join(parts)
            if len(big) > 5:
                out += ", and %d more in the realised-control table" % (len(big) - 5)
        elif all(_defined(r) for r in unc):
            out += ". No uncontrolled dimension differed by more than %s SD" % _fmt_g(bound)
    return out


def _spread_note(rows) -> str:
    """The predictor's realised span and SD, the SD set against an even spread over the
    span, in parentheses, or empty for a record without them. Mirrors .spread_note in
    datasheet.R."""
    span = next((r.get("predictor_span") for r in rows
                 if r.get("predictor_span") is not None), None)
    pred = next((r for r in rows if r.get("role") == "predictor"), {})
    parts = []
    if span is not None:
        parts.append("a span of " + _fmt_dp(span, 2))
    if pred.get("sd") is not None:
        sd = "an SD of " + _fmt_dp(pred["sd"], 2)
        if pred.get("sd_ratio") is not None:
            sd += ", %s times that of an even spread over the span" % _fmt_dp(pred["sd_ratio"], 2)
        parts.append(sd)
    return " (%s)" % " and ".join(parts) if parts else ""


def _bands_note(ds, rows) -> str:
    """A continuous design's control windows, the rule that set them and the realised
    SDs, as a sentence, or how the windows were widened when they held too few items.

    The windows are the mean +/- k SD of the controls in a first selection spread over
    the predictor's ranks, k from the resolved tolerance_k with the matcher's default of
    2, and each realised SD is set against the pool's. That first selection follows the
    pool's distribution of the predictor, so it is not called an even spread, the phrase
    the text keeps for values spaced evenly over the span. The text used to call the
    controls near-constant, though the windows only trim their tails and a relaxation
    drops them. Mirrors .bands_note in datasheet.R.
    """
    sel = ds.get("selection") or {}
    controls = list(sel.get("controls") or [])
    if not controls:
        return ""
    tol = sel.get("tolerance_k") or {}
    ks = [tol.get(c, 2) for c in controls]
    same_k = all(k == ks[0] for k in ks)
    by = {r.get("dimension"): r for r in rows if r.get("role") == "control"}
    windows = []
    for c, k in zip(controls, ks, strict=True):
        r = by.get(c) or {}
        if r.get("window_low") is None or r.get("window_high") is None:
            continue
        windows.append("%s %s to %s%s" % (c, _fmt_dp(r["window_low"], 2),
                                          _fmt_dp(r["window_high"], 2),
                                          "" if same_k else " at k = " + _fmt_g(k)))
    ratios = [(by.get(c) or {}).get("sd_ratio") for c in controls]
    many = len(controls) > 1
    rule = "the mean \u00b1 %s SD of an initial selection spread over the ranks of %s" % (
        _fmt_g(ks[0]) if same_k else "k", sel.get("predictor"))
    win = " (%s)" % _and_join(windows) if windows else ""
    sds = ""
    if all(x is not None for x in ratios):
        sds = ", and %s %s of the pool's" % (
            "their realised SDs were" if many else "its realised SD was",
            _and_join(_fmt_dp(x, 2) for x in ratios))
    if sel.get("window_relaxations"):
        return " The control %s, %s%s, held too few items and %s widened to the whole pool%s." % (
            "windows" if many else "window", rule, win, "were" if many else "was", sds)
    return " The %s banded within %s of %s%s%s." % (
        "controls were" if many else "control was", "windows" if many else "a window", rule,
        win, sds)


def methods_paragraph(ds: dict) -> str:
    """A ready-to-adapt Methods paragraph rendered from a datasheet.

    Every number in the paragraph is printed by lexsync's own formatter, rounded
    half away from zero from the value the datasheet stores, so the R and Python
    engines write the same text from the same record, a record read back from its
    JSON included.

    It states the items each condition holds, and the request beside them when they
    fell short of it. The realised control is described before it is tested: the
    largest difference on a matched dimension in that dimension's unit, with d and its
    interval, then the equivalence tests, then, largest first, up to five comparisons of
    an uncontrolled dimension whose |d| exceeds the bound (see _control_note). Every
    interval is labelled by the schema's alpha. A continuous design gives the predictor's
    spread and the control windows (see _bands_note). When a response mapping applies, it
    says which key the participants pressed for which condition (see _mapping_note).
    Mirrors methods_paragraph in datasheet.R.
    """
    d = ds["design"]
    src = ds["materials_source"]["type"]
    lang = d["language"].capitalize()
    sel = ds.get("selection") or {}
    lo, hi = _realised_range(ds)
    n = (_int_text(lo) + " to " + _int_text(hi)) if lo != hi else _int_text(lo)
    one = hi == 1
    were = "was" if one else "were"
    req = _requested_note(ds, lo)
    # What was selected. A pair design's unit is the pair, and its `n_per_condition`
    # counts pairs, so calling them "items" would misreport the size of the materials
    # by a factor of the number of conditions.
    rel = ds.get("relational")
    unit = ("item" if not rel else "-".join(rel["members"]) + " pair") + ("" if one else "s")
    if "predictor" in sel:
        predictor = sel["predictor"]
        rc = ds.get("realised_control") or []
        rs = [abs(r["pearson_r"]) for r in rc
              if r.get("pearson_r") is not None and r["pearson_r"] == r["pearson_r"]]
        # |r| is printed at three places, the precision of the comparisons report it
        # comes from (the record keeps up to four, see _num), so the record holds the
        # digit shown. _fmt_dp prints it, as every number here, because R's sprintf()
        # rounds a tie such as 0.0825 to 0.082 on Windows where this engine gives 0.083.
        corr_str = (" The largest predictor-control correlation was |r| = "
                    + _fmt_dp(max(rs), 3) + "." if rs else "")
        cb = ds["counterbalancing"]
        recipe_label = _recipe_label(cb)
        excluded = _exclusions_note(ds)
        excluded = " " + excluded + "." if excluded else ""
        return (f"{n} {lang} {unit}{req} {were} selected to span {predictor}{_spread_note(rc)}, "
                f"for analysis by regression or a mixed model rather than a between-condition "
                f"contrast (Kuperman, 2015; Liben-Nowell et al., 2019)."
                f"{_bands_note(ds, rc)}{corr_str}{_norms_note(ds)}{excluded} Materials were "
                f"counterbalanced into {cb['lists']} list(s) ({recipe_label}) and generated "
                f"for PsychoPy, OpenSesame and jsPsych.{_versions_note(ds)}"
                f"{_trial_order_note(ds)}{_response_note(ds)}"
                f"{_mapping_note(ds)} The selection is deterministic and reproducible (lexsync "
                f"{ds['reproducibility']['versions']['lexsync']}), and the seed "
                f"({ds['reproducibility']['seed']}) fixes the trial order.")
    items = "item" if one else "items"
    if src == "corpus":
        ctrl = ", ".join(ds["selection"]["match_on"]) or "the control dimensions"
        lead = (f"{n} {items} per condition{req} {were} selected from the {lang} lexicon "
                f"({ds['materials_source']['provenance']}) and matched item by item on "
                f"{ctrl} using lexsync's {ds['selection']['method']} matcher")
    elif src == "pool":
        # A supplied pool is matched exactly as a corpus is; what differs, and what the
        # Methods section has to say, is that the candidate words were chosen by the
        # researcher rather than drawn from the whole lexicon.
        ctrl = ", ".join(ds["selection"]["match_on"]) or "the control dimensions"
        lead = (f"{n} {lang} {items} per condition{req} {were} selected from a supplied "
                f"candidate pool and matched item by item on {ctrl} using lexsync's "
                f"{ds['selection']['method']} matcher, with the matched dimensions taken "
                f"from {ds['materials_source']['dimensions_from']}")
    elif src == "generate":
        lead = (f"{n} real {lang} {'word' if one else 'words'}{req} and {n} length-matched "
                f"{'pseudoword' if one else 'pseudowords'} (generated by "
                f"{ds['selection']['method']}) were assembled for a lexical-decision "
                f"contrast{_known_forms_note(ds)}")
    else:
        # An item table selects nothing, so it has the items it holds and no request. A
        # record written before the realised counts existed divides its rows.
        if not (ds.get("items") or {}).get("n_per_condition_realised"):
            lo = hi = ds["items"]["n_total"] // max(1, ds["items"]["n_conditions"])
        lead = ("%s drawn from an item table for a %s design (%s)"
                % (_count_text(lo, hi, "item") + (" was" if hi == 1 else " were"),
                   d["paradigm"], lang))
    control = _control_note(ds)
    rs = ds.get("resampling")
    resamp = (f". {rs['n_sets']} disjoint matched item sets were drawn, so items can be "
              f"treated as a random factor" if rs else "")
    cb = ds["counterbalancing"]
    recipe_label = _recipe_label(cb)
    tail = (resamp + f". Materials were counterbalanced into {cb['lists']} list(s) "
            f"({recipe_label}) and generated for PsychoPy, OpenSesame and "
            f"jsPsych.{_versions_note(ds)}{_trial_order_note(ds)}{_response_note(ds)}"
            f"{_mapping_note(ds)} The "
            f"selection is deterministic and reproducible (lexsync "
            f"{ds['reproducibility']['versions']['lexsync']}), and the seed "
            f"({ds['reproducibility']['seed']}) fixes the trial order.")
    cp = (ds.get("selection") or {}).get("candidate_pool")
    # The candidate pool counts the candidates excluded for a missing matched value,
    # which were never eligible, so they come off the count of the condition that
    # lost them. Mirrors methods_paragraph in datasheet.R.
    lost = {}
    for d in (ds.get("selection") or {}).get("incomplete_dropped") or []:
        lost[d["condition"]] = lost.get(d["condition"], 0) + int(d["n"])
    pool_note = ""
    if cp:
        sizes = [c["n_candidates"] - lost.get(c.get("condition"), 0) for c in cp
                 if c.get("n_candidates") is not None]
        if sizes:
            pool_note = (f". The smallest condition was selected from {min(sizes)} "
                         "eligible candidates, and the selection was deterministic and "
                         "blind to any outcome measure")
    cap_rec = (ds.get("selection") or {}).get("candidate_cap")
    cap_note = ""
    if cap_rec and any(cap_rec.get("applied", {}).values()):
        cap_note = (f". Each candidate pool exceeding the pairwise cap was reduced to "
                    f"the {int(cap_rec['cap'])} candidates nearest the other "
                    f"condition's centroid before pairing")
    ce_note = ""
    if str((ds.get("selection") or {}).get("cross_engine", "")).startswith("approximate"):
        ce_note = (". This design's matching method uses a covariance inverse or an "
                   "assignment solver, so the R and Python engines select equivalent "
                   "but not byte-identical materials")
    bal = (ds.get("counterbalancing") or {}).get("optimise")
    bal_note = "" if not bal else (
        ". Item sets were assigned to lists so as to equate the lists on %s rather than "
        "by an arbitrary deal, by a deterministic integer search (%d swap(s); imbalance "
        "reduced from %d to %d)"
        % (", ".join(bal["dimensions"]), bal["n_swaps"],
           bal["cost_before"], bal["cost_after"]))
    # Placed before the pool size, which it shrank.
    excluded = _exclusions_note(ds)
    excluded = ". " + excluded if excluded else ""
    return (lead + control + excluded + pool_note + cap_note + ce_note + bal_note + tail
            + _norms_note(ds))


def prereg_template(ds: dict) -> str:
    return (
        "## Pre-registration template\n\n"
        "*Auto-generated by lexsync. The Materials section is filled from the datasheet; "
        "complete the remaining sections before data collection.*\n\n"
        "### Study information\n- Title:\n- Authors:\n- Research questions:\n\n"
        "### Hypotheses\n- H1:\n\n"
        "### Design\n- Manipulated variable(s):\n- Measured variable(s):\n"
        f"- Paradigm: {ds['design']['paradigm']}\n\n"
        "### Materials (from the lexsync datasheet)\n" + methods_paragraph(ds) + "\n\n"
        "### Sampling plan\n- Sample size and justification:\n- Stopping rule:\n\n"
        "### Analysis plan\n- Statistical model: "
        + ds["analysis"]["suggested_model"] + "\n  (" + ds["analysis"]["note"] + ")\n"
        "- Inference criteria:\n"
        "- Treatment of items (e.g. items as a random factor):\n"
    )


def _transparency_note(ds: dict) -> str:
    """How the selection was made, as the Markdown's transparency section states it.

    Selection reads no seed, so the note names what it does depend on, and how exact
    ties were broken when the record gives the rule. It used to call the selection
    deterministic given the seed and free of item-selection bias, though the
    spelling tie-break skewed tied conditions towards early-alphabet words. Mirrors
    .transparency_note in datasheet.R.
    """
    rule = ((ds.get("selection") or {}).get("tie_break") or {}).get("rule")
    if rule == "hash":
        ties = (" Exact ties between equally close candidates are broken by a keyed hash "
                "of each word (salt %s), so no part of the alphabet is favoured."
                % ds["selection"]["tie_break"]["salt"])
    elif rule == "bytes":
        ties = (" Exact ties between equally close candidates are broken by spelling, in "
                "byte order, as lexsync 0.1 did, so every tie goes to the spelling that "
                "sorts first.")
    else:
        ties = ""
    return ("Selection is a deterministic function of the materials source, the design "
            "and the schema, blind to any outcome measure, and does not depend on the "
            "seed, which fixes the trial order." + ties + " Automating the choice "
            "removes the experimenter's discretion that Forster (2000) showed can bias "
            "item selection.")


def render_datasheet_md(ds: dict) -> str:
    d = ds["design"]
    lines = [f"# Materials datasheet — {d['name']} ({d['language']})", "",
             f"*lexsync datasheet v{ds['lexsync_datasheet_version']}; "
             f"{ds['reproducibility']['versions']['engine']} engine.*", "",
             "## Provenance", "",
             f"- **Paradigm:** {d['paradigm']}  |  **Item source:** {d['source']}",
             f"- **Description:** {d.get('description') or '--'}",
             f"- **Materials source:** `{ds['materials_source']['path']}` "
             f"(sha256 `{(ds['materials_source']['sha256'] or '')[:16]}…`)"]
    # Where a supplied pool's matched values came from. Without this the record names
    # only the word list, and the numbers every control rests on have no stated origin.
    # Appended here rather than inserted at an index, so the position stays right if a
    # line above it is ever added or removed.
    dim_from = (ds.get("materials_source") or {}).get("dimensions_from")
    if dim_from:
        dim_sha = (ds.get("materials_source") or {}).get("dimensions_sha256")
        lines.append("- **Dimensions from:** `%s`%s"
                     % (dim_from, "" if not dim_sha else " (sha256 `%s…`)" % dim_sha[:16]))
    # The design's exclusion list, which decided what the selection could draw on.
    ex = (ds.get("materials_source") or {}).get("exclusions")
    if ex:
        n_listed = int(ex["n_listed"])
        lines.append("- **Excluded words:** %s (%d word%s, %d removed, sha256 `%s…`)"
                     % ("the design's list" if ex["path"] == "inline" else "`%s`" % ex["path"],
                        n_listed, "" if n_listed == 1 else "s", int(ex["n_removed"]),
                        (ex.get("sha256") or "")[:16]))
    nfc = (ds.get("materials_source") or {}).get("input_normalisation")
    if nfc:
        lines.append("- **Input normalisation:** %d text form(s) rewritten to Unicode NFC, "
                     "%d duplicate(s) removed" % (nfc["changed"], nfc["collapsed"]))
    zd = (ds.get("materials_source") or {}).get("zipf_derivation")
    if zd:
        lines.append("- **Zipf from frequencies per million:** %d of %d value(s) within 1e-9 "
                     "of a rounding boundary" % (zd["near_boundary"], zd["n_values"]))
    # The known-form lists a generated design's pseudowords were checked against: they
    # decide which pseudowords the run produced, as the lexicon does.
    for r in (ds.get("selection") or {}).get("generation_exclude") or []:
        lines.append("- **Known word forms:** `%s` (%d forms, sha256 `%s…`)"
                     % (r["source"], r["n_forms"], (r.get("sha256") or "")[:16]))
    lines += [
        f"- **Selection:** {ds['selection']['method']}",
        f"- **Cross-engine determinism:** {ds['selection'].get('cross_engine', 'byte-identical')}",
        f"- **Counterbalancing:** {ds['counterbalancing']['recipe']}, "
        f"{ds['counterbalancing']['lists']} list(s)"]
    # Said only where there is a choice to make, so a single-version record reads as
    # it always has.
    if (ds["counterbalancing"].get("versions") or 1) > 1:
        lines.append(f"- **Presentation versions:** {ds['counterbalancing']['versions']}, "
                     f"assigned as {ds['counterbalancing']['assignment']}")
    orders = ds["counterbalancing"].get("orders")
    if orders:
        lines.append(f"- **Trial orders:** {orders['m']} per list, assigned as "
                     f"{orders['rule']}")
    limit = ds["counterbalancing"].get("max_run")
    if limit:
        realised = max((r["longest_run"] for r in limit["longest"]), default=0)
        lines.append(f"- **Run limit:** at most {limit['k']} consecutive trials with the "
                     f"same `{limit['run_on']}` (longest realised: {realised})")
    lines += [
        f"- **Items:** {ds['items']['n_total']} rows across "
        f"{ds['items']['n_conditions']} conditions "
        f"({', '.join(ds['items']['conditions'])})",
        f"- **Seed:** {ds['reproducibility']['seed']}  |  **Versions:** "
        + ", ".join(f"{k} {v}" for k, v in ds["reproducibility"]["versions"].items()), ""]
    # Norm tables, with their checksums and coverage. A dimension covering only part of
    # the lexicon matters to a reader: the uncovered rows carry NaN and are dropped by
    # the tolerance windows, so coverage is part of how the pool was defined.
    nrm = (ds.get("materials_source") or {}).get("norms")
    if nrm:
        lines += ["## Joined norms", "",
                  "| File | Key | Column | Coverage | sha256 |", "|---|---|---|---|---|"]
        for t in nrm:
            for cl in t["columns"]:
                lines.append(f"| `{t['path']}` | {t['on']} | {cl['column']} | "
                             f"{cl['n_matched']} / {cl['n_total']} | "
                             f"`{(t.get('sha256') or '')[:16]}…` |")
        lines.append("")
    # Balance-aware list assignment. Reported because it decides which items each
    # participant sees, and the before/after costs are what make the claim checkable
    # rather than a bare assertion that the lists are balanced.
    bal = (ds.get("counterbalancing") or {}).get("optimise")
    if bal:
        lines += ["## Balanced list assignment", "",
                  "- **Balanced on:** " + ", ".join(bal["dimensions"]),
                  "- **Imbalance:** %d before, %d after, in %d swap(s)"
                  % (bal["cost_before"], bal["cost_after"], bal["n_swaps"]),
                  "- **Cost unit:** " + bal["cost_unit"],
                  ("- The search stopped at its pass bound rather than at a local "
                   "optimum, so a higher `counterbalance.max_passes` may balance the "
                   "lists further.") if bal.get("max_passes_reached") else
                  ("- The search ran to a local optimum: no single exchange of two item "
                   "sets between lists would reduce the imbalance further."),
                  ("- The search is a deterministic integer descent with a keyed-hash "
                   "tie-break, so it uses no random number generator and the R and "
                   "Python engines produce the same assignment."), ""]
    # The trials each list gives each condition, and whatever leaves a Latin-square
    # rotation incomplete, so a reader can check the rotation against the counts.
    # Mirrors render_datasheet_md in datasheet.R.
    cbk = ds.get("counterbalancing") or {}
    issues = cbk.get("issues") or []
    cells = cbk.get("cells") or []
    if issues or cells:
        lines += ["## Counterbalanced lists", ""]
        if issues:
            lines += ["- **Incomplete rotation:** " + issue for issue in issues] + [""]
        if cells:
            with_rep = any("replicate" in c for c in cells)
            lines += (["| Replicate | List | Condition | Trials |", "|---|---|---|---|"]
                      if with_rep else ["| List | Condition | Trials |", "|---|---|---|"])
            lines += [("| %s | " % c["replicate"] if with_rep else "| ")
                      + "%s | %s | %s |" % (c["list"], c["condition"], c["n_trials"])
                      for c in cells] + [""]
    rel = ds.get("relational")
    if rel:
        lines += ["## Pair-keyed items", "",
                  f"- **Members:** {', '.join(rel['members'])}  |  "
                  f"**Pairs:** {rel['n_pairs']}",
                  f"- **Member lexicon:** `{rel['member_lexicon']}` "
                  f"(sha256 `{(rel.get('member_lexicon_sha256') or '')[:16]}…`)",
                  "- **Member-level dimensions** (one word): "
                  + ", ".join(rel["member_dimensions"]),
                  "- **Relational dimensions** (the pair): "
                  + ", ".join(rel["relational_dimensions"]),
                  "- Selection ran on one row per pair and the result was re-expanded, so "
                  "every condition row of every chosen pair is present.", ""]
    cp = (ds.get("selection") or {}).get("candidate_pool")
    if cp:
        parts = ", ".join(f"{c['condition']}: {c['n_candidates']}" for c in cp
                          if "condition" in c and "n_candidates" in c)
        lines += ["## Selection transparency", "",
                  "- **Candidate pool** (items satisfying each condition's window before "
                  f"matching): {parts}.",
                  "- " + _transparency_note(ds), ""]
    if ds["realised_control"] and "predictor" in (ds.get("selection") or {}):
        lines += ["## Realised control (continuous predictor)", "",
                  "| Dimension | Role | r with predictor | Predictor span |",
                  "|---|---|---|---|"]
        for r in ds["realised_control"]:
            # A missing value prints "--", not an em dash: the R renderer's
            # placeholder, kept identical.
            lines.append(f"| {r['dimension']} | {r['role']} | "
                         f"{_fmt_dp(r.get('pearson_r'), 3)} | "
                         f"{_fmt_dp(r.get('predictor_span'), 3)} |")
        lines.append("")
    elif ds["realised_control"]:
        # Each row names its pair and gives the raw difference, and the interval is
        # labelled by the schema's alpha: the table said 90% whatever alpha was.
        pct = _ci_pct((ds.get("equivalence") or {}).get("alpha", 0.05))
        lines += ["## Realised control", "",
                  "Each row compares a condition with its reference. The raw difference and "
                  "Cohen's d are the reference mean minus the condition mean, and the "
                  "variance ratio is the condition's variance over the reference's.", "",
                  "| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | "
                  f"{pct}% CI | Var ratio | TOST p | Equivalent |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in ds["realised_control"]:
            # "--", not an em dash: the R renderer's placeholder, kept identical.
            # An undefined d (unequal constants) reaches every one of these cells, and a
            # record written before the pair was recorded reaches the first two. A
            # condition with one item has no TOST verdict either, which printed as None.
            ci = (f"[{_fmt_dp(r['ci_low'], 2)}, {_fmt_dp(r['ci_high'], 2)}]"
                  if r.get("ci_low") is not None else "--")
            pair = [("--" if r.get(k) is None else r[k]) for k in ("condition", "reference")]
            verdict = "--" if r.get("equivalent") is None else r["equivalent"]
            lines.append(f"| {pair[0]} | {pair[1]} | {r['dimension']} | {r['role']} | "
                         f"{_fmt_dp(r.get('mean_diff'), 3)} | {_fmt_dp(r['cohens_d'], 2)} | "
                         f"{ci} | {_fmt_dp(r.get('var_ratio'), 2)} | "
                         f"{_fmt_tost_p(r['tost_p'])} | {verdict} |")
        lines.append("")
    a = ds.get("analysis")
    if a:
        lines += ["## Suggested analysis", "",
                  f"- **Model:** `{a['suggested_model']}` — where the response is "
                  f"{a['response']}.",
                  f"- {a['note']}", ""]
    lines += ["## Methods paragraph", "", methods_paragraph(ds), "", prereg_template(ds)]
    return "\n".join(lines)


def _at_15_significant_digits(o):
    """Round every float in the record to 15 significant digits.

    The R engine writes this JSON with jsonlite, whose numeric precision is a single
    setting for the whole document; 15 significant digits (``digits = NA``) is R's full
    display precision and the closest common ground. Without this the two engines'
    records disagreed on any value that had not already been rounded on the way in.
    A `tolerance_k` of 1/9 was written to 16 digits here and 15 there, so a reader
    diffing the two records saw a difference that meant nothing.

    Fifteen digits is ample for a provenance record: every value in it either came from
    a human-written design file or was deliberately rounded to four places. The design
    file remains the authoritative source for an exact re-run.
    """
    if isinstance(o, float):
        return float("%.15g" % o)
    if isinstance(o, dict):
        return {k: _at_15_significant_digits(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_at_15_significant_digits(v) for v in o]
    return o


def write_datasheet(ds: dict, json_path: str, md_path: str) -> tuple:
    import os
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(_at_15_significant_digits(ds), handle, indent=2, ensure_ascii=False,
                  sort_keys=True)
        handle.write("\n")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_datasheet_md(ds) + "\n")
    return json_path, md_path
