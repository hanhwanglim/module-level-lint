import ast

import pytest

from module_level_lint.format import lazy_format
from tests import FIXTURES, TESTS


def assert_format(expected: str, actual: str, test_name: str) -> None:
    try:
        assert expected == actual
    except AssertionError:
        with open(TESTS / "artifacts" / test_name, "w") as f:
            f.write(actual)
        raise


class TestLazyFormat:
    def test_trivial(self, request: pytest.FixtureRequest) -> None:
        with open(FIXTURES / "trivial.py") as f:
            tree = ast.parse(f.read())
            # To keep mypy happy
            if isinstance(formatted := lazy_format(f.name, tree, write=False), int):
                raise ValueError
            assert_format("", formatted, request.node.name)

    @pytest.mark.parametrize(
        ["actual_file", "expected_file"],
        [
            pytest.param("class.py", "class_formatted.py", id="class"),
            pytest.param("function.py", "function_formatted.py", id="function"),
            pytest.param("newline.py", "newline_formatted.py", id="newline"),
            pytest.param("script.py", "script_formatted.py", id="script"),
        ],
    )
    def test_format(
        self, expected_file: str, actual_file: str, request: pytest.FixtureRequest
    ) -> None:
        with (
            open(FIXTURES / "format" / expected_file) as expected,
            open(FIXTURES / "format" / actual_file) as actual,
        ):
            expected_str, actual_str = expected.read(), actual.read()
            tree = ast.parse(actual_str)
            # To keep mypy happy
            if isinstance(
                formatted := lazy_format(actual.name, tree, write=False), int
            ):
                raise ValueError
            assert_format(expected_str, formatted, request.node.name)
