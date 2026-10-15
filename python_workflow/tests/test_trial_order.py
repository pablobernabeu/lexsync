"""Trial-order constraints and per-participant orders (counterbalance.max_run, orders).

The keyed-hash order behaves as a uniform shuffle, so it gives runs of one condition as
long as a uniform shuffle does: over seeds 1 to 1000 of a 60 + 60 lexical decision the
longest run had a median of 7 and a maximum of 21, which in that task means seven or
more consecutive trials with the same correct key. ``counterbalance.max_run`` repairs
the seeded order so that no run is longer than k, and refuses only a constraint that no
order can meet. A plain greedy repair refused feasible designs at the tail of the list,
which is why the repair looks ahead.

Every participant on a list also met the same order. ``counterbalance.orders: m``
writes m orders per list into the loop tables, and the experiments choose one by
participant number. Every test here is pinned identically in test-trial-order.R.
"""
import os

import pandas as pd
import pytest
import yaml

from lexsync import counterbalancing as cb
from lexsync.blocks import add_blocks
from lexsync.counterbalancing import counterbalance
from lexsync.design import validate_design
from lexsync.scripting import loop_table


def _lexdec(n_words, n_pseudo):
    """A one-list lexical decision: words in sets 1..n_words, pseudowords in sets
    1..n_pseudo, so (set, condition) is unique."""
    rows = [{"word": "w%03d" % i, "set": i, "condition": "word"}
            for i in range(1, n_words + 1)]
    rows += [{"word": "p%03d" % i, "set": i, "condition": "pseudoword"}
             for i in range(1, n_pseudo + 1)]
    return pd.DataFrame(rows)


def _longest_run(labels):
    best = run = 0
    previous = object()
    for label in labels:
        run = run + 1 if label == previous else 1
        previous = label
        best = max(best, run)
    return best


def _in_order(out, column="trial"):
    return out.sort_values(["list", column], kind="stable")


def test_max_run_holds_for_every_seed_on_balanced_and_unbalanced_lists():
    design = {"counterbalance": {"lists": 1, "max_run": 2}}
    for n_words, n_pseudo in ((60, 60), (40, 80)):
        stim = _lexdec(n_words, n_pseudo)
        for seed in range(1, 51):
            out = _in_order(counterbalance(stim, design, {"seed": seed}))
            assert _longest_run(out["condition"]) <= 2, (n_words, n_pseudo, seed)
            # Every trial is still presented once, numbered from 1.
            assert sorted(out["word"]) == sorted(stim["word"])
            assert list(out["trial"]) == list(range(1, len(stim) + 1))


def test_the_unconstrained_order_has_long_runs_and_the_repair_changes_only_what_it_must():
    stim = _lexdec(60, 60)
    plain = _in_order(counterbalance(stim, {"counterbalance": {"lists": 1}}, {"seed": 7}))
    assert _longest_run(plain["condition"]) > 2
    # A limit the seeded order already meets leaves it exactly as it was.
    loose = _in_order(counterbalance(
        stim, {"counterbalance": {"lists": 1, "max_run": 120}}, {"seed": 7}))
    assert list(loose["word"]) == list(plain["word"])
    # The repair takes the earliest trial in the seeded order that keeps the limit, so
    # the order agrees with the seeded one up to the first run that breaks it.
    tight = _in_order(counterbalance(
        stim, {"counterbalance": {"lists": 1, "max_run": 2}}, {"seed": 7}))
    labels = list(plain["condition"])
    first_break = next(i for i in range(2, len(labels))
                       if labels[i] == labels[i - 1] == labels[i - 2])
    assert list(tight["word"])[:first_break] == list(plain["word"])[:first_break]


def test_an_impossible_run_limit_is_refused_with_one_message():
    with pytest.raises(ValueError) as err:
        counterbalance(_lexdec(40, 80), {"counterbalance": {"lists": 1, "max_run": 1}},
                       {"seed": 1})
    assert str(err.value) == ("lexsync: no order of list 1 keeps runs of 'condition' to 1 "
                              "or fewer: 80 'pseudoword' trials against 40 others.")
    with pytest.raises(ValueError) as err:
        counterbalance(_lexdec(40, 90), {"counterbalance": {"lists": 1, "max_run": 2}},
                       {"seed": 1})
    assert str(err.value) == ("lexsync: no order of list 1 keeps runs of 'condition' to 2 "
                              "or fewer: 90 'pseudoword' trials against 40 others.")


