from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING is True:
    from interface.goal_description import GoalDescription
    from interface.state import State


class Frontier(Protocol):

    def __init__(self) -> None: ...

    def prepare(self, goal_description: GoalDescription) -> None: ...

    def add(self, state: State) -> None: ...

    def pop(self) -> State: ...

    def is_empty(self) -> bool: ...

    def size(self) -> int: ...

    def contains(self, state: State) -> bool: ...

    def __contains__(self, state: State) -> bool: ...