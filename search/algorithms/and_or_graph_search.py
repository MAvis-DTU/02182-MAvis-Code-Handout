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
from typing import Callable

from search.domain import State
from search.domain.actions import ActionSet, JointAction
from search import print_debug


type Policy = dict[State, JointAction]

type ResultsFunction[S] = Callable[[S, JointAction], list[S]]

MAX_RECURSION = 496

def and_or_graph_search(
    initial_state: State,
    action_set: ActionSet,
    goal_test: Callable[[State], bool],
    results: ResultsFunction,
    iterative_deepening: bool = True,
    allow_cyclic: bool = False,
) -> tuple[int, Policy] | tuple[None, None]:
    # Here you should implement AND-OR-GRAPH-SEARCH. We are going to use a policy format, mapping from states to actions.
    # The algorithm should return a pair (worst_case_length, or_plan)
    # where the or_plan is a dictionary with states as keys and actions as values
    raise NotImplementedError()
