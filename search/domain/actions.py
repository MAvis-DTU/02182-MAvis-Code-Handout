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
"""
Implementations of the actions that can be performed in the hospital domain by a single agent.
These actions are used to construct joint actions which are used in the search algorithms.

An action class must implement three types to be a valid action:

1. is_applicable(self, agent_index, state) which return a boolean describing whether this action is valid for
   the agent with 'agent_index' to perform in 'state' independently of any other action performed by other agents.
2. result(self, agent_index, state) which modifies the 'state' to incorporate the changes caused by the agent
   performing the action. Since we *always* call both 'is_applicable' and 'conflicts' prior to calling 'result',
   there is no need to check for correctness.
3. conflicts(self, agent_index, state) which returns information regarding potential conflicts with other actions
   performed concurrently by other agents. More specifically, conflicts can occur with regard to the following
   two invariants:
   1. Two objects may not have the same destination.
      Ex: '0  A1' where agent 0 performs Move(E) and agent 1 performs Push(W,W)
   2. Two agents may not move the same box concurrently,
      Ex: '0A1' where agent 0 performs Pull(W,W) and agent 1 performs Pull(E,E)

   In order to check for these, the conflict method should return two lists:
      1. destinations which contains all newly occupied cells.
      2. moved_boxes which contains the current position of boxes moved during the action, i.e. their position
         prior to being moved by the action.

Note that 'agent_index' is the index of the agent in the state.agent_positions list which is often but *not always*
the same as the numerical value of the agent character.
"""
from __future__ import annotations

from typing import Literal
from abc import ABC, abstractmethod

from search.domain.state import State
from search.domain.level import Position


Direction = Literal["N", "S", "E", "W"]
"""Type alias for the four cardinal directions."""


direction_deltas: dict[Direction, Position] = {
    "N": Position(-1, 0),
    "S": Position(1, 0),
    "E": Position(0, 1),
    "W": Position(0, -1),
}
"""Lookup table for the delta values of the four cardinal directions."""


type JointAction = tuple[Action]
type Plan = list[JointAction]
type ActionLibrary = list[Action]
type ActionSet = list[ActionLibrary]


class Action(ABC):
    name: str

    @abstractmethod
    def is_applicable(self, agent_index: int, state: State) -> bool:
        pass

    @abstractmethod
    def result(self, agent_index: int, state: State):
        pass

    @abstractmethod
    def conflicts(
        self, agent_index: int, state: State
    ) -> tuple[list[Position], list[Position]]:
        pass

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class NoOp(Action):
    def __init__(self):
        self.name = "NoOp"

    def is_applicable(self, agent_index: int, state: State) -> bool:
        # Optimization. NoOp can never change the state if we only have a single agent
        return len(state.agent_positions) > 1

    def result(self, agent_index: int, state: State):
        pass

    def conflicts(
        self, agent_index: int, state: State
    ) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        destinations = [current_agent_position]
        boxes_moved = []
        return destinations, boxes_moved


class Move(Action):
    def __init__(self, agent_direction: Direction):
        self.agent_delta = direction_deltas[agent_direction]
        self.name = f"Move({agent_direction})"

    def calculate_positions(self, current_agent_position: Position) -> Position:
        return current_agent_position + self.agent_delta

    def is_applicable(self, agent_index: int, state: State) -> bool:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        return state.free_at(new_agent_position)

    def result(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        state.agent_positions[agent_index] = (new_agent_position, agent_char)

    def conflicts(
        self, agent_index: int, state: State
    ) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        # New agent position is a destination because it is unoccupied before the action and occupied after the action.
        destinations = [new_agent_position]
        # Since a Move action never moves a box, we can just return the empty value.
        boxes_moved = []
        return destinations, boxes_moved


class Push(Action):
    def __init__(self, agent_direction: Direction, box_direction: Direction):
        self.agent_delta = direction_deltas[agent_direction]
        self.box_delta = direction_deltas[box_direction]
        self.name = f"Push({agent_direction},{box_direction})"

    def calculate_positions(self, current_agent_position: Position):
        new_agent_position = current_agent_position + self.agent_delta
        new_box_position = new_agent_position + self.box_delta
        return new_agent_position, new_box_position

    def is_applicable(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position, new_box_position = self.calculate_positions(
            current_agent_position
        )
        _, box_char = state.box_at(new_agent_position)
        return (
            box_char != ""
            and state.level.colors[box_char] == state.level.colors[agent_char]
            and state.free_at(new_box_position)
        )

    def result(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position, new_box_position = self.calculate_positions(
            current_agent_position
        )
        box_index, box_char = state.box_at(new_agent_position)
        state.agent_positions[agent_index] = (new_agent_position, agent_char)
        state.box_positions[box_index] = (new_box_position, box_char)

    def conflicts(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        old_box_position, new_box_position = self.calculate_positions(
            current_agent_position
        )
        destinations = [new_box_position]
        boxes_moved = [old_box_position]
        return destinations, boxes_moved


class Pull(Action):
    def __init__(self, agent_direction: Direction, box_direction: Direction):
        self.agent_delta = direction_deltas[agent_direction]
        self.box_delta = direction_deltas[box_direction]
        self.name = f"Pull({agent_direction},{box_direction})"

    def calculate_positions(self, current_agent_position: Position):
        current_box_position = current_agent_position - self.box_delta
        new_agent_position = current_agent_position + self.agent_delta
        return current_box_position, new_agent_position

    def is_applicable(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        current_box_position, new_agent_position = self.calculate_positions(
            current_agent_position
        )
        box_index, box_char = state.box_at(current_box_position)
        return (
            box_char != ""
            and state.level.colors[box_char] == state.level.colors[agent_char]
            and state.free_at(new_agent_position)
        )

    def result(self, agent_index: int, state: State):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        current_box_position, new_agent_position = self.calculate_positions(
            current_agent_position
        )
        box_index, box_char = state.box_at(current_box_position)
        state.agent_positions[agent_index] = (new_agent_position, agent_char)
        state.box_positions[box_index] = (current_agent_position, box_char)

    def conflicts(self, agent_index: int, state: State):
        current_agent_position, _ = state.agent_positions[agent_index]
        current_box_position, new_agent_position = self.calculate_positions(
            current_agent_position
        )
        destinations = [new_agent_position]
        boxes_moved = [current_box_position]
        return destinations, boxes_moved


# An action library for the multi agent pathfinding
DEFAULT_MAPF_ACTION_LIBRARY: ActionLibrary = [
    NoOp(),
    Move("N"),
    Move("S"),
    Move("E"),
    Move("W"),
]
"""Action library for the multi agent pathfinding (MAPF) domain. Note that there are no actions involving boxes."""

# An action library for the full hospital domain
DEFAULT_HOSPITAL_ACTION_LIBRARY: ActionLibrary = [
    NoOp(),
    
    Move("N"),
    Move("S"),
    Move("E"),
    Move("W"),
    
    Push("N", "N"),
    Push("N", "E"),
    Push("N", "W"),
    Push("S", "S"),
    Push("S", "E"),
    Push("S", "W"),
    Push("E", "N"),
    Push("E", "S"),
    Push("E", "E"),
    Push("W", "N"),
    Push("W", "S"),
    Push("W", "W"),
    
    Pull("N", "N"),
    Pull("N", "E"),
    Pull("N", "W"),
    Pull("S", "S"),
    Pull("S", "E"),
    Pull("S", "W"),
    Pull("E", "N"),
    Pull("E", "S"),
    Pull("E", "E"),
    Pull("W", "N"),
    Pull("W", "S"),
    Pull("W", "W"),
]
"""Default action library for the hospital domain."""

