import ast

import pytest

from module_level_lint.utils import is_module_docstring, is_dunder, is_future_import


@pytest.mark.parametrize(
    ["code", "expected"],
    [
        pytest.param("'hello world'", True, id="str"),
        pytest.param("'''hello world'''", True, id="docstr"),
        pytest.param("if True: ...", False, id="stmt"),
        pytest.param("x = 1", False, id="assign"),
    ],
)
def test_is_module_docstring(code: str, expected: bool) -> None:
    has_docstring = False
    for node in ast.walk(ast.parse(code)):
        has_docstring = has_docstring or is_module_docstring(node)
    assert has_docstring == expected


@pytest.mark.parametrize(
    ["code", "expected"],
    [
        pytest.param("import __future__", True, id="future-import"),
        pytest.param("import __future__ as f", True, id="future-import alias"),
        pytest.param("from __future__ import division", True, id="future-importfrom"),
        pytest.param(
            "from __future__ import division as d", True, id="future-importfrom alias"
        ),
        pytest.param("import random", False, id="import"),
        pytest.param("import random as r", False, id="import alias"),
        pytest.param("from random import randint", False, id="importfrom"),
        pytest.param("from random import randint as r", False, id="importfrom alias"),
        pytest.param("x = 1", False, id="assign"),
    ],
)
def test_is_future_import(code: str, expected: bool) -> None:
    has_future_import = False
    for node in ast.walk(ast.parse(code)):
        has_future_import = has_future_import or is_future_import(node)
    assert has_future_import == expected


@pytest.mark.parametrize(
    ["code", "expected"],
    [
        pytest.param("__all__ = ['hello']", True, id="dunder assign"),
        pytest.param(
            "__all__, __doc__ = ['hello'], 'this is the doc'",
            True,
            id="dunder tuple assign",
        ),
        pytest.param(
            "__all__, x = ['hello'], 1", True, id="single dunder tuple assign"
        ),
        pytest.param(
            "[__all__, __doc__] = ['hello'], 'this is the doc'",
            True,
            id="dunder list assign",
        ),
        pytest.param("a.b = 1", False, id="attribute assign"),
        pytest.param("a[1:] = 1", False, id="subscript assign"),
        pytest.param("a, *b = [1, 2, 3]", False, id="starred assign"),
        pytest.param("a = 1", False, id="name assign"),
        pytest.param("[a, b] = [1, 2]", False, id="list assign"),
        pytest.param("a, b = 1, 2", False, id="tuple assign"),
        pytest.param("import random", False, id="statement"),
    ],
)
def test_is_dunder(code: str, expected: bool) -> None:
    has_dunder = False
    for node in ast.walk(ast.parse(code)):
        has_dunder = has_dunder or is_dunder(node)
    assert has_dunder == expected
