"""The API reference promises that every public name is documented there.

R CMD check refuses an exported object whose help page has no \\arguments or
\\value, so the R twin's reference cannot fall behind its exports. Nothing gave
the Python side that guarantee, and twenty of the rendered objects once carried
no prose at all while not one documented a parameter. These checks read the same
source mkdocstrings renders, so a new export or a new argument has to be
documented before the reference can claim to describe it.
"""
import ast
import inspect
from pathlib import Path

import pytest

import lexsync

SRC = Path(lexsync.__file__).resolve().parent
API_MD = Path(__file__).resolve().parents[1] / "docs" / "api.md"

# Objects api.md renders that are not plain functions, so their documentation is
# read from the source rather than from a runtime __doc__.
_ATTRIBUTES = {"PARADIGMS"}


def _documented_paths() -> list[str]:
    return [line[4:].strip() for line in API_MD.read_text(encoding="utf-8").splitlines()
            if line.startswith("::: ")]


def _module_docstrings(module: str) -> dict[str, str | None]:
    """Every top-level name in one module file, with the docstring griffe reads."""
    tree = ast.parse((SRC / f"{module}.py").read_text(encoding="utf-8"))
    found: dict[str, str | None] = {}
    body = tree.body
    for i, node in enumerate(body):
        following = body[i + 1] if i + 1 < len(body) else None
        # An attribute's docstring is the string expression right after it, which
        # is how PARADIGMS is documented; a function's is its own first statement.
        attached = None
        if (isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
                and isinstance(following.value.value, str)):
            attached = following.value.value
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            found[node.name] = ast.get_docstring(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found[target.id] = attached
    return found


def _defining_module(name: str) -> str:
    obj = getattr(lexsync, name)
    if hasattr(obj, "__module__"):
        return obj.__module__.rsplit(".", 1)[-1]
    owners = [p.stem for p in sorted(SRC.glob("*.py"))
              if name in _module_docstrings(p.stem)]
    assert len(owners) == 1, f"{name} is defined in {owners}"
    return owners[0]


def _resolve(path: str) -> tuple[str, str]:
    parts = path.split(".")
    assert parts[0] == "lexsync", path
    if len(parts) == 3:
        return parts[1], parts[2]
    return _defining_module(parts[1]), parts[1]


def test_every_public_name_is_rendered_exactly_once():
    paths = _documented_paths()
    assert len(paths) == len(set(paths)), "api.md renders a name twice"
    rendered = {p.split(".")[-1] for p in paths}
    missing = [n for n in lexsync.__all__ if n not in rendered]
    assert not missing, f"api.md does not render {missing}"


@pytest.mark.parametrize("path", _documented_paths())
def test_every_rendered_object_documents_itself(path):
    module, name = _resolve(path)
    doc = _module_docstrings(module).get(name)
    assert doc and doc.strip(), f"{path} has no docstring"
    if name in _ATTRIBUTES:
        return
    obj = getattr(__import__(f"lexsync.{module}", fromlist=[name]), name)
    params = [p for p in inspect.signature(obj).parameters
              if p not in ("self", "args", "kwargs")]
    if params:
        assert "\nArgs:\n" in doc, f"{path} documents no parameter"
        args = "\n" + doc.split("\nArgs:\n", 1)[1]
        for param in params:
            assert f"\n    {param}:" in args, f"{path} does not document '{param}'"
    assert "\nReturns:\n" in doc, f"{path} does not say what it returns"
