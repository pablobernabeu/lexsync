"""Practice and filler trials: rows that are PRESENTED but not ANALYSED.

Everything else in the package treats one frame as both the materials record and the
thing the experiment runs. That works only while the two are the same set of trials, and
they usually are not. A practice block exists to settle the participant into the task and
is discarded before analysis; fillers exist to dilute the manipulation so it is less
guessable, and are likewise not analysed. Both have to reach the generated experiment and
neither belongs in the stimuli file, the descriptives or the realised control.

The pipeline therefore splits after counterbalancing: the analysis artefacts are
written from the main rows, and the experiment is generated from the presented rows. A ``block``
column marks which is which, and it appears ONLY when a design declares one of these
blocks -- a design without them keeps exactly the columns it had.

Where each block goes in the sequence is a methodological choice, not a convenience:

Practice comes first, as its own run of trials, because its purpose is to precede the
task. It is ordered within itself by the seeded keyed hash, so every participant given a
list meets the practice items in one fixed order. With ``counterbalance.orders`` each
order of a list has its own practice order, still before the main trials.

Fillers are INTERLEAVED with the main trials, not appended, because a block of fillers at
the end is not a filler -- it is a second block that participants can tell apart. They
are merged into each list before the order is drawn, so one deterministic shuffle mixes
them through. That does renumber the main trials, which is correct: adding fillers
changes the sequence, and the stimuli file records where each item actually appeared.
``counterbalance.max_run`` applies to this interleaved order and, separately, to the
practice order, since a pause separates the two.

Both blocks appear in EVERY list. They are not counterbalanced, because they carry no
manipulation to rotate; every participant should get the same practice. In a resampled
design each replicate's copy of a list is a presentation version of its own, given to
its own participants, so the blocks are added to every (replicate, list) pair, and the
trials are numbered within it.

Mirrors R_workflow/R/blocks.R.
"""
from __future__ import annotations

import pandas as pd

from .counterbalancing import _order_trials, _trial_order_settings, _unit_label
from .io_utils import sha256_file
from .paradigms import required_fields
from .querying import load_items

BLOCK_MAIN = "main"


