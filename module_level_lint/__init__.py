import argparse
import ast
import importlib.metadata
from typing import Any, Generator

from flake8.options.manager import OptionManager

from module_level_lint.lint import Visitor


class Plugin:
    name = __name__
    version = importlib.metadata.version(__name__)
    should_fix = False

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    @staticmethod
    def add_options(option_manager: OptionManager) -> None:
        option_manager.add_option(
            "--fix", action=argparse.BooleanOptionalAction, help="Fix code"
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        cls.should_fix = options.fix or False

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        if self.should_fix:
            # todo: implement fix
            yield from []

        visitor = Visitor()
        visitor.visit(self.tree)

        for lineno, col_offset, msg in visitor.errors:
            yield lineno, col_offset, msg, type(self)
