"""Install commands in the documentation paste into any shell.

zsh, the default shell for new accounts on macOS since 10.15, breaks two kinds of
pasted install command with its stock options. Square brackets form a pattern, and
with NOMATCH on, an unquoted extra such as lexsync[corpora] stops the shell with "no
matches found" before pip runs. INTERACTIVE_COMMENTS is off, so a line that ends in
a `# ...` comment hands the `#` and every word after it to pip, which stops with
"ERROR: Invalid requirement: '#'". The tests read the package's README, its
documentation and its sources, whose error messages give install hints, and, from a
checkout, the repository's README and apps/README.md. They fail on an argument of
`pip install` that holds `[` outside double quotes, and on a `pip install` line in a
fenced shell block that carries a comment. Single quotes count as unquoted, because
cmd.exe passes them on to pip, while double quotes work in zsh, bash, fish,
PowerShell and cmd.exe alike. The R package documents no pip command, so the check
has no R twin.
"""
import re
from pathlib import Path

import pytest
from helper_repo import repo_path

PACKAGE = Path(__file__).resolve().parents[1]

# The languages of the fenced blocks a reader pastes into a shell.
SHELL_FENCES = {"bash", "sh", "shell", "console", "zsh"}

_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*([A-Za-z0-9_+-]*)")
_PIP_INSTALL = re.compile(r"\bpip3?[ \t]+install\b")
# One argument after `pip install`: a double- or single-quoted string, or a bare
# word. A bare word ends at white space, a quote or a backtick, so the end of a
# Python string literal or of a Markdown code span ends the command.
_ARGUMENT = re.compile(r"""[ \t]+("[^"\n]*"|'[^'\n]*'|[^\s"'`]+)""")


def _shell_lines(text):
    """The numbers of the lines inside a fenced shell block."""
    numbers, fence, shell = set(), None, False
    for number, line in enumerate(text.splitlines(), 1):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence, shell = match.group(1), match.group(2).lower() in SHELL_FENCES
        elif match and match.group(1).startswith(fence) and not line.strip().strip(fence[0]):
            fence = None
        elif shell:
            numbers.add(number)
    return numbers


def _pip_installs(line):
    """The arguments of each `pip install` on a line."""
    for command in _PIP_INSTALL.finditer(line):
        arguments, position = [], command.end()
        while argument := _ARGUMENT.match(line, position):
            arguments.append(argument.group(1))
            position = argument.end()
        yield arguments


def _scan(text):
    """The numbers of the lines with an unquoted extra and of the commented install
    lines in shell blocks, and the number of install commands read."""
    shell = _shell_lines(text)
    extras, comments, read = [], [], 0
    for number, line in enumerate(text.splitlines(), 1):
        for arguments in _pip_installs(line):
            read += 1
            if any("[" in a and not a.startswith('"') for a in arguments):
                extras.append(number)
            # A shell starts a comment only at the start of a word, so the `#` of
            # git+https://...#subdirectory= is part of the URL.
            if number in shell and any(a.startswith("#") for a in arguments):
                comments.append(number)
    return extras, comments, read


def _files(scope):
    if scope == "package":
        # docs/ is absent from the sdist, which ships README.md and src/.
        files = [PACKAGE / "README.md", *sorted((PACKAGE / "docs").rglob("*.md")),
                 *sorted((PACKAGE / "src").rglob("*.py"))]
        return [path for path in files if path.is_file()]
    reason = "the repository's READMEs are not around this package"
    return [repo_path("README.md", reason=reason), repo_path("apps", "README.md", reason=reason)]


def _sweep(scope):
    extras, comments, read = [], [], 0
    for path in _files(scope):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        name = path.relative_to(PACKAGE.parent).as_posix()
        found_extras, found_comments, found = _scan(text)
        extras += [f"{name}:{n}: {lines[n - 1].strip()}" for n in found_extras]
        comments += [f"{name}:{n}: {lines[n - 1].strip()}" for n in found_comments]
        read += found
    # Every scope documents an installation, so reading none means the sweep lost
    # its files and would pass without checking anything.
    assert read, f"no pip install command found in the {scope} files"
    return extras, comments


SAMPLE = """\
pip install lexsync[corpora]
python -m pip install -e .[dev]
raise ImportError("Install it with: pip install lexsync[experiment]")
pip install "lexsync[corpora]"
pip install 'lexsync[corpora]'
```bash
pip install -e python_workflow   # the lexsync package
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```
pip install lexsync  # in prose, outside a shell block
````console
$ pip install "streamlit>=1.49" #the app
````
"""


def test_the_scan_finds_both_forms():
    """The sweeps pass by default if the scan misses a command, so it is shown each
    form, and the forms it must leave alone, once."""
    extras, comments, read = _scan(SAMPLE)
    assert extras == [1, 2, 3, 5]
    assert comments == [7, 12]
    assert read == 9


@pytest.mark.parametrize("scope", ["package", "repository"])
def test_install_commands_quote_their_extras(scope):
    extras, _ = _sweep(scope)
    assert not extras, "put the extra in double quotes:\n" + "\n".join(extras)


@pytest.mark.parametrize("scope", ["package", "repository"])
def test_install_commands_in_shell_blocks_carry_no_comment(scope):
    _, comments = _sweep(scope)
    assert not comments, "move the comment into the prose before the block:\n" + "\n".join(comments)
