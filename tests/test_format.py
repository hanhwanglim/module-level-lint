import ast

from module_level_lint.format import lazy_format
from tests import FIXTURES


class TestLazyFormat:
    def test_trivial(self):
        with open(FIXTURES / "trivial.py") as f:
            tree = ast.parse(f.read())
            f.seek(0)
            assert lazy_format(f.name, tree, write=False) == ""

    def test_clean(self):
        with open(FIXTURES / "clean.py") as f:
            tree = ast.parse(f.read())
            f.seek(0)
            assert lazy_format(f.name, tree, write=False) == f.read()

    def test_fix_clean(self):
        with (
            open(FIXTURES / "format" / "fix_clean.py") as f,
            open(FIXTURES / "clean.py") as f2,
        ):
            tree = ast.parse(f.read())
            f.seek(0)
            assert lazy_format(f.name, tree, write=False) == f2.read()
