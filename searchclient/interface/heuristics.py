from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING is True:
    from interface.state import State
    from interface.level import Level
    from interface.goal_description import GoalDescription


class Heuristics(Protocol):
    def preprocess(self, level: Level) -> None: ...

    def h(
        self,
        state: State,
        goal_description: GoalDescription,
    ) -> int: ...
