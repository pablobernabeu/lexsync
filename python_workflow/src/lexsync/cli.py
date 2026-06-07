# -*- coding: utf-8 -*-
"""Command-line interface: ``lexsync run | corpora list | fetch``."""
from __future__ import annotations

import argparse

from .corpora import fetch_corpus, list_corpora
from .run_pipeline import run_all, run_pipeline


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="lexsync",
        description="lexsync: multidimensional lexical optimisation and hardware-timed experiment generation",
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run one design, or all designs in --config-dir")
    run.add_argument("design", nargs="?", help="path to a design YAML (omit to run all)")
    run.add_argument("--schema", default="config/schema.yaml")
    run.add_argument("--config-dir", default="config")
    run.add_argument("--outdir", default="output")

    corpora = sub.add_parser("corpora", help="corpus registry operations")
    corpora.add_argument("action", choices=["list"])

    fetch = sub.add_parser("fetch", help="fetch a corpus by registry name or language code")
    fetch.add_argument("name")

    args = parser.parse_args(argv)
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


if __name__ == "__main__":
    main()
