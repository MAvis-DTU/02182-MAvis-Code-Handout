from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING is True:
    from interface.typing import PositionType, AgentType, BoxType, AgentGoalType, BoxGoalType

class Level(Protocol):
    name: str
    walls: list[PositionType]
    colors: dict[str, str]
    agent_goals: list[AgentGoalType]
    box_goals: list[BoxGoalType]
    initial_agent_positions: list[AgentType]
    initial_box_positions: list[BoxType]

    num_agents: int
    num_boxes: int
    num_agent_goals: int
    num_box_goals: int
