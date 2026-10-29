
from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict = {}

    def define(self, name: str, line: int) -> None:
        if name in self._names:
            raise SemanticError(
                f"Variable '{name}' is already defined in this scope"
            )

        self._names[name] = line

    def resolve(self, name: str) -> int:
        if name in self._names:
            return self._names[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        raise SemanticError(f"Undefined variable '{name}'")


def check_program(ast: Program) -> Environment:
    env = Environment()

    def check_expr(node):
        if isinstance(node, Variable):
            env.resolve(node.name)

        elif isinstance(node, BinOp):
            check_expr(node.left)

            if node.right is not None:
                check_expr(node.right)

        elif isinstance(node, Number):
            return

    for stmt in ast.statements:
        if isinstance(stmt, Declaration):
            check_expr(stmt.expr)
            env.define(stmt.name, stmt.line)

        elif isinstance(stmt, Assignment):
            env.resolve(stmt.name)
            check_expr(stmt.expr)

    return env
