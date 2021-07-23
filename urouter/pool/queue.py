from ..typeutil import routetask


class Queue():
    _heap: list

    def __init__(self):
        """
        Initial a queue.
        """
        self._heap = []

    def push(self, weight: int, task: routetask):

        # Put higher weights at the last of the list
        # If the same weight appears,
        # the item to be added will be before the existing item

        # No sorting algorithm is needed here.

        length = len(self._heap)

        if length == 0:
            self._heap.append((weight, task))
            return

        for idx, (w, _) in enumerate(self._heap):
            if w > weight:
                # 你权重比我高, 排在你后面
                self._heap.insert(idx, (weight, task))
                return
            elif w == weight:
                # 和你权重一样高, 排在你后面
                self._heap.insert(idx, (weight, task))
                return
            elif idx == length - 1:
                # 已经到最后边了
                self._heap.append((weight, task))
                return

    def pop_task(self) -> routetask:
        """
        Pop the route-task, if have nothing, return None
        """
        # The higher value and the oldest connection will be at the end
        # so just pop it.
        
        return self._heap.pop()[1] if len(self._heap) else None
        
