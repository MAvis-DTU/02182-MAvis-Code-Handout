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

from collections import deque

from search.frontiers.frontier import Frontier


class BFSFrontier[T](Frontier[T]):
    """
    A frontier for Breadth First Search algorithms.
    """

    def __init__(self):
        super().__init__()
        self.queue = deque()

    def _add(self, state: T):
        self.queue.append(state)

    def _pop(self) -> T:
        return self.queue.popleft()

    def _clear(self):
        self.queue.clear()
