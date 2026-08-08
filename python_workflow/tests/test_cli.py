"""The command-line interface and the ``python -m lexsync`` module entry point."""


import os

import pytest

from lexsync.cli import DEFAULT_SCHEMA, _resolve_schema, main


def test_corpora_list_runs(capsys):
    main(["corpora", "list"])
    out = capsys.readouterr().out
    assert "language" in out


def test_version_prints_and_exits_zero(capsys):
    # argparse's version action exits, so the SystemExit is the success path.
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip()


def test_default_schema_falls_back_to_bundled_copy(tmp_path, monkeypatch):
    # An installed CLI can run from anywhere, so with no config/ in the working
    # directory the default schema must resolve to the copy shipped inside the
    # package (byte-identical to config/schema.yaml; the identity is enforced
    # elsewhere in the suite).
    monkeypatch.chdir(tmp_path)
    resolved = _resolve_schema(DEFAULT_SCHEMA)
    assert resolved != DEFAULT_SCHEMA
    assert os.path.isfile(resolved)


def test_explicit_missing_schema_still_errors(tmp_path, monkeypatch):
    # The fallback is only for the untouched default: a path the user named must
    # not be silently substituted.
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="pass --schema"):
        main(["run", "--schema", "does_not_exist.yaml"])


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
