import ast
import tokenize
from contextlib import suppress
from os import PathLike

from module_level_lint.utils import is_module_docstring, is_future_import, is_dunder


def trim_lines(tokens: list[str], end_line: int) -> None:
    with suppress(IndexError):
        if tokens[end_line] != "\n":
            tokens[end_line - 1] += "\n"
            return

    for i, token in enumerate(tokens[end_line + 1 :], start=end_line):
        if not token.isspace():
            break
        tokens[i] = ""


class LazyVisitor(ast.NodeVisitor):
    def __init__(self, tree: ast.AST):
        self.tree = tree

        self.docstring_lines = []
        self.future_import_lines = []
        self.module_dunder_lines = []

    def visit_Module(self, node: ast.Module):
        for body in node.body:
            if is_module_docstring(body):
                self.docstring_lines.append((body.lineno, body.end_lineno))
            elif is_future_import(body):
                self.future_import_lines.append((body.lineno, body.end_lineno))
            elif is_dunder(body):
                self.module_dunder_lines.append((body.lineno, body.end_lineno))


def lazy_format(
    filename: str | PathLike, tree: ast.AST, write: bool = True
) -> str | bool:
    """
    Only formats the newlines in module level

    :return: formatted content or None depending on `write`
    """
    tokens: list[str] = list(tokenize.open(filename))
    src = "".join(tokens)

    visitor = LazyVisitor(tree)
    visitor.visit(tree)

    for i, token in enumerate(tokens):
        if not token.isspace():
            break
        tokens[i] = ""

    if visitor.docstring_lines:
        end_line = visitor.docstring_lines[-1][1]
        trim_lines(tokens, end_line)

    if visitor.future_import_lines:
        end_line = visitor.future_import_lines[-1][1]
        trim_lines(tokens, end_line)

    if visitor.module_dunder_lines:
        end_line = visitor.module_dunder_lines[-1][1]
        trim_lines(tokens, end_line)

    formatted = "".join(tokens)

    if not write:
        return formatted

    with open(filename, "w") as f:
        f.write(formatted)

    return src == formatted
