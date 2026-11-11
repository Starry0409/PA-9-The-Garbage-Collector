
import threading
from collections import deque
from typing import Any

from gc_heap import GCHeap


_CLOSED_SENTINEL = object()


class Channel:
    CLOSED = _CLOSED_SENTINEL

    def __init__(self, capacity: int, heap: GCHeap) -> None:
        if capacity < 0:
            raise ValueError("Capacity cannot be negative")

        self.capacity = capacity
        self.heap = heap
        self.buffer = deque()
        self.condition = threading.Condition()
        self.closed = False

    def put(self, value: Any) -> None:
    
        with self.condition:

            if self.closed:
                raise RuntimeError("Cannot put into a closed channel")

            # Capacity 0 means unbounded.
            while (
                self.capacity > 0
                and len(self.buffer) >= self.capacity
            ):
                self.condition.wait()

                if self.closed:
                    raise RuntimeError("Cannot put into a closed channel")

            self.heap.incref(value)

            self.buffer.append(value)

            self.condition.notify_all()

    def get(self):

        with self.condition:

            while len(self.buffer) == 0:

                if self.closed:
                    return Channel.CLOSED

                self.condition.wait()

            value = self.buffer.popleft()

            self.condition.notify_all()

            return value

    def close(self) -> None:
    
        with self.condition:
            self.closed = True
            self.condition.notify_all()


def producer_consumer_driver(
    heap: GCHeap,
    values: list,
    channel: Channel,
    num_consumers: int = 1
):


    delivered = []
    delivered_lock = threading.Lock()

    def produce():
        try:
            for v in values:

                handle = heap.allocate(v)

                try:
                    channel.put(handle)

                finally:
                    heap.decref(handle)

        finally:
            channel.close()

    def consume():
        while True:

            handle = channel.get()

            if handle is Channel.CLOSED:
                return

            try:
                value = heap._objects[handle][0]

                with delivered_lock:
                    delivered.append((handle, value))

            finally:
                heap.decref(handle)

    producer_thread = threading.Thread(target=produce)

    consumer_threads = [
        threading.Thread(target=consume)
        for _ in range(num_consumers)
    ]

    producer_thread.start()

    for t in consumer_threads:
        t.start()

    producer_thread.join()

    for t in consumer_threads:
        t.join(timeout=10.0)

    return delivered


# Example test
if __name__ == "__main__":

    heap = GCHeap()

    channel = Channel(capacity=2, heap=heap)

    values = [10, 20, 30, 40, 50]

    results = producer_consumer_driver(
        heap,
        values,
        channel,
        num_consumers=2
    )

    print("PA 10: Channels")
    print("--------------------")

    for handle, value in results:
        print(f"Handle: {handle}, Value: {value}")

    print("--------------------")
    print("Total delivered:", len(results))
    print("Channel closed:", channel.closed)
    print("Remaining buffer:", list(channel.buffer))
