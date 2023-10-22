import dataclasses
import re
import ast
import importlib.metadata
from typing import Any, Generator, Optional

DUNDER_PATTERN = r"^__[a-zA-Z_]\w*__$"


class Error:
    MLL001 = "MLL001 Module level docstring appears after code"
    MLL002 = "MLL002 Module level future-imports appears after module level dunders"
    MLL003 = "MLL003 Module level future-imports appears after code"
    MLL004 = "MLL004 Module level dunders appears after code"


def is_module_docstring(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Expr):
        return False
    node = node.value
    if not isinstance(node, ast.Str):
        return False
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return False
    return True


def is_future_import(node: ast.stmt) -> bool:
    if not isinstance(node, (ast.Import, ast.ImportFrom)):
        return False
    if isinstance(node, ast.Import) and "__future__" in [name.name for name in node.names]:
        return True
    if isinstance(node, ast.ImportFrom) and node.module == "__future__":
        return True
    return False


def is_dunder(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Assign):
        return False
    for target in node.targets:  # type: ast.Name
        if re.match(DUNDER_PATTERN, target.id):
            return True
    return False


def is_code(node: ast.stmt) -> bool:
    return not (is_module_docstring(node) or is_future_import(node) or is_dunder(node))


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: [tuple[int, int, str]] = []

    def visit_Module(self, node: ast.Module) -> None:
        seen = 0

        for body in node.body:
            if is_module_docstring(body):
                seen = max(seen, 1)
            if is_future_import(body):
                seen = max(seen, 2)
            if is_dunder(body):
                seen = max(seen, 3)
            if is_code(body):
                seen = max(seen, 4)
            self.check(body, seen)

        self.generic_visit(node)

    def check(self, node: ast.stmt, seen: int) -> None:
        if is_module_docstring(node) and seen > 1:
            self.errors.append((node.lineno, node.col_offset, Error.MLL001))
            return
        if is_future_import(node) and seen == 3:
            self.errors.append((node.lineno, node.col_offset, Error.MLL002))
            return
        if is_future_import(node) and seen == 4:
            self.errors.append((node.lineno, node.col_offset, Error.MLL003))
            return
        if is_dunder(node) and seen > 3:
            self.errors.append((node.lineno, node.col_offset, Error.MLL004))
            return


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
