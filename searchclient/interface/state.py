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

from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING is True:
    from interface.actions import Action
    from interface.level import Level
    from interface.typing import PositionType, AgentType, BoxType


class State(Protocol):
    level: Level
    agent_positions: list[AgentType]
    box_positions: list[BoxType]
    parent: State | None
    path_cost: int

    def agent_at(self, position: PositionType) -> AgentType: ...

    def box_at(self, position: PositionType) -> BoxType: ...

    def object_at(self, position: PositionType) -> str: ...

    def free_at(self, position: PositionType) -> bool: ...

    def extract_plan(self) -> list[Action]: ...

    def is_conflicting(self, joint_action: list[Action]) -> bool: ...

    def result(self, joint_action: list[Action]) -> State: ...

    def result_of_plan(self, plan: list[list[Action]]) -> State: ...

    def is_applicable(self, joint_action: list[Action]) -> bool: ...

    def get_applicable_actions(self, action_set: list[list[Action]]) -> list[Action]: ...

    def color_filter(self, color: str) -> State: ...

    def __repr__(self) -> str: ...
        
    def __eq__(self, other: State) -> bool: ...

    def __ne__(self, other: State) -> bool: ...

    def __hash__(self) -> int: ...
