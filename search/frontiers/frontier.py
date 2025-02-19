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
from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Hashable
from typing import Any

from search.domain.goal_description import GoalDescription


class Frontier[T: Hashable](ABC):
    """
    Abstract base class for implementing frontiers.

    To implement a concrete subclass of Frontier, the following methods must
    be provided: `_add`, `_pop`, and `_clear`. For an example implementation,
    see BFSFrontier.

    Maintains a multiset (Counter) of states for efficient membership checks.

    For those unfamiliar with abstract classes and generics, you don't have to
    know about it to be able to write frontiers, but here's a summary:

    An Abstract Base Class (ABC) contains one or more abstract methods, in this
    case `_add`, `_pop`, and `_clear`. As long as a class has an abstract
    method, it cannot be instantiated, so the code `frontier = Frontier()`
    would fail. Subclasses should define these methods to allow them to be
    instantiated, such as `BFSFrontier` does. This way, we can define all the
    common frontier methods in this class, and let the subclasses only care
    about the behaviour that is specific to them, e.g. FIFO/LIFO queues for
    BFS/DFS frontiers.
    """

    def __init__(self):
        self.counter = Counter[T]()

    @abstractmethod
    def _add(self, element: T, *args: Any):
        pass

    @abstractmethod
    def _pop(self) -> T:
        pass

    @abstractmethod
    def _clear(self) -> None:
        pass

    def prepare(self, goal_description: GoalDescription):
        """
        Called before each search to clear the frontier and set the
        goal description.
        """
        self.goal_description = goal_description
        self._clear()
        self.counter.clear()

    def add(self, element: T, *args: Any, **kwargs: Any):
        """
        Add an element to the frontier. Can take additional arguments if needed
        for e.g. supplying a priority for a priority queue.
        """
        self._add(element, *args, **kwargs)
        self.counter[element] += 1

    def pop(self) -> T:
        """
        Retrieve and remove an element from the frontier.
        """
        element = self._pop()
        self.counter[element] -= 1
        if not self.counter[element]:
            del self.counter[element]
        return element

    def is_empty(self) -> bool:
        """
        Whether the frontier is empty.

        `frontier.is_empty()` is equivalent to `not frontier`.
        """
        return not self

    def size(self) -> int:
        """
        The number of elements in the frontier.

        Included for backwards compatibility, use `len(frontier)` instead.
        """
        return len(self)

    def contains(self, element: T) -> bool:
        """
        Whether the frontier contains the given state.

        Included for backwards compatibility, use `state in frontier` instead.
        """
        return element in self

    def __len__(self):
        return self.counter.total()

    def __bool__(self):
        return bool(self.counter)

    def __contains__(self, element: T):
        return element in self.counter

    def __repr__(self):
        return f"{type(self).__name__}[size={len(self)}]"
