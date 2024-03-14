from typing import NewType

PositionType = NewType('PositionType', tuple[int, int])

AgentType = NewType('AgentType', tuple[PositionType, str])
BoxType = NewType('BoxType', tuple[PositionType, str])

GoalType = NewType('GoalType', tuple[PositionType, str, bool])
AgentGoalType = NewType('AgentGoalType', tuple[PositionType, str, bool])
BoxGoalType = NewType('BoxGoalType', tuple[PositionType, str, bool])
