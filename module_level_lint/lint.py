import ast
from enum import IntEnum


from module_level_lint.error import Error
from module_level_lint.utils import is_module_docstring, is_future_import, is_dunder


class NodeType(IntEnum):
    UNINITIALIZED = 0
    MODULE_DOCSTRING = 1
    FUTURE_IMPORT = 2
    MODULE_DUNDER = 3
    OTHER_CODE = 4


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[tuple[int, int, str]] = []

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
