# coding: utf-8
#
# Copyright 2021 The Technical University of Denmark
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import heapq
import itertools

from search.domain.heuristics import Heuristic
from search.frontiers.frontier import Frontier


class PriorityQueue[T]:
    """
    A priority queue which allows the priority of elements to be updated in
    constant time. This is therefore suitable for usage as the frontier in
    a best-first search.

    The elements are stored in a queue as a triplet (priority, count, element).
    Python sorts tuples by comparing the first position and if these tie
    progressing to the next position until it either finds a position in the
    tuples where they differ or all positions has been compared (in which case
    the two tuples are identical. By storing the priority in the first
    position, we ensures that the element with the lowest priority will be
    placed in the front of the queue. The second 'count' component is used to
    break ties when two elements have the same priority. By using a
    monotonically increasing counter we ensure that:

    1. In case of identical priorities elements are ordered by their
    insertion order (i.e. LIFO behaviour).
    2. Since all elements has a unique count, we can never have a tie and
    therefore never need to compare the element itself.

    The entry finder stores a reference to all elements which ensures that we
    later can access the entry.
    """

    def __init__(self):
        self.heap = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def add(self, element: T, priority: int):
        """
        Insert an element into the queue according to the priority.
        """
        count = next(self.counter)
        entry = [priority, -count, element]
        heapq.heappush(self.heap, entry)
        self.entry_finder[element] = entry

    def change_priority(self, element: T, new_priority: int):
        """
        Change priority of an element in the queue.

        We cannot change the priority of an element already on the heap as
        that would break the heap invariant. Instead we invalidate the
        current entry by replacing the element with None and then inserting
        the element again with the new priority.
        """
        entry = self.entry_finder.pop(element)
        entry[2] = None
        # Add new entry with new priority
        self.add(element, new_priority)

    def pop(self) -> T:
        """
        Retrive and remove an element from the queue.

        Since some of the elements in the queue might have been invalidated by
        the 'change_priority' method, we need to keep taking elements from the
        queue until we find a valid entry.
        """
        while True:
            entry = heapq.heappop(self.heap)
            if entry[2] is not None:
                break
        state = entry[2]
        self.entry_finder.pop(state)
        return state

    def clear(self):
        """
        Remove all elements from the priority queue.
        """
        self.heap.clear()
        self.entry_finder.clear()
        self.counter = itertools.count()

    def get_priority(self, element: T) -> int | None:
        """
        Get the priority of an element in the queue. Returns None if the
        element is not present.
        """
        entry = self.entry_finder.get(element)
        if entry is None:
            return None
        return entry[0]

    def __len__(self):
        return len(self.entry_finder)


class BestFirstFrontier[T](Frontier[T]):
    """
    A frontier for Best First Search algorithms.
    """

    def __init__(self, heuristic: Heuristic):
        super().__init__()
        self.heuristic = heuristic
        self.goal_description = None
        # Your code here...
        raise NotImplementedError()

    def _add(self, element: T):
        # Your code here...
        raise NotImplementedError()

    def _pop(self) -> T:
        # Your code here...
        raise NotImplementedError()

    def _clear(self) -> None:
        # Your code here...
        raise NotImplementedError()

    def f(self, element: T) -> int:
        raise NotImplementedError(
            "FrontierBestFirst should not be directly used. Instead use a subclass overriding f()"
        )


# The FrontierAStar and FrontierGreedy classes extend the FrontierBestFirst class, that is, they are
# exact copies of the above class but where the 'f' method is replaced.
class AStarFrontier[T](BestFirstFrontier[T]):
    def f(self, element: T) -> int:
        assert (
            self.goal_description is not None
        ), "Cannot evaluate heuristic without goal description!"
        # Your code here...
        raise NotImplementedError()


class GreedyFrontier[T](BestFirstFrontier[T]):
    def f(self, element: T) -> int:
        assert (
            self.goal_description is not None
        ), "Cannot evaluate heuristic without goal description!"
        # Your code here...
        raise NotImplementedError()
