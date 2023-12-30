import ast
import re

DUNDER_PATTERN = r"^__[a-zA-Z_]\w*__$"


def is_module_docstring(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Expr):
        return False
    expr = node.value
    if not isinstance(expr, ast.Str):
        return False
    if not isinstance(expr, ast.Constant) or not isinstance(expr.value, str):
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
    for target in node.targets:  # type: ast.AST
        for child_node in ast.walk(target):
            if isinstance(child_node, ast.Name) and re.match(
                DUNDER_PATTERN, child_node.id
            ):
                return True
    return False
