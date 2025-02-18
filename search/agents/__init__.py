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
"""
This module contains a number of agents, which are used to solve search problems.
"""
from search.agents.classic import classic_agent
from search.agents.decentralised import decentralised_agent
from search.agents.helper import helper_agent
from search.agents.goal_recognition import goal_recognition_agent
from search.agents.non_deterministic import non_deterministic_agent
from search.agents.robot import robot_agent

__all__ = [
    "classic_agent",
    "decentralised_agent",
    "helper_agent",
    "goal_recognition_agent",
    "non_deterministic_agent",
    "robot_agent",
]