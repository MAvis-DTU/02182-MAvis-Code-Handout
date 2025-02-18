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
import os
import time
import psutil
from typing import Hashable

from search import print_debug
from search.frontiers.frontier import Frontier


class _MemoryTracker:
    def __init__(self) -> None:
        self._process = psutil.Process(os.getpid())
        self._max_usage = float('inf')

    def get_usage(self):
        return int(self._process.memory_info().rss)

    def set_max_usage(self, value: int):
        self._max_usage = value

    def is_exceeded(self):
        return self.get_usage() > self._max_usage


memory_tracker = _MemoryTracker()
"""Singleton instance of the _Memory class used to track memory usage."""


class _SearchTimer:
    def __init__(self) -> None:
        self._start_time = time.time()

    def start(self):
        """
        Sets the start time of the search timer to the current time.
        """
        self._start_time = time.time()

    def elapsed(self):
        """
        Returns the time elapsed since the start of the search timer.
        """
        return time.time() - self._start_time


search_timer = _SearchTimer()
"""Singleton instance of the _SearchTimer class used to track search time."""


def print_search_status[T: Hashable](expanded: set[T], frontier: Frontier[T]):
    """
    Print a status message to stderr with information about the current search.
    """
    time_spent_seconds = search_timer.elapsed()
    memory_usage_bytes = memory_tracker.get_usage()
    # Replacing the generated comma thousands separators with dots is neither pretty nor locale aware but none of
    # Pythons four different formatting facilities seems to handle this correctly!
    num_expanded = f"{len(expanded):8,d}".replace(",", ".")
    num_frontier = f"{len(frontier):8,d}".replace(",", ".")
    num_generated = f"{len(expanded) + len(frontier):8,d}".replace(",", ".")
    elapsed_time = f"{time_spent_seconds:3.3f}".replace(".", ",")
    memory_usage_mb = f"{memory_usage_bytes / (1024*1024):3.2f}".replace(".", ",")
    status_text = (
        f"#Expanded: {num_expanded}, #Frontier: {num_frontier}, #Generated: {num_generated},"
        f" Time: {elapsed_time} s, Memory: {memory_usage_mb} MB"
    )
    print_debug(status_text)
