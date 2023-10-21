import ast

from module_level_lint import Plugin
from tests import FIXTURES


def run_lint(path) -> set[str]:
    with open(path) as f:
        tree = ast.parse(f.read())
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial() -> None:
    path = FIXTURES / "trivial.py"
    results = run_lint(path)
    assert results == set()


def test_clean() -> None:
    path = FIXTURES / "clean.py"
    results = run_lint(path)
    assert results == set()


def test_mll001() -> None:
    path = FIXTURES / "mll001.py"
    results = run_lint(path)
    assert len(results) > 0


def test_mll002() -> None:
    path = FIXTURES / "mll002.py"
    results = run_lint(path)
    assert len(results) > 0


def test_mll003() -> None:
    path = FIXTURES / "mll003.py"
    results = run_lint(path)
    assert len(results) > 0


def test_mll004() -> None:
    path = FIXTURES / "mll004.py"
    results = run_lint(path)
    assert len(results) > 0


def test_mll005() -> None:
    path = FIXTURES / "mll005.py"
    results = run_lint(path)
    assert len(results) > 0


def test_mll006() -> None:
    path = FIXTURES / "mll006.py"
    results = run_lint(path)
    assert len(results) > 0
