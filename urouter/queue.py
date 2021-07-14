try:
    import uheapq as heapq
except:
    import heapq

class Queue():
    _heap: list

    def __init__(self):
        """
        Initial a queue.
        """
        self._heap = heapq.heapify([])

    def push(self, item):
        heapq.heappush(self._heap, item)

    def pop(self) -> tuple:
        heapq.heappop(self._heap)