def test_run_on_names_a_column_and_a_missing_value_is_a_category_of_its_own():
    stim = _lexdec(6, 6)
    stim["answer"] = ["f"] * 6 + [None] * 6
    out = _in_order(counterbalance(
        stim, {"counterbalance": {"lists": 1, "max_run": 1, "run_on": "answer"}},
        {"seed": 3}))
    shown = ["" if a is None or a != a else a for a in out["answer"]]
    assert _longest_run(shown) == 1
    with pytest.raises(ValueError) as err:
        counterbalance(stim, {"counterbalance": {"lists": 1, "max_run": 1,
                                                 "run_on": "animacy"}}, {"seed": 3})
    assert str(err.value) == ("lexsync: counterbalance.run_on names 'animacy', a column "
                              "that list 1 does not have.")
    stim["answer"] = [None] * 9 + ["f"] * 3
    with pytest.raises(ValueError) as err:
        counterbalance(stim, {"counterbalance": {"lists": 1, "max_run": 2,
                                                 "run_on": "answer"}}, {"seed": 3})
    assert str(err.value) == ("lexsync: no order of list 1 keeps runs of 'answer' to 2 or "
                              "fewer: 9 trials with no 'answer' against 3 others.")


def test_the_run_limit_applies_within_each_list_of_a_latin_square():
    rows = []
    for s in range(1, 13):
        for cond in ("related", "unrelated"):
            rows.append({"set": s, "condition": cond, "target": "t%d" % s})
    design = {"paradigm": "priming", "counterbalance": {"lists": 2, "max_run": 1}}
    for seed in range(1, 11):
        out = _in_order(counterbalance(pd.DataFrame(rows), design, {"seed": seed}))
        for _, part in out.groupby("list"):
            assert _longest_run(part["condition"]) == 1, seed


def test_the_trial_order_keys_are_validated():
    base = {"name": "t", "language": "english"}
    cases = [({"max_run": 0}, "lexsync: counterbalance.max_run must be a whole number of "
                              "at least 1."),
             ({"max_run": 1.5}, "lexsync: counterbalance.max_run must be a whole number "
                                "of at least 1."),
             ({"max_run": "2"}, "lexsync: counterbalance.max_run must be a whole number "
                                "of at least 1."),
             ({"max_run": True}, "lexsync: counterbalance.max_run must be a whole number "
                                 "of at least 1."),
             ({"orders": 0}, "lexsync: counterbalance.orders must be a whole number of "
                             "at least 1."),
             ({"run_on": 3}, "lexsync: counterbalance.run_on must name a column of the "
                             "trials."),
             ({"run_on": " "}, "lexsync: counterbalance.run_on must name a column of the "
                               "trials.")]
    for block, message in cases:
        with pytest.raises(ValueError) as err:
            validate_design(dict(base, counterbalance=block), {})
        assert str(err.value) == message, block
    assert validate_design(dict(base, counterbalance={"max_run": 2.0, "orders": 3,
                                                      "run_on": "answer"}), {}) == []


def test_orders_give_distinct_orders_that_each_keep_the_run_limit():
    stim = _lexdec(30, 30)
    design = {"counterbalance": {"lists": 1, "orders": 3, "max_run": 2}}
    out = counterbalance(stim, design, {"seed": 11})
    assert [c for c in out.columns if c.startswith("order_")] == [
        "order_1", "order_2", "order_3"]
    # Order 1 is the order the trial column gives, the order without the key.
    assert list(out["order_1"]) == list(out["trial"])
    sequences = []
    for j in (1, 2, 3):
        ordered = out.sort_values("order_%d" % j, kind="stable")
        assert sorted(ordered["order_%d" % j]) == list(range(1, 61))
        assert _longest_run(ordered["condition"]) <= 2
        sequences.append(tuple(ordered["word"]))
    assert len(set(sequences)) == 3
    plain = counterbalance(stim, {"counterbalance": {"lists": 1, "max_run": 2}}, {"seed": 11})
    assert list(plain["word"]) == list(out["word"])
    assert "order_1" not in plain.columns


def test_the_order_keys_give_both_engines_the_same_orders():
    # Order j > 1 ranks each trial by the SHA-256 of "seed|order<j>|replicate|list|set|
    # condition". test-trial-order.R pins these same words.
    stim = pd.DataFrame({"word": list("abcdefgh"), "condition": ["x", "y"] * 4,
                         "set": [1, 1, 2, 2, 3, 3, 4, 4]})
    out = counterbalance(stim, {"counterbalance": {"lists": 2, "orders": 3}}, {"seed": 2026})
    assert list(_in_order(out, "order_1")["word"]) == ["b", "f", "e", "a", "c", "g", "h", "d"]
    assert list(_in_order(out, "order_2")["word"]) == ["f", "a", "e", "b", "c", "h", "d", "g"]
    assert list(_in_order(out, "order_3")["word"]) == ["f", "b", "e", "a", "d", "c", "h", "g"]


