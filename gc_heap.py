
from typing import Any, List


class HeapNode:
    def __init__(self, **fields: Any) -> None:
        self.fields = fields

    def get_child_handles(self) -> List[int]:
        return [v for v in self.fields.values() if isinstance(v, int)]


class GCHeap:
    def __init__(self) -> None:
        self._objects = {}
        self._next_handle = 1

    def allocate(self, obj: Any) -> int:
        handle = self._next_handle
        self._next_handle += 1
        self._objects[handle] = [obj, 1]
        return handle

    def incref(self, handle: int) -> None:
        if handle not in self._objects:
            raise KeyError(f"Invalid handle: {handle}")
        self._objects[handle][1] += 1

    def decref(self, handle: int) -> None:
        if handle not in self._objects:
            raise KeyError(f"Invalid handle: {handle}")

        self._objects[handle][1] -= 1

        if self._objects[handle][1] == 0:
            obj = self._objects[handle][0]
            del self._objects[handle]

            if hasattr(obj, "get_child_handles"):
                for child in obj.get_child_handles():
                    self.decref(child)

    def is_alive(self, handle: int) -> bool:
        return handle in self._objects

    def live_count(self) -> int:
        return len(self._objects)
