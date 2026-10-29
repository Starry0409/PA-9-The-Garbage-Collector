
from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:
    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:
    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
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

        return {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b
        }[node.op](left, right)

    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    cell = env.resolve(name)

    if not isinstance(cell, Cell):
        raise TypeError(
            f"'{name}' is not bound to a Cell -- did you forget to wrap it?"
        )

    cell.value = value


def bind_parameters(
    param_specs: List[Tuple[str, str]],
    arg_nodes: list,
    caller_env: Environment,
    callee_record
) -> None:
    if len(param_specs) != len(arg_nodes):
        raise ValueError("Parameter and argument counts do not match")

    callee_record.pending_writeback = []

    for (name, mode), arg in zip(param_specs, arg_nodes):
        if mode == "value":
            value = evaluate(arg, caller_env)
            callee_record.locals_env.define(name, Cell(value))

        elif mode == "reference":
            if not isinstance(arg, Variable):
                raise TypeError("Reference argument must be a variable")

            cell = caller_env.resolve(arg.name)

            if not isinstance(cell, Cell):
                raise TypeError("Reference argument must be a Cell")

            callee_record.locals_env.define(name, cell)

        elif mode == "value-result":
            if not isinstance(arg, Variable):
                raise TypeError("Value-result argument must be a variable")

            value = evaluate(arg, caller_env)
            callee_record.locals_env.define(name, Cell(value))
            callee_record.pending_writeback.append((name, arg.name))

        else:
            raise ValueError(f"Unknown parameter mode: {mode}")


def commit_value_result(callee_record, caller_env: Environment) -> None:
    for local_name, caller_name in getattr(
        callee_record, "pending_writeback", []
    ):
        value = callee_record.locals_env.resolve(local_name)

        if isinstance(value, Cell):
            value = value.value

        assign_through(caller_env, caller_name, value)


class Closure:
    def __init__(
        self,
        declaration: FunctionDecl,
        defining_env: Environment
    ) -> None:
        self.declaration = declaration
        self.defining_env = defining_env

    def call(self, args: list, caller_env: Environment):
        if len(args) != len(self.declaration.params):
            raise ValueError("Incorrect number of arguments")

        local_env = Environment(parent=self.defining_env)

        for name, value in zip(self.declaration.params, args):
            local_env.define(name, Cell(value))

        return evaluate(self.declaration.body, local_env)
