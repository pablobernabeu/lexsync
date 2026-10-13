"""Check a design and its schema before anything is selected or written.

Mirrors R_workflow/R/design.R. A design file is read key by key all over the
package, so a key it misspells is not an error anywhere: ``n_per_conditon: 8``
left the design on the default twenty items per condition and nothing said so.
Metadata were checked only at export, after the stimuli and both reports were on
disk, and a missing ``name`` failed differently in each engine. This module holds
the vocabulary of keys lexsync reads and the checks that ``run_pipeline`` applies
right after reading the configuration, so a design that cannot be honoured is
refused before the output directory is touched, with one message in both engines.

It also resolves the three values that each selector used to resolve by its own
rule: the number of items per condition, the tolerance windows and the file stem
every artefact is named after.
"""
from __future__ import annotations

import hashlib
import math
import numbers
import unicodedata

from rapidfuzz.distance import OSA

from .io_utils import _key_part, clean_meta, clean_port, slugify
from .paradigms import resolve_events

# Every key lexsync reads from a design, as dotted paths. `[]` marks a list whose
# entries are mappings. A key whose value holds names the user chooses is listed
# without children (pool_filters, define_by, tolerance_k, timing, norms,
# response_mapping), so nothing below it is checked here: timing checks its own keys in
# render_events, the keys of a norms entry are checked where the norms are joined, and
# a response mapping is checked against the response event's keys. Seeded from every
# key the shipped designs, both engines, both apps and the tests read. Must list the
# same paths in the same order as .DESIGN_KEYS in R_workflow/R/design.R, and both test
# suites pin a digest of the list.
DESIGN_KEYS = (
    "name", "language", "language_tag", "description", "paradigm", "lexicon",
    "items", "items.source", "items.path", "items.lexicon", "items.members",
    "items.generation", "items.generation.method", "items.generation.exclude",
    "items.anchor_condition",
    "pool_filters",
    "exclude_words", "exclude_words.path",
    "conditions", "conditions[].name", "conditions[].define_by",
    "match_on", "n_per_condition", "n_per_cell",
    "matching", "matching.method", "matching.tolerance_k", "matching.shortfall",
    "matching.on_insufficient_tolerance", "matching.tie_break",
    "resample", "resample.n_sets",
    "counterbalance", "counterbalance.lists", "counterbalance.optimise",
    "counterbalance.balance_on", "counterbalance.max_passes", "counterbalance.recipe",
    "counterbalance.incomplete",
    "continuous", "continuous.predictor", "continuous.controls",
    "norms",
    "events", "events[].type", "events[].content", "events[].duration_ms",
    "events[].duration_frames", "events[].duration", "events[].duration.from_column",
    "events[].duration.jitter", "events[].duration.as", "events[].trigger",
    "events[].onset_locked", "events[].keys", "events[].timeout_ms", "events[].from",
    "events[].advance",
    "events[].sep", "events[].critical_region_trigger", "events[].answer",
    "events[].correct", "events[].incorrect", "events[].no_response", "events[].blocks",
    "timing", "font", "instructions", "response_mapping", "rotate_mapping_by_list",
    "practice", "practice.path",
    "fillers", "fillers.path",
)

# The same for the global schema. `dimensions` holds the dimension names.
SCHEMA_KEYS = (
    "seed",
    "lexicon_schema", "lexicon_schema.required", "lexicon_schema.optional",
    "dimensions",
    "matching", "matching.method", "matching.tolerance_k", "matching.shortfall",
    "matching.on_insufficient_tolerance", "matching.tie_break",
    "equivalence", "equivalence.bound_d", "equivalence.alpha",
    "triggers", "triggers.parallel_address", "triggers.trigger_hold_ms",
    "triggers.reset_after_frames", "triggers.inter_trigger_ms", "triggers.allow_code_overlap",
    "triggers.mode", "triggers.backend", "triggers.serial_port", "triggers.baudrate",
    "presentation", "presentation.font", "presentation.opensesame_font",
    "presentation.assumed_refresh_hz", "presentation.fullscreen",
    "presentation.text_height_px",
    "counterbalance", "counterbalance.incomplete",
)

