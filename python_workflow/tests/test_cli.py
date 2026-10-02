"""The command-line interface and the ``python -m lexsync`` module entry point."""


import os

import pytest

from lexsync.cli import main


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
    # directory an unnamed schema must resolve to the copy shipped inside the
    # package (byte-identical to config/schema.yaml; the identity is enforced
    # elsewhere in the suite).
    from lexsync.paths import resolve_schema
    monkeypatch.chdir(tmp_path)
    resolved, origin = resolve_schema(config_dir="config")
    assert origin == "bundled"
    assert os.path.isfile(resolved)


def test_explicit_missing_schema_still_errors(tmp_path, monkeypatch, capsys):
    # The fallback is only for an unnamed schema: a path the user named must not be
    # silently substituted.
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(["run", "--schema", "does_not_exist.yaml"])
    assert exc.value.code == 1
    assert capsys.readouterr().err.startswith(
        "lexsync: schema not found: 'does_not_exist.yaml'")


def _cli_study(root, seed):
    """study/config/ holding one design and a schema with its own seed."""
    from conftest import _pkg_data
    cfg = root / "study" / "config"
    cfg.mkdir(parents=True)
    with open(_pkg_data("schema.yaml"), encoding="utf-8") as handle:
        text = handle.read()
    with open(cfg / "schema.yaml", "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\nseed: 2026\n", "\nseed: %d\n" % seed, 1))
    lexicon = _pkg_data("en_example.csv").replace("\\", "/")
    (cfg / "design_cli.yaml").write_text(
        "name: cli_study\n"
        "language: english\n"
        f"lexicon: {lexicon}\n"
        "n_per_condition: 5\n"
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}\n"
        "conditions:\n"
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}\n"
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}\n"
        "match_on: [length]\n",
        encoding="utf-8",
    )
    return cfg


def test_run_all_uses_the_config_dirs_schema(tmp_path, monkeypatch, capsys):
    # `run --config-dir DIR` resolved the schema from ./config/schema.yaml and then
    # the bundled copy, never from DIR, so a study's own seed and tolerances were
    # ignored whenever the working directory had no config/ folder.
    import json
    _cli_study(tmp_path, 99)
    monkeypatch.chdir(tmp_path)
    main(["run", "--config-dir", "study/config", "--outdir", "out"])
    with open(tmp_path / "out" / "reports" / "cli_study_english_datasheet_py.json",
              encoding="utf-8") as handle:
        rep = json.load(handle)["reproducibility"]
    assert rep["seed"] == 99
    assert rep["schema_path"] == "study/config/schema.yaml"
    assert "lexsync: using the schema at 'study" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [["run", "nope.yaml"], ["run"], ["fetch", "nosuch"]])
def test_lexsync_errors_print_without_a_traceback(tmp_path, monkeypatch, capsys, argv):
    # A missing design, a folder without designs and an unknown corpus each raise a
    # prepared "lexsync:" message, which used to arrive under a Python traceback.
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert err.startswith("lexsync:")
    assert "Traceback" not in err


def test_traceback_reraises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="lexsync: configuration not found"):
        main(["--traceback", "run", "nope.yaml"])


def test_other_errors_still_raise(monkeypatch):
    # Only lexsync's own messages are prepared for a reader; anything else is a bug
    # whose traceback is the useful report.
    import lexsync.cli as cli

    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")
    monkeypatch.setattr(cli, "list_corpora", boom)
    with pytest.raises(RuntimeError, match="unexpected"):
        main(["corpora", "list"])


def test_usage_errors_keep_argparse_status(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["run", "--no-such-flag"])
    assert exc.value.code == 2


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
