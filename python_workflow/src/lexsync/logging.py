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
    """Start a new run log.

    Args:
        name: A label for the run.
        meta: A mapping of run-level metadata (seed, versions, ...).

    Returns:
        A run-log object (a dictionary).
    """
    return {
        "name": name,
        "started": _now(),
        "engine": f"Python {platform.python_version()}",
        "meta": meta or {},
        "steps": [],
    }


# The console-narration gate, mirroring the R engine's options(lexsync.verbose):
# run_pipeline sets it from its `verbose` argument, so an embedding front end
# (the Streamlit app runs with verbose=False) gets a silent console while every
# step is still recorded on the log itself.
_VERBOSE = True


def get_verbose() -> bool:
    """The current setting, so a caller that changes it can put it back.

    run_pipeline does exactly that, as the R twin restores its
    options(lexsync.verbose) with on.exit.

    Returns:
        Whether the console narration is on.
    """
    return _VERBOSE


def set_verbose(flag: bool) -> None:
    """Turn the console narration on or off.

    Args:
        flag: Whether steps are printed as they are logged.
    """
    global _VERBOSE
    _VERBOSE = bool(flag)


def log_step(log: dict, message: str, data: dict | None = None) -> dict:
    """Append a step to a run log.

    Args:
        log: A run-log object.
        message: A short description of the step.
        data: An optional mapping of step details.

    Returns:
        The updated run-log object.
    """
    log["steps"].append({"time": _now(), "message": message, "data": data})
    if _VERBOSE:
        print(f"[lexsync] {message}")
    return log


def log_artefact(log: dict, path: str, rows=None) -> dict:
    """Record a written artefact (path, rows, fingerprint) in the log.

    Args:
        log: A run-log object.
        path: A file path that has just been written.
        rows: Optional row count.

    Returns:
        The updated run-log object.
    """
    return log_step(log, f"wrote '{os.path.basename(path)}'",
                    {"path": path, "rows": rows, "md5": hash_file(path)})


def write_run_log(log: dict, md_path: str, jsonl_path: str | None = None) -> str:
    """Write the run log to Markdown, and optionally to JSON Lines.

    Args:
        log: A run-log object.
        md_path: Output path for the Markdown log.
        jsonl_path: Optional output path for the JSON Lines log.

    Returns:
        ``md_path``.
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
