from typing import Protocol
from abc import abstractmethod

import domains.hospital.goal_description as h_goal_description
import domains.hospital.state as h_state

from interface.goal_description import GoalDescription
from interface.state import State


class Frontier(Protocol):
    @abstractmethod
    def prepare(self, goal_description: GoalDescription) -> None:
        ...

    @abstractmethod
    def add(self, state: State) -> None:
        ...

    @abstractmethod
    def pop(self) -> State:
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        ...
    
    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def contains(self, state: State) -> bool:
        ...

    def __len__(self) -> int:
        return self.size()
    
    def __contains__(self, state: State) -> bool:
        return self.contains(state)
