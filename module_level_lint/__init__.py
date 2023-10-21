import ast
import importlib.metadata
from typing import Any, Generator


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: [tuple[int, int, str]] = []

    def visit_Module(self, node: ast.Module) -> None:
        for body in node.body:
            pass


class Plugin:
    name = __name__
    version = importlib.metadata.version(__name__)

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self.tree)

        for lineno, col_offset, msg in visitor.errors:
            yield lineno, col_offset, msg, type(self)
