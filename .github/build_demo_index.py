"""Generate the index page for the published browser experiments.

GitHub Pages serves no directory listing, so a demo that nothing links to is
published but unreachable. This walks the design configurations, matches each to
the staged experiment, and writes ``site/demos/index.html``. Deriving the list
from ``config/design_*.yaml`` rather than hard-coding it means a design added or
renamed in the repository cannot leave the index behind.

Only the four scalar keys needed here are read (``name``, ``language``,
``paradigm`` and ``description``), by line, so the script has no dependency on a
YAML parser and runs on a bare Python. The card text is the design's own
``description``, which the author wrote and which therefore describes the
experiment better than anything derivable from the filename.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DEMO_DIR = ROOT / "site" / "demos"

# The paradigm identifier is written for a machine. These are what a reader of
# the psycholinguistic literature would call the same task.
PARADIGM_LABELS = {
    "lexical_decision": "Lexical decision",
    "factorial_word": "Factorial word contrast",
    "priming": "Priming",
    "self_paced_reading": "Self-paced reading",
    "continuous": "Continuous predictor",
}

SCALAR = re.compile(r"^(name|language|paradigm|description)\s*:\s*(.+?)\s*$")


def unquote(value: str) -> str:
    """Undo the one YAML quoting form these configurations use."""
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def read_design(path: Path) -> dict[str, str]:
    """Return the top-level scalars of a design file."""
    found: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        # Only top-level keys: an indented line belongs to a nested block, where
        # `name` means something else (a condition's name, for instance).
        if line[:1].isspace():
            continue
        match = SCALAR.match(line)
        if match:
            found.setdefault(match.group(1), unquote(match.group(2).strip()))
    return found


def collect() -> list[dict[str, str]]:
    demos = []
    for config in sorted(CONFIG_DIR.glob("design_*.yaml")):
        design = read_design(config)
        name, language = design.get("name"), design.get("language")
        if not name or not language:
            continue
        target = DEMO_DIR / f"{name}_{language}.html"
        if not target.exists():
            continue
        paradigm = design.get("paradigm", "")
        # Only some designs declare a paradigm; the rest take the factorial word
        # contrast the schema defaults to. Stating that is better than an
        # empty chip.
        label = PARADIGM_LABELS.get(paradigm) if paradigm else PARADIGM_LABELS["factorial_word"]
        demos.append(
            {
                "file": target.name,
                "name": name,
                "language": language.capitalize(),
                "paradigm": label or paradigm.replace("_", " ").capitalize(),
                "description": design.get("description", ""),
            }
        )
    return demos


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Generated experiments &middot; lexsync</title>
  <link rel="icon" href="../logo.svg">
  <style>
    :root {{
      --bg:#ffffff; --fg:#1b1b1b; --lead:#444; --muted:#555; --link:#7C4EA3;
      --card-bg:#ffffff; --card-border:#e3e3e3; --card-hover:#b8b8b8; --chip:#f3f3f3;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg:#0f1722; --fg:#e9eef3; --lead:#c3cdd7; --muted:#9fb0c0; --link:#C3ADE8;
        --card-bg:#16222f; --card-border:#27384a; --card-hover:#3c5570; --chip:#1d2c3b;
      }}
    }}
    body {{
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      max-width: 52rem; margin: 3.5rem auto; padding: 0 1.25rem; line-height: 1.6;
      background: var(--bg); color: var(--fg);
    }}
    h1 {{ font-size: 1.9rem; margin-bottom: .25rem; letter-spacing: -.5px; }}
    p.lead {{ color: var(--lead); margin-top: 0; }}
    a {{ color: var(--link); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 1rem; margin-top: 2rem; }}
    a.card {{
      background: var(--card-bg); color: inherit; text-decoration: none;
      border: 1px solid var(--card-border); border-top: 3px solid var(--link);
      border-radius: 10px; padding: 1rem 1.1rem; display: block;
      transition: border-color .15s, transform .15s;
    }}
    a.card:hover {{ border-color: var(--card-hover); transform: translateY(-2px); }}
    a.card:focus-visible {{ outline: 2px solid var(--link); outline-offset: 2px; }}
    .card h2 {{ margin: 0 0 .35rem; font-size: 1.05rem; }}
    .card p {{ margin: 0 0 .7rem; color: var(--muted); font-size: .9rem; line-height: 1.5; }}
    .chip {{
      display: inline-block; background: var(--chip); color: var(--muted);
      font-size: .74rem; padding: .1rem .45rem; border-radius: 4px; margin-right: .3rem;
    }}
    footer {{ margin-top: 3rem; color: var(--muted); font-size: .9rem; }}
    footer a {{ color: inherit; }}
    @media (prefers-reduced-motion: reduce) {{ a.card {{ transition: none; }} }}
  </style>
</head>
<body>
  <h1>Generated experiments</h1>
  <p class="lead">Every worked design in the lexsync repository ships as a browser experiment, written
  by the same pipeline that emits the PsychoPy and OpenSesame scripts and rendered from the same
  declarative event list. These are build artefacts rather than mock-ups. Each is a single HTML file
  carrying its own trial list, so it runs by being opened.</p>
  <div class="grid">
{cards}
  </div>
  <footer>
    <a href="../">lexsync documentation</a> &middot;
    <a href="https://github.com/pablobernabeu/lexsync">Source on GitHub</a>
  </footer>
</body>
</html>
"""

CARD = """    <a class="card" href="{file}">
      <h2>{paradigm}</h2>
      <p>{description}</p>
      <span class="chip">{language}</span><span class="chip">{name}</span>
    </a>"""


def main() -> None:
    demos = collect()
    if not demos:
        raise SystemExit("no demos matched a design configuration; refusing to write an empty index")
    cards = "\n".join(
        CARD.format(**{k: html.escape(v) for k, v in demo.items()}) for demo in demos
    )
    (DEMO_DIR / "index.html").write_text(PAGE.format(cards=cards), encoding="utf-8")
    print(f"wrote {DEMO_DIR / 'index.html'} with {len(demos)} experiments")


if __name__ == "__main__":
    main()