_N_MESSAGE = "lexsync: n_per_condition must be a positive whole number."
# R's as.integer() gives NA beyond this, so both engines refuse a larger request.
_INT_MAX = 2147483647

# The items per condition each selector takes when a design gives no n_per_condition:
# the matcher (resampled sets included), the continuous selector and the pseudoword
# generator. The datasheet records the request from here too, so the record names the
# n the selector applied. Must stay identical to the .N_DEFAULT_* values in
# R_workflow/R/design.R.
N_DEFAULT_MATCHED = 20
N_DEFAULT_CONTINUOUS = 60
N_DEFAULT_GENERATED = 40


def _key_name(key) -> str:
    """A mapping key as text, spelt as R's YAML reader names it.

    PyYAML keeps a key such as `yes:` as the boolean True, where R names it "TRUE",
    so the two engines would otherwise quote different keys in their messages.
    """
    if isinstance(key, bool):
        return "TRUE" if key else "FALSE"
    return str(key)


def _is_annotation(key: str) -> bool:
    return key == "description" or key.startswith("x_")


def _children(vocabulary, prefix: str) -> list:
    """The keys directly below `prefix` ('' for the top level), in vocabulary order."""
    out = []
    for path in vocabulary:
        if prefix:
            if not path.startswith(prefix + "."):
                continue
            rest = path[len(prefix) + 1:]
        else:
            rest = path
        if "." not in rest:
            out.append(rest)
    return out


def _has_children(vocabulary, prefix: str) -> bool:
    return any(p.startswith(prefix + ".") for p in vocabulary)


def _nearest(key: str, known: list):
    """The known key a typo was probably meant to be, or None.

    One edit is a typo for a known key of up to five characters, two for a longer
    one. The distance is optimal string alignment, Levenshtein's with an adjacent
    transposition counted as one edit, so `nmae` is one edit from `name`. Without the
    shorter limit, `notes`, a natural annotation, would be refused as a misspelling of
    `norms`, two edits away. rapidfuzz here and stringdist's "osa" in the R twin agree
    on these integer distances. Ties go to the earlier key in the vocabulary.
    """
    best, best_d = None, None
    for cand in known:
        d = OSA.distance(key, cand)
        limit = 1 if len(cand) <= 5 else 2
        if d <= limit and (best_d is None or d < best_d):
            best, best_d = cand, d
    return best


def _check_keys(config, vocabulary, kind: str) -> list:
    """Refuse a near-miss key and return a note for every other unknown one.

    The walk follows the document's own key order, so the first near-miss is the one
    reported and the notes come in the order the keys were written. A list entry is
    named by its position counted from 1, as in `events[3].durration`.
    """
    notes: list = []

    def walk(node, vprefix: str, dprefix: str):
        siblings = None
        for raw_key, value in node.items():
            key = _key_name(raw_key)
            if _is_annotation(key):
                continue
            vpath = f"{vprefix}.{key}" if vprefix else key
            dpath = f"{dprefix}.{key}" if dprefix else key
            if vpath in vocabulary:
                if isinstance(value, dict) and _has_children(vocabulary, vpath):
                    walk(value, vpath, dpath)
                elif isinstance(value, list) and _has_children(vocabulary, vpath + "[]"):
                    for i, entry in enumerate(value, start=1):
                        if isinstance(entry, dict):
                            walk(entry, vpath + "[]", "%s[%d]" % (dpath, i))
                continue
            if siblings is None:
                siblings = _children(vocabulary, vprefix)
            near = _nearest(key, siblings)
            if near is not None:
                want = f"{dprefix}.{near}" if dprefix else near
                raise ValueError(f"lexsync: unknown {kind} key '{dpath}' "
                                 f"(did you mean '{want}'?)")
            notes.append(f"lexsync: {kind} key '{dpath}' is not read by lexsync and is "
                         f"ignored; a later release will refuse it. Put annotations in "
                         f"`description` or a key beginning `x_`.")

    if isinstance(config, dict):
        walk(config, "", "")
    return notes