def test_practice_and_fillers_follow_every_order(schema, tmp_path):
    practice = tmp_path / "practice.csv"
    pd.DataFrame({"item": range(1, 7), "condition": ["word", "pseudoword"] * 3,
                  "target": ["pa", "pb", "pc", "pd", "pe", "pf"]}).to_csv(practice,
                                                                          index=False)
    fillers = tmp_path / "fillers.csv"
    pd.DataFrame({"item": range(1, 21), "condition": ["pseudoword"] * 20,
                  "target": ["f%02d" % i for i in range(1, 21)]}).to_csv(fillers, index=False)
    design = {"name": "t", "language": "english", "paradigm": "lexical_decision",
              "practice": {"path": str(practice)}, "fillers": {"path": str(fillers)},
              "counterbalance": {"lists": 1, "orders": 2, "max_run": 2}}
    stim = _lexdec(20, 0).rename(columns={"word": "target"})
    out = add_blocks(counterbalance(stim, design, schema), design, schema)["presented"]
    for j in (1, 2):
        ordered = out.sort_values("order_%d" % j, kind="stable")
        assert list(ordered["block"])[:6] == ["practice"] * 6
        body = ordered[ordered["block"] != "practice"]
        # Twenty words and twenty filler pseudowords, interleaved under the limit.
        assert _longest_run(body["condition"]) <= 2
        assert _longest_run(ordered["condition"].iloc[:6]) <= 2
    assert list(out["order_1"]) == list(out["trial"])
    # The loop table carries every order, after the columns that place a trial.
    tab = loop_table(out, [{"type": "text", "content": "{target}", "duration_ms": 500}])
    assert list(tab.columns[:8]) == ["trial", "list", "block", "set", "condition",
                                     "order_1", "order_2", "target"]


def test_the_counterbalancing_record_states_the_limit_and_the_orders(schema, tmp_path):
    from lexsync.run_pipeline import run_pipeline

    items = tmp_path / "items.csv"
    rows = []
    for s in range(1, 13):
        for cond in ("related", "unrelated"):
            rows.append({"item": s, "condition": cond, "prime": "%s%d" % (cond[:3], s),
                         "target": "t%d" % s})
    pd.DataFrame(rows).to_csv(items, index=False)
    design_path = tmp_path / "design.yaml"
    design_path.write_text(yaml.safe_dump({
        "name": "order_record", "language": "english", "paradigm": "priming",
        "items": {"source": "table", "path": str(items).replace("\\", "/")},
        "counterbalance": {"lists": 2, "max_run": 2, "orders": 3}}), encoding="utf-8")
    from conftest import _pkg_data
    out = tmp_path / "out"
    run_pipeline(str(design_path), _pkg_data("schema.yaml"), outdir=str(out), verbose=False)
    with open(os.path.join(out, "reports", "order_record_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        import json
        ds = json.load(handle)
    rec = ds["counterbalancing"]
    assert rec["max_run"]["k"] == 2 and rec["max_run"]["run_on"] == "condition"
    assert [r["list"] for r in rec["max_run"]["longest"]] == [1, 2]
    assert all(1 <= r["longest_run"] <= 2 for r in rec["max_run"]["longest"])
    assert rec["orders"] == {
        "m": 3, "rule": "order = (((participant - 1) div 2) mod 3) + 1; a run without a "
                        "participant number presents order 1"}
    with open(os.path.join(out, "reports", "order_record_english_datasheet_py.md"),
              encoding="utf-8") as handle:
        md = handle.read()
    assert ("Each list was presented in 3 trial orders, assigned in rotation by "
            "participant number. Runs of consecutive trials with the same condition were "
            "limited to 2 (van Casteren & Davis, 2006).") in md
    assert "- **Trial orders:** 3 per list" in md


def test_the_settings_resolve_to_the_defaults_when_the_design_gives_none():
    assert cb._trial_order_settings({}) == {"max_run": None, "run_on": "condition",
                                            "orders": 1}
    assert cb._trial_order_settings({"counterbalance": {"max_run": 3, "orders": 2.0}}) == {
        "max_run": 3, "run_on": "condition", "orders": 2}