def _concat_blocks(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Concatenate two block frames that need not have the same columns.

    A filler table carries no ``frequency`` or ``old20``, and the main rows carry no
    filler-specific field; the union is taken and the gaps left missing, which is honest
    -- a filler has no matched frequency because it was never matched.

    The key columns are put back to their original dtypes afterwards. This is not
    cosmetic: pandas promotes an integer column to float the moment a missing value
    enters it, and the trial-order shuffle formats an integer `set` as "3" but a float
    one as "3.0", which would change every digest and every trial order with nothing to
    signal it.
    """
    cols = list(a.columns) + [c for c in b.columns if c not in a.columns]
    dtypes = {c: a[c].dtype for c in a.columns if str(a[c].dtype).startswith("int")}
    dtypes.update({c: b[c].dtype for c in b.columns
                   if c not in dtypes and str(b[c].dtype).startswith("int")})
    out = pd.concat([a.reindex(columns=cols), b.reindex(columns=cols)],
                    ignore_index=True)
    for c, dt in dtypes.items():
        if c in out.columns and out[c].notna().all():
            out[c] = out[c].astype(dt)
    return out


def _load_block(cfg: dict, design: dict, label: str, set_offset: int) -> pd.DataFrame:
    """Read one block's item table and give it a block label and a non-colliding ``set``.

    The offset matters more than it looks. ``load_items`` numbers sets from 1 within
    whatever table it is given, so practice item 1 and main item 1 would both be set 1 --
    and ``set`` is part of the key the trial-order shuffle hashes. Two rows sharing a key
    would be ordered by a coin the package does not own.
    """
    path = cfg.get("path")
    if not path:
        raise ValueError(
            "lexsync: the `%s:` block needs a `path` to an item table." % label)
    items = load_items(path, required_fields(design))
    df = items.copy()
    df["block"] = label
    df["set"] = df["set"].astype(int) + int(set_offset)
    df = df.reset_index(drop=True)
    # Read by add_blocks, which reports it for the run log and the datasheet.
    record = items.attrs.get("input_normalisation")
    if record:
        df.attrs["input_normalisation"] = record
    return df


def add_blocks(stimuli: pd.DataFrame, design: dict, schema: dict) -> dict:
    """Assemble the presented trial sequence from the main, filler and practice blocks.

    Returns ``{"presented": DataFrame, "report": dict | None, "normalisation": dict}``:
    every trial the experiment runs, in order, with a ``block`` column when more than
    one block exists; the per-block counts and item-table checksums, or None when the
    design declares no extra block; and ``{"changed", "collapsed"}``, what Unicode NFC
    normalisation did to the practice and filler tables (see ``load_items``). Trials are
    numbered from 1 within each list, or within each (replicate, list) pair of a
    resampled design, and the counts are per list or pair. ``counterbalance.max_run``
    applies to the main and filler trials together and to the practice trials on their
    own. With ``counterbalance.orders: m``, ``order_1`` to ``order_m`` give each trial's
    position in each order, the practice trials first in every one.
    """
    practice_cfg = design.get("practice")
    filler_cfg = design.get("fillers")
    if not practice_cfg and not filler_cfg:
        # No block column at all: a design that declares none must keep the columns it
        # had, so adding this feature moves no existing artefact.
        return {"presented": stimuli, "report": None,
                "normalisation": {"changed": 0, "collapsed": 0}}

    seed = schema.get("seed", 1)
    stimuli = stimuli.copy()
    stimuli["block"] = BLOCK_MAIN
    if "list" not in stimuli.columns:
        stimuli["list"] = 1
    # The unit the blocks are added to is a presentation version: a list, or in a
    # resampled design a (replicate, list) pair. Added per list, the practice and filler
    # rows carried no replicate, so only the first replicate's version presented them.
    by_replicate = "replicate" in stimuli.columns
    units = (sorted(set(zip(stimuli["replicate"], stimuli["list"], strict=True)))
             if by_replicate else [(None, li) for li in sorted(stimuli["list"].unique())])
    offset = int(max([0] + [int(s) for s in stimuli["set"]]))

    fillers = None
    if filler_cfg:
        fillers = _load_block(filler_cfg, design, "filler", offset)
        offset = max(offset, int(fillers["set"].max()))
    practice = None
    if practice_cfg:
        practice = _load_block(practice_cfg, design, "practice", offset)

    def in_unit(rep, li):
        keep = stimuli["list"] == li
        return keep & (stimuli["replicate"] == rep) if by_replicate else keep

    settings = _trial_order_settings(design)
    orders = settings["orders"]
    parts = []
    for rep, li in units:
        body = stimuli[in_unit(rep, li)].reset_index(drop=True)
        if fillers is not None:
            f = fillers.copy()
            f["list"] = li
            if by_replicate:
                f["replicate"] = rep
            body = _concat_blocks(body, f)
        # One shuffle over main and fillers together is what interleaves them.
        unit = _unit_label(body)
        body = _order_trials(body, seed, settings, unit).reset_index(drop=True)
        if practice is not None:
            p = practice.copy()
            p["list"] = li
            if by_replicate:
                p["replicate"] = rep
            p = _order_trials(p, seed, settings,
                              "the practice block of " + unit).reset_index(drop=True)
            # The practice trials come first in every order.
            if orders > 1:
                for j in range(1, orders + 1):
                    body["order_%d" % j] = body["order_%d" % j] + len(p)
            body = _concat_blocks(p, body)
        body["trial"] = range(1, len(body) + 1)
        parts.append(body)
    out = pd.concat(parts, ignore_index=True)

    # Counted in the first version, as the other blocks are counted per version.
    n_main = int(in_unit(*units[0]).sum())
    report = {"blocks": [{"block": BLOCK_MAIN, "n_per_list": n_main}]}
    if fillers is not None:
        report["blocks"].append({
            "block": "filler", "n_per_list": int(len(fillers)),
            "path": filler_cfg["path"], "sha256": sha256_file(filler_cfg["path"]),
            "placement": "interleaved with the main trials by the seeded order"})
    if practice is not None:
        report["blocks"].append({
            "block": "practice", "n_per_list": int(len(practice)),
            "path": practice_cfg["path"], "sha256": sha256_file(practice_cfg["path"]),
            "placement": "before the main trials"})
    report["analysed"] = BLOCK_MAIN
    changed = sum((b.attrs.get("input_normalisation") or {}).get("changed", 0)
                  for b in (fillers, practice) if b is not None)
    return {"presented": out, "report": report,
            "normalisation": {"changed": changed, "collapsed": 0}}
