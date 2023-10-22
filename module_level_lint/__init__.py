import dataclasses
import re
import ast
import importlib.metadata
from typing import Any, Generator, Optional

DUNDER_PATTERN = r"^__[a-zA-Z_]\w*__$"


class Error:
    MLL001 = "Module level docstring appears after code"
    MLL002 = "Module level future-imports appears after module level dunders"
    MLL003 = "Module level future-imports appears after code"
    MLL004 = "Module level dunders appears after code"


@dataclasses.dataclass
class SeenStmt:
    module_docstring_idx: Optional[ast.stmt] = None
    future_import_idx: Optional[ast.stmt] = None
    module_dunder_idx: Optional[ast.stmt] = None
    code_idx: Optional[ast.stmt] = None

    def values(self) -> tuple[Optional[ast.stmt], Optional[ast.stmt], Optional[ast.stmt], Optional[ast.stmt]]:
        return self.module_docstring_idx, self.future_import_idx, self.module_dunder_idx, self.code_idx


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
    return "__future__" in [alias.name for alias in node.names]


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
        self.seen_stmt = SeenStmt()

    def visit_Module(self, node: ast.Module) -> None:
        for body in node.body:
            self.check_for_mll001(body)

        self.generic_visit(node)

    def check_for_mll001(self, node: ast.stmt) -> None:
        """MLL001: Module level docstring should be at the top of the file"""
        if is_module_docstring(node):
            self.seen_stmt.module_docstring_idx = node
            _, seen_future, seen_dunder, seen_code = self.seen_stmt.values()
            if seen_future or seen_dunder or seen_code:
                self.errors.append((node.lineno, node.col_offset, Error.MLL001))

    def check_for_mll002(self, node: ast.stmt) -> None:
        """MLL002: Module level future-imports should be at the top of the file"""
        if is_future_import(node):
            self.seen_stmt.future_import_idx = node
            _, _, seen_dunder, seen_code = self.seen_stmt.values()
            if seen_dunder or seen_code:
                self.errors.append((node.lineno, node.col_offset, Error.MLL002))

    def check_for_mll003(self, node: ast.stmt) -> None:
        """MLL003: Module level future-imports should be after module level docstrings"""
        if is_module_docstring(node):
            self.seen_stmt.module_docstring_idx = node
            _, seen_future, _, _ = self.seen_stmt.values()
            if seen_future:
                self.errors.append((node.lineno, node.col_offset, Error.MLL003))

    def check_for_mll004(self, node: ast.stmt) -> None:
        MLL004 = "Module level dunders should be at the top of the file"
        if is_dunder(node):
            self.seen_stmt.module_dunder_idx = node
            _, _, _, seen_code = self.seen_stmt.values()
            if seen_code:
                self.errors.append((node.lineno, node.col_offset, Error.MLL004))

    def check_for_mll005(self, node: ast.stmt) -> None:
        MLL005 = "Module level dunders should be after module level docstrings"
        if is_future_import(node):
            self.seen_stmt.module_dunder_idx = node
            _, _, seen_dunder, seen_code = self.seen_stmt.values()
            if seen_code:
                self.errors.append((node.lineno, node.col_offset, Error.MLL004))


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
