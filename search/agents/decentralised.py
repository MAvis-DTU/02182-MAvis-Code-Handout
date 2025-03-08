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
from search import print_debug
from search.domain import Level
from search.domain.actions import NoOp, ActionLibrary

from search.algorithms.graph_search import graph_search
from search.frontiers.frontier import Frontier
from search.agents.server_communication import send_joint_action

def decentralised_agent(
    level: Level,
    action_library: ActionLibrary,
    frontier: Frontier,
):
    """
    
    """
    # Get the initial state and goal description from the level
    initial_state = level.initial_state()
    goal_description = level.goal_description()

    # Create an action set where all agents can perform all actions
    action_set = [action_library] * level.num_agents

    # Here you should implement the DECENTRALISED-AGENTS algorithm.
    # You can use the 'classic' agent type as a starting point for how to communicate with the server, i.e.
    # use 'send_joint_action' to send a joint_action to the server which will read back an array of booleans indicating
    # whether each individual action in the joint action succeeded.
    raise NotImplementedError()
