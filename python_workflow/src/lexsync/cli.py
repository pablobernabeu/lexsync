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


def _positive_int(text: str) -> int:
    """An argparse type for a count of at least 1."""
    try:
        value = int(text)
    except ValueError:
        value = 0
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be a whole number of at least 1, not {text!r}")
    return value


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
    run.add_argument("--config-dir", default="config",
                     help="used only when no design is named: the folder whose design_*.yaml "
                          "and design_*.yml files run and whose schema.yaml is tried first "
                          "(default: config)")
    run.add_argument("--outdir", default="output",
                     help="root of the written stimuli/, reports/ and experiments/ (default: output)")

    corpora = sub.add_parser("corpora", help="corpus registry operations")
    corpora.add_argument("action", choices=["list"], help="list: print the corpus registry as a table")

    fetch = sub.add_parser("fetch", help="fetch a corpus by registry name or language code into the "
                                         "cache and print its path")
    fetch.add_argument("name", help="a registry corpus name, or a language code the wordfreq connector "
                                    "builds a lexicon for")
    # The committed lexica were built with 30,000 forms (20,000 for zh) by
    # corpora/fetch_corpora.py. The default is 10,000.
    fetch.add_argument("--n-words", type=_positive_int, default=10000,
                       help="forms in a lexicon the wordfreq connector builds (default 10000)")

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
            print(fetch_corpus(args.name, n_words=args.n_words))
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
