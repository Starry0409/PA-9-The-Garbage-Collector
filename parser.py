"""
PA 5 dependency: paste in YOUR OWN completed PA 3 parser.py here
(needed transitively -- symtable.py imports from this file).

Complete the parsing functions below. AST node types are already
defined -- do not modify them. See the assignment,
Part B, for the full requirements.
"""

from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:
    """Given: a mutable box. Two names that share the SAME Cell are aliased."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:
    """Given: a minimal function declaration -- params and a single expr body."""

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    """Given: evaluate a PA3 expression AST node against `env` (Cells are transparently dereferenced)."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    """Given: write `value` into whatever Cell `name` resolves to (mutates in place, does not rebind)."""
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    cell.value = value


def bind_parameters(param_specs: List[Tuple[str, str]], arg_nodes: list, caller_env: Environment, callee_record) -> None:
    """
    Populate callee_record.locals_env according to each parameter's
    mode ("value", "reference", or "value-result"). For value-result
    parameters, also record what commit_value_result needs to do the
    delayed write-back later -- store it whichever way you like (e.g.
    an attribute on callee_record such as callee_record.pending_writeback).
    """
    # TODO
    raise NotImplementedError


def commit_value_result(callee_record, caller_env: Environment) -> None:
    """
    For every value-result parameter bound by bind_parameters on this
    callee_record, copy its FINAL local value back into the caller's
    corresponding variable now (call this only after the callee's body
    has finished running).
    """
    # TODO
    raise NotImplementedError


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        # TODO
        raise NotImplementedError

    def call(self, args: list, caller_env: Environment):
        """
        Create the callee Environment as a child of self.defining_env
        (NOT caller_env) -- this is what makes closure capture work.
        Bind each declaration.params[i] to args[i] (already-evaluated
        values, wrapped in a Cell), then evaluate declaration.body in
        that new environment and return the result.
        """
        # TODO
        raise NotImplementedError
