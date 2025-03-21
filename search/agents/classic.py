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
from search.domain import Level, ActionLibrary

from search.algorithms.graph_search import graph_search
from search.frontiers.frontier import Frontier
from search.agents.server_communication import send_joint_action


def classic_agent(
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

    planning_success, plan = graph_search(
        initial_state,
        action_set,
        goal_description,
        frontier,
    )

    assert planning_success, "Unable to solve level."
    
    print_debug(f"Found solution of length {len(plan)}")

    for joint_action in plan:
        # Send the joint action to the server, and read back whether the agents 
        # succeeded in performing the joint action
        execution_successes = send_joint_action(joint_action)
        # Uncomment the below line to print the executed actions to the command line for debugging purposes
        # print_debug(joint_action_to_string(joint_action))

        # Assert that none of the agents failed to execute their action.
        # This should not occur in classical planning, so if it does we abort immediately
        assert False not in execution_successes, "Execution failed! Stopping..."
