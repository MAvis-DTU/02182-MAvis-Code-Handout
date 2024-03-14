from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


from interface.typing import PositionType

if TYPE_CHECKING is True:
    from interface.state import State


class Action(Protocol):
    name: str

    def is_applicable(self, agent_index: int, state: State) -> bool: ...

    def result(self, agent_index: int, state: State) -> None: ...

    def conflicts(
        self, agent_index: int, state: State
    ) -> tuple[list[PositionType], list[PositionType]]: ...

    def __repr__(self) -> str: ...
