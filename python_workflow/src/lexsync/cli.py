"""Command-line interface: ``lexsync run | corpora list | fetch``."""
from __future__ import annotations

import argparse
import os

from .corpora import fetch_corpus, list_corpora
from .run_pipeline import run_all, run_pipeline

# _resolve_schema treats this exact value as "the user asked for nothing in
# particular", which is what licenses the bundled-copy fallback; an explicit
# --schema is honoured or refused, never substituted.
DEFAULT_SCHEMA = "config/schema.yaml"


def _version() -> str:
    # importlib.metadata knows only installed distributions, so a source-tree
    # invocation (sys.path pointing at src/) has no version record to read;
    # "unknown" keeps --version working there instead of crashing.
    from importlib.metadata import PackageNotFoundError, version
    try:
        return version("lexsync")
    except PackageNotFoundError:
        return "unknown"


def _resolve_schema(schema_path: str) -> str:
    """Resolve --schema for the installed CLI as well as for a checkout.

    The default is checkout-relative, so on its own it strands an installed CLI
    run from anywhere else. A byte-identical copy of config/schema.yaml ships
    inside the package (the identity is test-enforced), and the default falls
    back to it when the checkout-relative file is absent. An explicit path
    still errors: silently substituting the bundled schema there would run a
    different file from the one the user named.
    """
    if os.path.exists(schema_path):
        return schema_path
    if schema_path == DEFAULT_SCHEMA:
        from importlib.resources import files
        bundled = files("lexsync") / "data" / "schema.yaml"
        if bundled.is_file():
            return str(bundled)
    raise FileNotFoundError(
        f"lexsync: schema not found: '{schema_path}'. "
        "Run from a checkout root or pass --schema.")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="lexsync",
        description="lexsync: multidimensional lexical optimisation and hardware-timed experiment generation",
    )
    parser.add_argument("--version", action="version", version="lexsync " + _version())
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run one design, or all designs in --config-dir")
    run.add_argument("design", nargs="?", help="path to a design YAML (omit to run all)")
    run.add_argument("--schema", default=DEFAULT_SCHEMA)
    run.add_argument("--config-dir", default="config")
    run.add_argument("--outdir", default="output")

    corpora = sub.add_parser("corpora", help="corpus registry operations")
    corpora.add_argument("action", choices=["list"])

    fetch = sub.add_parser("fetch", help="fetch a corpus by registry name or language code")
    fetch.add_argument("name")

    args = parser.parse_args(argv)
    if args.command == "run":
        schema = _resolve_schema(args.schema)
        if args.design:
            run_pipeline(args.design, schema, args.outdir)
        else:
            run_all(args.config_dir, schema, args.outdir)
    elif args.command == "corpora":
        print(list_corpora().to_string(index=False))
    elif args.command == "fetch":
        print(fetch_corpus(args.name))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
