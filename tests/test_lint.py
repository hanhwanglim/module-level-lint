import ast
from functools import partial
from pathlib import Path

from module_level_lint import Plugin
from module_level_lint.error import Error
from tests import FIXTURES


def error_str(lineno: int, col_offset: int, msg: str) -> str:
    return f"{lineno}:{col_offset} {msg}"


MLL001 = partial(error_str, msg=Error.MLL001)
MLL002 = partial(error_str, msg=Error.MLL002)
MLL003 = partial(error_str, msg=Error.MLL003)
MLL004 = partial(error_str, msg=Error.MLL004)


def run_lint(path: Path) -> list[str]:
    with open(path) as f:
        tree = ast.parse(f.read())
    plugin = Plugin(tree, str(path))
    return [
        error_str(lineno, col_offset, msg)
        for lineno, col_offset, msg, _ in plugin.run()
    ]


def test_trivial() -> None:
    path = FIXTURES / "trivial.py"
    results = run_lint(path)
    assert results == []


def test_clean() -> None:
    path = FIXTURES / "clean.py"
    results = run_lint(path)
    assert results == []


def test_mll001() -> None:
    path = FIXTURES / "lint" / "mll001.py"
    results = run_lint(path)
    assert results == [MLL001(lineno=5, col_offset=0)]


def test_mll002() -> None:
    path = FIXTURES / "lint" / "mll002.py"
    results = run_lint(path)
    assert results == [MLL002(lineno=3, col_offset=0)]


def test_mll003() -> None:
    path = FIXTURES / "lint" / "mll003.py"
    results = run_lint(path)
    assert results == [MLL003(lineno=5, col_offset=0)]


def test_mll004() -> None:
    path = FIXTURES / "lint" / "mll004.py"
    results = run_lint(path)
    assert results == [MLL004(lineno=5, col_offset=0)]
