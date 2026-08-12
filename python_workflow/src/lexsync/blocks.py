"""Practice and filler trials: rows that are PRESENTED but not ANALYSED.

Everything else in the package treats one frame as both the materials record and the
thing the experiment runs. That works only while the two are the same set of trials, and
they usually are not. A practice block exists to settle the participant into the task and
is discarded before analysis; fillers exist to dilute the manipulation so it is less
guessable, and are likewise not analysed. Both have to reach the generated experiment and
neither belongs in the stimuli file, the descriptives or the realised control.

So the pipeline splits after counterbalancing: the analysis artefacts are written from
the main rows, and the experiment is generated from the presented rows. A ``block``
column marks which is which, and it appears ONLY when a design declares one of these
blocks -- a design without them keeps exactly the columns it had.

Where each block goes in the sequence is a methodological choice, not a convenience:

Practice comes first, as its own run of trials, because its purpose is to precede the
task. It is shuffled within itself so participants do not all meet the practice items in
one order.

Fillers are INTERLEAVED with the main trials, not appended, because a block of fillers at
the end is not a filler -- it is a second block that participants can tell apart. They
are merged into each list before the order is drawn, so one deterministic shuffle mixes
them through. That does renumber the main trials, which is correct: adding fillers
changes the sequence, and the stimuli file records where each item actually appeared.

Both blocks appear in EVERY list. They are not counterbalanced, because they carry no
manipulation to rotate; every participant should get the same practice.

Mirrors R_workflow/R/blocks.R.
"""
from __future__ import annotations

import pandas as pd

from .counterbalancing import _shuffle_deterministic
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
    df = load_items(path, required_fields(design)).copy()
    df["block"] = label
    df["set"] = df["set"].astype(int) + int(set_offset)
    return df.reset_index(drop=True)


def add_blocks(stimuli: pd.DataFrame, design: dict, schema: dict) -> dict:
    """Assemble the presented trial sequence from the main, filler and practice blocks.

    Returns ``{"presented": DataFrame, "report": dict | None}``: every trial the
    experiment runs, in order, with a ``block`` column when more than one block exists;
    and the per-block counts and item-table checksums, or None when the design declares
    no extra block.
    """
    practice_cfg = design.get("practice")
    filler_cfg = design.get("fillers")
    if not practice_cfg and not filler_cfg:
        # No block column at all: a design that declares none must keep the columns it
        # had, so adding this feature moves no existing artefact.
        return {"presented": stimuli, "report": None}

    seed = schema.get("seed", 1)
    stimuli = stimuli.copy()
    stimuli["block"] = BLOCK_MAIN
    if "list" not in stimuli.columns:
        stimuli["list"] = 1
    lists = sorted(stimuli["list"].unique())
    offset = int(max([0] + [int(s) for s in stimuli["set"]]))

    fillers = None
    if filler_cfg:
        fillers = _load_block(filler_cfg, design, "filler", offset)
        offset = max(offset, int(fillers["set"].max()))
    practice = None
    if practice_cfg:
        practice = _load_block(practice_cfg, design, "practice", offset)

    parts = []
    for li in lists:
        body = stimuli[stimuli["list"] == li].reset_index(drop=True)
        if fillers is not None:
            f = fillers.copy()
            f["list"] = li
            body = _concat_blocks(body, f)
        # One shuffle over main and fillers together is what interleaves them.
        body = _shuffle_deterministic(body, seed).reset_index(drop=True)
        if practice is not None:
            p = practice.copy()
            p["list"] = li
            p = _shuffle_deterministic(p, seed).reset_index(drop=True)
            body = _concat_blocks(p, body)
        body["trial"] = range(1, len(body) + 1)
        parts.append(body)
    out = pd.concat(parts, ignore_index=True)

    n_main = int((stimuli["list"] == lists[0]).sum())
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
    return {"presented": out, "report": report}