def _shown(value) -> str:
    """A value as the user typed it, near enough to quote back in a message.

    A number that is not finite is shown as R prints it, NaN, Inf or -Inf, and a list in
    brackets, so the two engines quote the same text. _key_part would refuse the first,
    and str() would quote each string of the second. Must match .shown in
    R_workflow/R/design.R.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, numbers.Real):
        if value != value:
            return "NaN"
        if value in (math.inf, -math.inf):
            return "Inf" if value > 0 else "-Inf"
        return _key_part(value)
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_shown(v) for v in value) + "]"
    return str(value)


def _text(design: dict, key: str, hint: str) -> str:
    """A required text value of the design, or a refusal naming the key.

    Only spaces, tabs and line breaks make a value blank, the set R's trimws()
    strips. str.strip() would also strip a no-break space or a vertical tab, and the
    two engines would then refuse a different set of names, with different messages.
    """
    value = design.get(key)
    if value is None or (isinstance(value, str) and not value.strip(" \t\r\n")):
        raise ValueError(f"lexsync: the design has no `{key}`.")
    if not isinstance(value, str):
        raise ValueError(f"lexsync: the design's `{key}` must be text; {hint}")
    return value


def _require_bool(value, key: str):
    """Refuse a value other than true or false for a design key that takes one.

    None passes, since the key may be left out. The engines would read any other value
    differently, R with isTRUE() and this engine by truthiness, so `optimise: n` or `1`
    balanced the lists here only. Must stay identical to .require_bool in
    R_workflow/R/design.R.
    """
    if value is not None and not isinstance(value, bool):
        raise ValueError(f"lexsync: {key} must be true or false.")
    return value


def _name_and_language(design) -> tuple:
    if not isinstance(design, dict):
        raise ValueError("lexsync: a design must be a mapping of keys to values.")
    name = _text(design, "name", "quote it in the design file.")
    language = _text(design, "language", "quote it if it is a code such as 'no'.")
    return name, language


def _resolve_n(design: dict, default):
    """The number of items per condition, by one rule everywhere.

    `n_per_condition`, then `n_per_cell`, then `default`, each taken when it is
    present, not when it is truthy: `or` read a configured 0 as absent and fell
    through to the next key or to the selector's default. A present value must be a
    whole number of at least 1, written as 4 or 4.0, and comes back as an int, which
    numpy's linspace needs. The finiteness test matters: R's trunc(Inf) equals Inf,
    so an infinite request once passed the whole-number test there and selected the
    whole pool. `default` may be None, for a caller that only checks.
    Must stay identical to .resolve_n in R_workflow/R/design.R.
    """
    n = design.get("n_per_condition")
    if n is None:
        n = design.get("n_per_cell")
    if n is None:
        return default
    if (isinstance(n, bool) or not isinstance(n, numbers.Real) or not math.isfinite(n)
            or n < 1 or n != int(n) or n > _INT_MAX):
        raise ValueError(_N_MESSAGE)
    return int(n)


def _resolve_tolerance_k(design: dict, schema: dict) -> dict:
    """The tolerance windows, k per dimension, as R's modifyList() resolves them.

    The schema's map is the base and the design's overrides it per dimension. A null
    in the schema's map is dropped, and a null in the design's deletes that dimension
    from the merged map, so k falls back to the matcher's default of 2. Keeping the
    schema's value instead would make the two engines select differently. The
    nearest-neighbour methods apply these windows. The pairwise `joint` and `optimal`
    methods never consult them, which is why the datasheet attaches this block only
    for the methods that do. Must stay identical to .resolve_tolerance_k in
    R_workflow/R/design.R.
    """
    base = (((schema or {}).get("matching") or {}).get("tolerance_k")) or {}
    over = (((design or {}).get("matching") or {}).get("tolerance_k")) or {}
    tol = {k: v for k, v in base.items() if v is not None} if isinstance(base, dict) else {}
    if isinstance(over, dict):
        for k, v in over.items():
            if v is None:
                tol.pop(k, None)
            else:
                tol[k] = v
    return tol


def _require_match_on(design: dict) -> list:
    """The dimensions a matched design equates its conditions on, or a refusal.

    Without any, every candidate scores distance zero and the tie-break alone picks
    the byte-first words, which the datasheet would still call matched.
    """
    match_on = list(design.get("match_on") or [])
    if not match_on:
        raise ValueError("lexsync: a matched design needs `match_on` naming at least "
                         "one dimension.")
    return match_on


def _names(value) -> list:
    """A design entry that lists names, as a list: a lone name counts as one."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [_key_name(v) for v in value]
    return [_key_name(value)]


