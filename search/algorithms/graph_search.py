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

from search.domain.state import State
from search.domain.goal_description import GoalDescription
from search.frontiers.frontier import Frontier
from search.algorithms.monitoring import search_timer, memory_tracker, print_search_status
from search.domain.actions import Action, JointAction, ActionSet, Plan, Move


class Node:
    def __init__(self, state: State, parent: Node | None = None, action: Action | None = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = 0 if parent is None else parent.path_cost + 1

    def extract_plan(self) -> Plan:
        plan = []
        node = self
        while node.parent is not None:
            plan.append(node.action)
            node = node.parent
        return plan[::-1]

    def get_applicable_actions(self, action_set: ActionSet) -> ActionSet:
        return self.state.get_applicable_actions(action_set)

    def result(self, action: JointAction) -> Node:
        new_state = self.state.result(action)
        return Node(new_state, self, action)

    def __eq__(self, other: Node) -> bool:
        return self.state == other.state

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        return f"{self.state}"


# Note: This syntax below (<variable name>: <variable type>) is type hinting and is meant
# to make it easier for you to understand (now you know that `action_set` is a list of lists of
# actions!) but if it is confusing, you can just ignore it as it is only for documentation
def graph_search(
    initial_state: State,
    action_set: ActionSet,
    goal_description: GoalDescription,
    frontier: Frontier[Node],
) -> tuple[bool, Plan]:
    """
    In this function, you should implement the Graph-Search algorithm from R&N figure 3.7
    The algorithm should here return a (boolean, list) pair where the boolean denotes
    whether the algorithm successfully found a plan and the list is the found plan.
    In the case of "failure to find a solution" you should therefore return False, [].
    Some useful methods on the State class which you will need to use are:
    node.extract_plan() - Returns the list of actions used to reach this state.
    node.get_applicable_actions(action_set) - Returns a list containing the actions applicable in the state.
    node.result(action) - Returns the new node reached by applying the action to the current node.
    For the GoalDescription class, you will need to use
    goal_description.is_goal(state) - Returns true if the state is a goal state.
    For debugging, remember that you can use print(node, file=sys.stderr) to get a representation of the state.
    You should also take a look at the frontiers in the strategies folder to see which methods they expose
    """
    # Set start time
    search_timer.start()
    iterations = 0
    frontier.prepare(goal_description)

    root = Node(initial_state)

    return_fixed_solution = True
    
    if return_fixed_solution:
        return True, [
            [Move("S")],
            [Move("E")],
            [Move("S")],
            [Move("E")],
            [Move("N")],
            [Move("N")],
            [Move("W")],
            [Move("W")],
        ]
    frontier.add(root)
    expanded: set[State] = set()

    while True:
        # Print a progress status message every 10000 iterations
        if iterations % 10000 == 0 and iterations != 0:
            print_search_status(expanded, frontier)

        # Ensure that we do not use more memory than allowed
        if memory_tracker.is_exceeded():
            raise MemoryError("Maximum memory usage exceeded!")

        iterations += 1

        # Your code here...
        raise NotImplementedError()


