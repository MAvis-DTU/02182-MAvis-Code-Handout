from typing import Protocol
from abc import abstractmethod

import domains.hospital.goal_description as h_goal_description
import domains.hospital.state as h_state


class Frontier(Protocol):
    @abstractmethod
    def prepare(self, goal_description: h_goal_description.HospitalGoalDescription) -> None:
        ...

    @abstractmethod
    def add(self, state: h_state.HospitalState) -> None:
        ...

    @abstractmethod
    def pop(self) -> h_state.HospitalState:
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        ...
    
    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def contains(self, state: h_state.HospitalState) -> bool:
        ...