def _referenced_dimensions(design: dict) -> list:
    """Every dimension the design names, in first-mention order.

    The names come from ``match_on``, each condition's ``define_by`` keys, the
    ``pool_filters`` keys, the continuous predictor and controls, and
    ``counterbalance.balance_on``, in that order and without repeats. The pipeline
    derives any of ``n_density``, ``old20`` and ``bigram_freq`` in this list that the
    lexicon lacks. Only ``match_on`` used to trigger the derivation, so a design that
    manipulated, filtered on or regressed on a derived dimension stopped with "absent
    from the pool". Must stay identical to .referenced_dimensions in
    R_workflow/R/design.R.
    """
    names = _names(design.get("match_on"))
    for cond in design.get("conditions") or []:
        if isinstance(cond, dict) and isinstance(cond.get("define_by"), dict):
            names += _names(list(cond["define_by"]))
    filters = design.get("pool_filters")
    if isinstance(filters, dict):
        names += _names(list(filters))
    continuous = design.get("continuous")
    if isinstance(continuous, dict):
        names += _names(continuous.get("predictor"))
        names += _names(continuous.get("controls"))
    counterbalance = design.get("counterbalance")
    if isinstance(counterbalance, dict):
        names += _names(counterbalance.get("balance_on"))
    return list(dict.fromkeys(names))


def design_stem(design: dict) -> str:
    """The stem every file a design writes is named after.

    The slug of the design's ``name`` and ``language``, which keeps letters and
    digits only. Two designs whose names differ only outside ASCII (``词频`` and
    ``笔画``, both ``chinese``) would share a slug and overwrite each other's files,
    and an all-Chinese name and language would give no slug at all. Whenever the
    name or the language holds a non-ASCII character, the stem therefore gains ``_``
    and the first eight hexadecimal digits of the SHA-256 of the NFC-normalised UTF-8
    text ``name|language``. An empty slug is replaced by those eight digits. NFC keeps a
    precomposed and a decomposed ``é`` on one stem. A design whose name and language
    hold no letter or digit at all is refused. Mirrors design_stem() in
    R_workflow/R/design.R.

    Parameters
    ----------
    design : dict
        A parsed design configuration.

    Returns
    -------
    str
        The file stem, such as ``en_lexdec_english`` or ``chinese_14aadfa7``.
    """
    name, language = _name_and_language(design)
    name = unicodedata.normalize("NFC", name)
    language = unicodedata.normalize("NFC", language)
    stem = slugify(name, language)
    joined = unicodedata.normalize("NFC", name + "|" + language)
    if not joined.isascii():
        digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:8]
        stem = f"{stem}_{digest}" if stem else digest
    if not stem:
        raise ValueError("lexsync: the design's `name` and `language` hold no letter or "
                         "digit to name its files after; use letters or digits in the "
                         "name.")
    return stem


