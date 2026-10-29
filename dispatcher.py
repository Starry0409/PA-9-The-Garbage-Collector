
from typing import Callable, Dict, Optional


class ClassDecl:
    __slots__ = ("name", "methods")

    def __init__(self, name: str, methods: Dict[str, Callable]) -> None:
        self.name = name
        self.methods = methods


class VTable:
    def __init__(self, entries: Dict[str, Callable], owning_class_name: str = "?") -> None:
        self.entries = dict(entries)
        self.owning_class_name = owning_class_name

    def resolve(self, method_name: str) -> Callable:
        if method_name not in self.entries:
            raise AttributeError(
                f"Class '{self.owning_class_name}' has no method '{method_name}'"
            )
        return self.entries[method_name]


def build_vtable(class_node: ClassDecl, parent_vtable: Optional[VTable] = None) -> VTable:
    entries = dict(parent_vtable.entries) if parent_vtable else {}
    entries.update(class_node.methods)
    return VTable(entries, class_node.name)


class USIObject:
    def __init__(self, class_descriptor: VTable, fields: dict) -> None:
        self.class_descriptor = class_descriptor
        self.fields = fields


def dispatch(obj: USIObject, method_name: str, args: list, caller_env) -> object:
    method = obj.class_descriptor.resolve(method_name)
    return method(obj, *args)
