"""Command-line interface: ``lexsync run | corpora list | fetch``."""
from __future__ import annotations

import argparse
import sys

from .corpora import fetch_corpus, list_corpora
from .run_pipeline import run_all, run_pipeline


def _version() -> str:
    # importlib.metadata knows only installed distributions, so a source-tree
    # invocation (sys.path pointing at src/) has no version record to read;
    # "unknown" keeps --version working there instead of crashing.
    from importlib.metadata import PackageNotFoundError, version
    try:
        return version("lexsync")
    except PackageNotFoundError:
        return "unknown"


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="lexsync",
        description="lexsync: lexical optimisation and hardware-timed experiment generation",
    )
    parser.add_argument("--version", action="version", version="lexsync " + _version())
    parser.add_argument("--traceback", action="store_true",
                        help="show the full Python traceback when a command fails")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run one design, or all designs in --config-dir")
    run.add_argument("design", nargs="?", help="path to a design YAML (omit to run all)")
    # None, so lexsync.paths.resolve_schema can tell a named schema from an unnamed
    # one: a named schema is used or refused, while an unnamed one is looked for
    # beside the designs before the bundled copy is used.
    run.add_argument("--schema", default=None,
                     help="path to the schema YAML (default: resolved, see the docs)")
    run.add_argument("--config-dir", default="config")
    run.add_argument("--outdir", default="output")

    corpora = sub.add_parser("corpora", help="corpus registry operations")
    corpora.add_argument("action", choices=["list"])

    fetch = sub.add_parser("fetch", help="fetch a corpus by registry name or language code")
    fetch.add_argument("name")

    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            if args.design:
                run_pipeline(args.design, args.schema, args.outdir)
            else:
                run_all(args.config_dir, args.schema, args.outdir)
        elif args.command == "corpora":
            print(list_corpora().to_string(index=False))
        elif args.command == "fetch":
            print(fetch_corpus(args.name))
        else:
            parser.print_help()
    except Exception as exc:
        # Every message lexsync prepares for a reader starts with "lexsync:", so the
        # prefix separates a refusal from a bug without a list of exception types.
        # Status 1 is what a traceback gave and what Rscript gives. Status 2 stays
        # argparse's code for a usage error.
        if args.traceback or not str(exc).startswith("lexsync:"):
            raise
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