_EXCLUDE_WORDS_MESSAGE = ("lexsync: exclude_words must be a list of words, or a mapping "
                          "whose `path` names a file of words.")


def _exclude_words(design: dict):
    """The design's `exclude_words`, checked: None, a list of words or {"path": path}.

    A list holds the words themselves, and a lone word is a list of one, as R's YAML
    reader gives `[dog]` and `dog` alike. A mapping names a UTF-8 file with one word
    per line, so a mapping without a `path`, `{}` among them, is refused: R reads `{}`
    as a mapping and `[]` as an empty list, as this engine does. The file is read
    later, by querying._read_exclude_words. A path containing '..' is refused, as for
    the design's other inputs, and so is the key for an item table, whose items are
    the researcher's own and are not filtered. Must stay identical to .exclude_words
    in R_workflow/R/design.R.
    """
    value = design.get("exclude_words")
    if value is None:
        return None
    if (design.get("items") or {}).get("source", "corpus") == "table":
        raise ValueError("lexsync: exclude_words has no effect for items.source 'table'; "
                         "leave the words out of the item table instead.")
    if isinstance(value, dict):
        path = value.get("path")
        if not isinstance(path, str) or not path.strip(" \t\r\n"):
            raise ValueError(_EXCLUDE_WORDS_MESSAGE)
        if ".." in path.replace("\\", "/").split("/"):
            raise ValueError("lexsync: exclude_words path must not contain '..'.")
        return {"path": path}
    words = [value] if isinstance(value, str) else value
    if not isinstance(words, list) or not all(isinstance(w, str) for w in words):
        raise ValueError(_EXCLUDE_WORDS_MESSAGE)
    return list(words)


def _check_conditions(design: dict) -> None:
    conds = design.get("conditions")
    if conds is None:
        return
    if not isinstance(conds, list):
        raise ValueError("lexsync: every entry under `conditions` needs a `name`.")
    names = []
    for cond in conds:
        if not isinstance(cond, dict) or cond.get("name") is None:
            raise ValueError("lexsync: every entry under `conditions` needs a `name`.")
        name = cond["name"]
        if not isinstance(name, str):
            raise ValueError("lexsync: condition names must be text; quote '%s'."
                             % _shown(name))
        names.append(name)
    # The first entry that repeats an earlier name is the one reported, as R's
    # duplicated() finds it, so `a, b, b, a` names 'b' in both engines.
    seen = set()
    for name in names:
        if name in seen:
            raise ValueError(f"lexsync: condition name '{name}' appears more than once; "
                             f"condition names must be unique.")
        seen.add(name)


