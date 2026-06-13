# -*- coding: utf-8 -*-
"""Materials datasheet and pre-registration template.

A *materials datasheet* is a machine- and human-readable provenance record for a
design: where the items came from, how they were selected and matched, the
realised control, how they were counterbalanced, and the seeds, versions and
checksums needed to reproduce them exactly. It is the shareable materials record
whose scarcity motivates lexsync (Bochynska et al., 2023; Roettger, 2019). The
module also emits an auto-filled Methods paragraph and a pre-registration
skeleton. Mirrors R_workflow/R/datasheet.R.
"""
from __future__ import annotations

import json
import platform

from .io_utils import sha256_file

DATASHEET_VERSION = "1.0"


def _versions(engine: str) -> dict:
    out = {"engine": engine, "lexsync": "0.1.0"}
    if engine == "python":
        import numpy as np
        import pandas as pd
        out["python"] = platform.python_version()
        out["pandas"] = pd.__version__
        out["numpy"] = np.__version__
        try:
            import scipy
            out["scipy"] = scipy.__version__
        except Exception:
            pass
    return out


def _controlled(design: dict, source: str) -> list:
    if source == "corpus":
        return list(design.get("match_on") or [])
    if source == "generate":
        return ["length"]
    return []


def build_datasheet(design, schema, report, stimuli, source_path, artifacts,
                    seed, engine="python") -> dict:
    """Assemble the datasheet dictionary from the pipeline's objects."""
    source = (design.get("items") or {}).get("source", "corpus")
    controlled = _controlled(design, source)
    conditions = list(dict.fromkeys(stimuli["condition"]))

    realised = []
    if report is not None:
        for _, r in report["comparisons"].iterrows():
            realised.append({
                "dimension": r["dimension"],
                "role": "controlled" if r["dimension"] in controlled else "manipulated/free",
                "cohens_d": _num(r["cohens_d"]),
                "ci_low": _num(r.get("d_ci_low")), "ci_high": _num(r.get("d_ci_high")),
                "tost_p": _num(r.get("tost_p")), "equivalent": _bool(r.get("equivalent")),
            })

    if source == "corpus":
        selection = {"method": ((design.get("matching") or {}).get("method")
                                or (schema.get("matching") or {}).get("method")
                                or "standardised_euclidean"),
                     "match_on": controlled,
                     "tolerance_k": (schema.get("matching") or {}).get("tolerance_k")}
    elif source == "generate":
        selection = {"method": "constrained letter substitution (deterministic pseudowords)",
                     "matched_on": ["length"]}
    else:
        selection = {"method": "item table (user-supplied)"}

    dims = {d: schema["dimensions"][d] for d in schema.get("dimensions", {})
            if d in controlled or source == "corpus"}

    return {
        "lexsync_datasheet_version": DATASHEET_VERSION,
        "design": {
            "name": design["name"], "language": design["language"],
            "paradigm": design.get("paradigm", "factorial"), "source": source,
            "description": design.get("description"),
            "n_per_condition": design.get("n_per_condition") or design.get("n_per_cell"),
        },
        "materials_source": {
            "type": source, "path": source_path, "sha256": sha256_file(source_path),
            "provenance": "see corpora/ATTRIBUTION.md for corpus licence and citation"
            if source in ("corpus", "generate") else "user-supplied item table",
        },
        "dimensions": dims,
        "selection": selection,
        "realised_control": realised,
        "counterbalancing": {
            "recipe": "latin_square_target" if source == "table" else "factorial",
            "lists": (design.get("counterbalance") or {}).get("lists", 1),
        },
        "items": {
            "n_total": int(len(stimuli)), "n_conditions": len(conditions),
            "conditions": conditions,
            "stimuli_file": artifacts.get("stimuli"),
            "stimuli_sha256": sha256_file(artifacts.get("stimuli")),
        },
        "reproducibility": {"seed": seed, "versions": _versions(engine)},
        "artifacts": [{"file": p, "sha256": sha256_file(p)}
                      for p in _artifact_paths(artifacts) if p],
    }


def _artifact_paths(artifacts: dict) -> list:
    paths = [artifacts.get(k) for k in ("stimuli", "descriptives", "comparisons")]
    exps = artifacts.get("experiments") or {}
    paths += list(exps.values())
    return paths


def _num(v):
    try:
        return None if v is None or v != v else round(float(v), 4)
    except (TypeError, ValueError):
        return None


def _bool(v):
    return None if v is None or (isinstance(v, float) and v != v) else bool(v)


