from typing import NewType

PositionType = NewType('Position', tuple[int, int])

AgentType = NewType('Agent', tuple[PositionType, str])
BoxType = NewType('Box', tuple[PositionType, str])

AgentGoalType = NewType('AgentGoal', tuple[PositionType, str, bool])
BoxGoalType = NewType('BoxGoal', tuple[PositionType, str, bool])
