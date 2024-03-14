from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING is True:
    from interface.level import Level
    from interface.state import State
    from interface.typing import PositionType, AgentType, BoxType, AgentGoalType, BoxGoalType


class GoalDescription:
    level: Level
    goals: list[tuple[PositionType, str, bool]]
    agent_goals: list[AgentGoalType]
    box_goals: list[BoxGoalType]

    def is_goal(self, state: State) -> bool: ...

    def color_filter(self, color: str) -> GoalDescription: ...

    def get_sub_goal(self, index: int) -> GoalDescription: ...

    def num_sub_goals(self) -> int: ...

    def create_new_goal_description_of_same_type(
        self, goals: list[tuple[PositionType, str, bool]]
    ) -> GoalDescription: ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: GoalDescription) -> bool: ...

    def __hash__(self) -> int: ...
