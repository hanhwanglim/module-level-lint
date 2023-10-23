import re
import ast
import importlib.metadata
from enum import IntEnum
from typing import Any, Generator

DUNDER_PATTERN = r"^__[a-zA-Z_]\w*__$"


class Error:
    MLL001 = "MLL001 Module level docstring appears after code"
    MLL002 = "MLL002 Module level future-imports appears after module level dunders"
    MLL003 = "MLL003 Module level future-imports appears after code"
    MLL004 = "MLL004 Module level dunders appears after code"


class NodeType(IntEnum):
    UNINITIALIZED = 0
    MODULE_DOCSTRING = 1
    FUTURE_IMPORT = 2
    MODULE_DUNDER = 3
    OTHER_CODE = 4


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
    if isinstance(node, ast.Import) and "__future__" in [
        name.name for name in node.names
    ]:
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


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: [tuple[int, int, str]] = []

    def visit_Module(self, node: ast.Module) -> None:
        seen_node_type = NodeType.UNINITIALIZED

        for body in node.body:
            if is_module_docstring(body):
                seen_node_type = max(seen_node_type, NodeType.MODULE_DOCSTRING)
                curr_node_type = NodeType.MODULE_DOCSTRING
            elif is_future_import(body):
                seen_node_type = max(seen_node_type, NodeType.FUTURE_IMPORT)
                curr_node_type = NodeType.FUTURE_IMPORT
            elif is_dunder(body):
                seen_node_type = max(seen_node_type, NodeType.MODULE_DUNDER)
                curr_node_type = NodeType.MODULE_DUNDER
            else:
                seen_node_type = max(seen_node_type, NodeType.OTHER_CODE)
                curr_node_type = NodeType.OTHER_CODE

            self.check(body, curr_node_type, seen_node_type)

        self.generic_visit(node)

    def check(self, node: ast.stmt, node_type: NodeType, seen: NodeType) -> None:
        if node_type == NodeType.MODULE_DOCSTRING and seen > NodeType.MODULE_DOCSTRING:
            self.errors.append((node.lineno, node.col_offset, Error.MLL001))
        elif node_type == NodeType.FUTURE_IMPORT and seen == NodeType.MODULE_DUNDER:
            self.errors.append((node.lineno, node.col_offset, Error.MLL002))
        elif node_type == NodeType.FUTURE_IMPORT and seen == NodeType.OTHER_CODE:
            self.errors.append((node.lineno, node.col_offset, Error.MLL003))
        elif node_type == NodeType.MODULE_DUNDER and seen == NodeType.OTHER_CODE:
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
