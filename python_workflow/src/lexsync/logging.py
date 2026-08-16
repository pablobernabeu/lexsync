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


def set_verbose(flag: bool) -> None:
    global _VERBOSE
    _VERBOSE = bool(flag)


def log_step(log: dict, message: str, data: dict | None = None) -> dict:
    log["steps"].append({"time": _now(), "message": message, "data": data})
    if _VERBOSE:
        print(f"[lexsync] {message}")
    return log


def log_artefact(log: dict, path: str, rows=None) -> dict:
    return log_step(log, f"wrote '{os.path.basename(path)}'",
                    {"path": path, "rows": rows, "md5": hash_file(path)})


def write_run_log(log: dict, md_path: str, jsonl_path: str | None = None) -> str:
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