def validate_design(design: dict, schema: dict) -> list:
    """Check a design and its schema before anything is selected or written.

    ``run_pipeline`` calls this right after reading the two files, so a design that
    cannot be honoured is refused before any output exists, with the same message in
    both engines. It first refuses a key within one or two edits of a key lexsync
    reads at that level, naming the key it was probably meant to be (one edit for a
    known key of up to five characters, two for a longer one). It then refuses a
    missing, empty or non-text ``name`` or ``language``, an ``n_per_condition`` or
    ``n_per_cell`` that is not a whole number of at least 1, and a
    ``counterbalance.optimise`` that is not true or false. It refuses a name,
    language or font that cannot be written into the generated experiments, a
    trigger port that is not an address, and an event list the renderer refuses, such
    as one with an unknown timing key, a bad response key or a response key that
    YAML reads as a boolean (an unquoted ``yes``, ``no``, ``on`` or ``off``). It
    refuses a ``presentation.fullscreen`` that is not true or false and a
    ``presentation.text_height_px`` that is not a whole number from 8 to 400. It
    refuses a ``triggers.mode`` other than ``auto``, ``hardware`` or ``mock``, a
    ``triggers.backend`` other than ``parallel`` or ``serial``, and a
    ``triggers.baudrate`` that is not a positive whole number. A serial backend needs a
    ``triggers.serial_port``, with a name the experiments can carry. Last, it
    refuses a condition without a name, with a name that is not text or with a
    repeated name, a corpus or pool design with conditions but no ``match_on``, and a
    name and language that leave no file stem. It also refuses an ``exclude_words``
    that is neither a list of words nor a mapping whose ``path`` names a file, and one
    that a design with an item table names.

    Any other key lexsync does not read is not refused yet. It is returned as a note,
    which ``run_pipeline`` writes into the run log, and a later release will refuse
    it. ``description`` and keys beginning ``x_`` are annotations and are never
    noted. A schema that still sets ``triggers.inter_trigger_ms``, which no longer
    does anything, gets a note too.

    The experiments' instructions and response mapping are checked here too. It
    refuses ``instructions`` that are not text, are empty or hold a control character
    other than a line break. It refuses a ``response_mapping`` that is not a mapping of
    conditions to single keys, names a key the response event does not allow, or comes
    with no response event. And it refuses a ``rotate_mapping_by_list`` that is not
    true or false, or that has no mapping to rotate.

    Parameters
    ----------
    design : dict
        A parsed design configuration.
    schema : dict
        The parsed global schema.

    Returns
    -------
    list of str
        The notes on unknown keys, in the order the keys were written, then the note
        on ``triggers.inter_trigger_ms``; empty when there are none.
    """
    # Imported here: scripting names its files through design_stem, so a module-level
    # import would be circular.
    from .scripting import (
        _check_instructions_and_mapping,
        _fullscreen,
        _refresh_hz,
        _text_height_px,
        _trigger_settings,
        render_events,
    )

    schema = schema or {}
    if not isinstance(design, dict):
        raise ValueError("lexsync: a design must be a mapping of keys to values.")
    notes = (_check_keys(design, DESIGN_KEYS, "design")
             + _check_keys(schema, SCHEMA_KEYS, "schema"))
    # The key held the self-paced reading critical-region code, which is now held for
    # trigger_hold_ms like every other code. A schema written for an earlier release
    # still sets it, so it is accepted and noted.
    triggers = schema.get("triggers")
    if isinstance(triggers, dict) and triggers.get("inter_trigger_ms") is not None:
        notes.append("lexsync: triggers.inter_trigger_ms is no longer used; the "
                     "self-paced reading critical-region code is held for "
                     "triggers.trigger_hold_ms, as every other code is.")
    _name_and_language(design)
    _resolve_n(design, None)
    counterbalance = design.get("counterbalance")
    if isinstance(counterbalance, dict):
        _require_bool(counterbalance.get("optimise"), "counterbalance.optimise")

    clean_meta(design["name"], "the design's `name`")
    clean_meta(design["language"], "the design's `language`")
    font = design.get("font")
    if font is not None and not isinstance(font, str):
        raise ValueError("lexsync: the design's `font` must be text; quote it in the "
                         "design file.")
    presentation = schema.get("presentation") or {}
    # The PsychoPy and jsPsych targets fall back to presentation.font, OpenSesame to
    # its own font token, so both effective fonts are checked.
    clean_meta(font or presentation.get("font") or "Courier New", "the font")
    clean_meta(font or presentation.get("opensesame_font") or "mono", "the font")
    clean_port((schema.get("triggers") or {}).get("parallel_address", "0x0378"))
    _fullscreen(schema)
    _text_height_px(schema)
    _trigger_settings(schema)
    render_events(resolve_events(design), design.get("timing") or {}, _refresh_hz(schema))
    _check_instructions_and_mapping(design)

    _check_conditions(design)
    _exclude_words(design)
    source = (design.get("items") or {}).get("source", "corpus")
    if (source in ("corpus", "pool") and not design.get("continuous")
            and design.get("conditions")):
        _require_match_on(design)
    design_stem(design)
    return notes
