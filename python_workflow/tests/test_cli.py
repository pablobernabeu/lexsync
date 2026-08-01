"""The command-line interface and the ``python -m lexsync`` module entry point."""


from lexsync.cli import main


def test_corpora_list_runs(capsys):
    main(["corpora", "list"])
    out = capsys.readouterr().out
    assert "language" in out


def test_help_runs(capsys):
    main([])  # no subcommand prints help
    out = capsys.readouterr().out
    assert "run" in out and "corpora" in out


def test_run_one_design(tmp_path, en_lexicon_path):
    import os

    import lexsync
    schema_path = os.path.join(os.path.dirname(lexsync.__file__), "data", "schema.yaml")
    design = tmp_path / "d.yaml"
    design.write_text(
        "name: cli_test\n"
        "language: english\n"
        f"lexicon: {en_lexicon_path.replace(chr(92), '/')}\n"
        "n_per_condition: 5\n"
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}\n"
        "conditions:\n"
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}\n"
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}\n"
        "match_on: [length]\n",
        encoding="utf-8",
    )
    out = tmp_path / "out"
    main(["run", str(design), "--schema", schema_path, "--outdir", str(out)])
    assert (out / "stimuli" / "cli_test_english_stimuli_py.csv").exists()


def test_module_entrypoint_exists():
    # python -m lexsync routes to cli.main via __main__.py
    import lexsync.__main__ as m
    assert hasattr(m, "main")