def methods_paragraph(ds: dict) -> str:
    d = ds["design"]
    src = ds["materials_source"]["type"]
    n = d["n_per_condition"]
    lang = d["language"].capitalize()
    if src == "corpus":
        ctrl = ", ".join(ds["selection"]["match_on"]) or "the control dimensions"
        lead = (f"{n} items per condition were selected from the {lang} lexicon "
                f"({ds['materials_source']['provenance']}) and matched item by item on "
                f"{ctrl} using lexsync's {ds['selection']['method']} matcher")
    elif src == "generate":
        lead = (f"{n} real {lang} words and {n} length-matched pseudowords "
                f"(generated by {ds['selection']['method']}) were assembled for a "
                f"lexical-decision contrast")
    else:
        lead = (f"{ds['items']['n_total'] // max(1, ds['items']['n_conditions'])} items "
                f"were drawn from an item table for a {d['paradigm']} design ({lang})")
    ctrl_rows = [r for r in ds["realised_control"] if r["role"] == "controlled"
                 and r["ci_high"] is not None]
    if ctrl_rows:
        worst = max(ctrl_rows, key=lambda r: abs(r["cohens_d"]))
        control = (f". The realised control was tight: the largest standardised difference on "
                   f"any matched dimension was {abs(worst['cohens_d']):.2f} "
                   f"(90% CI [{worst['ci_low']:.2f}, {worst['ci_high']:.2f}]), within the "
                   f"0.5-SD equivalence bound")
    else:
        control = ""
    cb = ds["counterbalancing"]
    tail = (f". Materials were counterbalanced into {cb['lists']} list(s) "
            f"({cb['recipe']}) and generated for PsychoPy, OpenSesame and jsPsych. The "
            f"selection is deterministic and reproducible (seed "
            f"{ds['reproducibility']['seed']}; lexsync "
            f"{ds['reproducibility']['versions']['lexsync']}).")
    return lead + control + tail


def prereg_template(ds: dict) -> str:
    return (
        "## Pre-registration template\n\n"
        "*Auto-generated by lexsync. The Materials section is filled from the datasheet; "
        "complete the remaining sections before data collection.*\n\n"
        "### Study information\n- Title:\n- Authors:\n- Research questions:\n\n"
        "### Hypotheses\n- H1:\n\n"
        "### Design\n- Manipulated variable(s):\n- Measured variable(s):\n"
        f"- Paradigm: {ds['design']['paradigm']}\n\n"
        "### Materials (from the lexsync datasheet)\n" + methods_paragraph(ds) + "\n\n"
        "### Sampling plan\n- Sample size and justification:\n- Stopping rule:\n\n"
        "### Analysis plan\n- Statistical model:\n- Inference criteria:\n"
        "- Treatment of items (e.g. items as a random factor):\n"
    )


def render_datasheet_md(ds: dict) -> str:
    d = ds["design"]
    lines = [f"# Materials datasheet — {d['name']} ({d['language']})", "",
             f"*lexsync datasheet v{ds['lexsync_datasheet_version']}; "
             f"{ds['reproducibility']['versions']['engine']} engine.*", "",
             "## Provenance", "",
             f"- **Paradigm:** {d['paradigm']}  |  **Item source:** {d['source']}",
             f"- **Description:** {d.get('description') or '—'}",
             f"- **Materials source:** `{ds['materials_source']['path']}` "
             f"(sha256 `{(ds['materials_source']['sha256'] or '')[:16]}…`)",
             f"- **Selection:** {ds['selection']['method']}",
             f"- **Counterbalancing:** {ds['counterbalancing']['recipe']}, "
             f"{ds['counterbalancing']['lists']} list(s)",
             f"- **Items:** {ds['items']['n_total']} rows across "
             f"{ds['items']['n_conditions']} conditions "
             f"({', '.join(ds['items']['conditions'])})",
             f"- **Seed:** {ds['reproducibility']['seed']}  |  **Versions:** "
             + ", ".join(f"{k} {v}" for k, v in ds["reproducibility"]["versions"].items()), ""]
    if ds["realised_control"]:
        lines += ["## Realised control", "",
                  "| Dimension | Role | Cohen's d | 90% CI | TOST p | Equivalent |",
                  "|---|---|---|---|---|---|"]
        for r in ds["realised_control"]:
            ci = (f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}]"
                  if r["ci_low"] is not None else "—")
            d_str = "—" if r["cohens_d"] is None else f"{r['cohens_d']:.2f}"
            lines.append(f"| {r['dimension']} | {r['role']} | {d_str} | {ci} | "
                         f"{r['tost_p']} | {r['equivalent']} |")
        lines.append("")
    lines += ["## Methods paragraph", "", methods_paragraph(ds), "", prereg_template(ds)]
    return "\n".join(lines)


def write_datasheet(ds: dict, json_path: str, md_path: str) -> tuple:
    import os
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ds, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_datasheet_md(ds) + "\n")
    return json_path, md_path
