"""An automated, comprehensive run log (Markdown + JSON Lines).

Mirrors R_workflow/R/logging.R. Records each pipeline stage with its parameters,
the seed, provenance and file fingerprints. Imported as ``lexsync.logging``;
this does not shadow the standard library ``logging`` for absolute imports.
"""
from __future__ import annotations

import datetime
import json
import os
import platform

from .io_utils import hash_file


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def new_run_log(name: str, meta: dict | None = None) -> dict:
    """Start a run log.

    Returns a dict holding the run's ``name``, its ``started`` time (local ISO 8601, to
    the second), the ``engine`` (``Python <version>``), ``meta`` (empty when None) and
    an empty list of ``steps``, which ``log_step`` and ``log_artefact`` append to.
    """
    return {
        "name": name,
        "started": _now(),
        "engine": f"Python {platform.python_version()}",
        "meta": meta or {},
        "steps": [],
    }


# The console-narration gate, mirroring the R engine's options(lexsync.verbose):
# run_pipeline sets it from its `verbose` argument, so a caller that passes
# verbose=False gets a silent console while every step is still recorded on the
# log itself.
_VERBOSE = True


def get_verbose() -> bool:
    """The current setting, so a caller that changes it can put it back.

    run_pipeline does exactly that, as the R twin restores its
    options(lexsync.verbose) with on.exit.
    """
    return _VERBOSE


def set_verbose(flag: bool) -> None:
    global _VERBOSE
    _VERBOSE = bool(flag)


def log_step(log: dict, message: str, data: dict | None = None) -> dict:
    """Append a step to ``log`` in place and return ``log``.

    The step is ``{"time", "message", "data"}``, with the current time and ``data``
    None when it is not given. ``[lexsync] <message>`` is also printed unless
    ``lexsync.logging.set_verbose(False)`` has silenced the console, as
    ``run_pipeline(verbose=False)`` does.
    """
    log["steps"].append({"time": _now(), "message": message, "data": data})
    if _VERBOSE:
        print(f"[lexsync] {message}")
    return log


def log_artefact(log: dict, path: str, rows=None) -> dict:
    """Log a written file as a step and return ``log``.

    The step's message is ``wrote '<file name>'`` and its data ``{"path", "rows",
    "md5"}``: ``rows`` as given (None by default) and the file's MD5 digest, None when
    the file does not exist.
    """
    return log_step(log, f"wrote '{os.path.basename(path)}'",
                    {"path": path, "rows": rows, "md5": hash_file(path)})


def write_run_log(log: dict, md_path: str, jsonl_path: str | None = None) -> str:
    """Write ``log`` as Markdown to ``md_path`` and return ``md_path``.

    The directory of ``md_path`` is created when it is missing. The file holds the
    engine, the start and finish times, the ``meta`` entries under "Run metadata" when
    there are any, and each step with its data. Given ``jsonl_path``, the steps alone
    are also written there as JSON Lines, one step per line. Both files are UTF-8 with
    LF line endings.
    """
    os.makedirs(os.path.dirname(md_path) or ".", exist_ok=True)
    lines = [
        f"# lexsync run log: {log['name']}", "",
        f"- Engine: {log['engine']}",
        f"- Started: {log['started']}",
        f"- Finished: {_now()}",
    ]
    if log["meta"]:
        lines += ["", "## Run metadata", ""]
        for key, value in log["meta"].items():
            lines.append(f"- {key}: {value}")
    lines += ["", "## Steps", ""]
    for step in log["steps"]:
        lines.append(f"- **{step['time']}**: {step['message']}")
        if step["data"]:
            for key, value in step["data"].items():
                lines.append(f"    - {key}: {value}")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    if jsonl_path:
        with open(jsonl_path, "w", encoding="utf-8", newline="\n") as handle:
            for step in log["steps"]:
                handle.write(json.dumps(step, ensure_ascii=False) + "\n")
    return md_path
