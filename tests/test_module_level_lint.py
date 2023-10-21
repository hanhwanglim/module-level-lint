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
