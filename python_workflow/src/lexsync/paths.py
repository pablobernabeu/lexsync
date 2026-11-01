"""Which schema a run reads. Mirrors R_workflow/R/paths.R.

The command line, run_pipeline and run_all all resolve the schema here, so the three
entry points cannot disagree about which file a run used.
"""
from __future__ import annotations

import os
import sys

from .datasheet import _posix

# How importlib.resources names the bundled copy, quoted in the error for a schema
# that does not exist so the caller can pass it on purpose.
_BUNDLED_CALL = "importlib.resources.files('lexsync') / 'data' / 'schema.yaml'"


def bundled_schema() -> str:
    """The schema shipped inside the package.

    It is byte-identical to the repository's config/schema.yaml (test_config.py
    enforces the identity), so an installed package runs anywhere.
    """
    from importlib.resources import files
    return str(files("lexsync") / "data" / "schema.yaml")


def resolve_schema(schema_path=None, design_path=None, config_dir=None) -> tuple:
    """Resolve the schema for a run, returning ``(path, origin)``.

    A named ``schema_path`` is used as given and must exist; it is never replaced by
    another file, since that would run a different schema from the one the caller
    chose. With no schema named, the candidates are tried in order:

    - for a folder of designs (``config_dir`` given): ``<config_dir>/schema.yaml``,
      then ``config/schema.yaml`` in the working directory;
    - for a single design: ``config/schema.yaml`` in the working directory, then
      ``schema.yaml`` in the design's own directory;
    - in both cases, last, the copy bundled with the package.

    Each list starts with the file that earlier releases read, so a call that relied on
    it still reads the same schema. Whenever no schema was named, the chosen path is
    printed to stderr as "lexsync: using the schema at '<path>'".

    ``origin`` is one of "named", "config_dir", "working_directory",
    "design_directory" or "bundled".
    """
    if schema_path is not None:
        if not os.path.isfile(schema_path):
            raise FileNotFoundError(
                f"lexsync: schema not found: '{schema_path}'. The schema bundled with "
                f"lexsync is {_BUNDLED_CALL}, at '{bundled_schema()}'.")
        return schema_path, "named"
    cwd_config = (os.path.join("config", "schema.yaml"), "working_directory")
    if config_dir is not None:
        candidates = [(os.path.join(config_dir, "schema.yaml"), "config_dir"), cwd_config]
    else:
        candidates = [cwd_config]
        if design_path is not None:
            # `or "."`, as R's dirname() gives for a bare file name, so both engines
            # record the same path.
            design_dir = os.path.dirname(design_path) or "."
            candidates.append((os.path.join(design_dir, "schema.yaml"), "design_directory"))
    candidates.append((bundled_schema(), "bundled"))
    for path, origin in candidates:
        if os.path.isfile(path):
            # stderr, so a run's printed output and any redirected stdout stay clean.
            # The run log and the datasheet record the path as well, for a caller who
            # never sees this line. In POSIX form, as they record it and as the R
            # engine prints it.
            print(f"lexsync: using the schema at '{_posix(path)}'", file=sys.stderr)
            return path, origin
    raise FileNotFoundError("lexsync: no schema found, and the copy bundled with "
                            "lexsync is missing; reinstall the package.")
