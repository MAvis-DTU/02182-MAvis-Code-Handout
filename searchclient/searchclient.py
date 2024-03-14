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

import argparse
import memory
import re
import sys
from agent_types.classic import classic_agent_type
from agent_types.decentralised import decentralised_agent_type
from agent_types.helper import helper_agent_type
from agent_types.non_deterministic import non_deterministic_agent_type
from domains.hospital import *
from strategies.bfs import FrontierBFS
from strategies.dfs import FrontierDFS
from strategies.bestfirst import FrontierAStar, FrontierGreedy

from utils import read_line

def load_level_file_from_server():
    lines = []
    while True:
        line = read_line()
        lines.append(line)
        if line.startswith("#end"):
            break
    return lines


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='Search-client for MAvis using state-space graph search.')

    parser.add_argument('--max-memory', metavar='<GB>', type=str, default="4g",
                        help='The maximum memory usage allowed in GB (soft limit, default 4g).')


    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument('-bfs', action='store_const', dest='strategy', const='bfs',
                                help='Use the BFS strategy.')
    strategy_group.add_argument('-dfs', action='store_const', dest='strategy', const='dfs',
                                help='Use the DFS strategy.')
    strategy_group.add_argument('-astar', action='store_const', dest='strategy', const='astar',
                                help='Use the A* strategy.')
    strategy_group.add_argument('-greedy', action='store_const', dest='strategy', const='greedy',
                                help='Use the Greedy strategy.')

    heuristic_group = parser.add_mutually_exclusive_group()
    heuristic_group.add_argument('-goalcount', action='store_const', dest='heuristic', const='goalcount',
                                 help='Use a goal count heuristic.')
    heuristic_group.add_argument('-advancedheuristic', action='store_const', dest='heuristic', const='advanced',
                                 help='Use an advanced heuristic.')

             

    agent_type_group = parser.add_mutually_exclusive_group()
    agent_type_group.add_argument('-classic', action='store_const', dest='agent_type', const='classic',
                                  help='Use a classic centralized agent type.')
    agent_type_group.add_argument('-decentralised', action='store_const', dest='agent_type', const='decentralised',
                                  help='Use a decentralised agent type.')
    agent_type_group.add_argument('-helper', action='store_const', dest='agent_type', const='helper',
                                  help='Use a helper agent type.')
    agent_type_group.add_argument('-nondeterministic', action='store_const', dest='agent_type', const='nondeterministic',
                                  help='Use a non deterministic agent type.')

    args = parser.parse_args()

    # Set max memory usage allowed (soft limit).
    max_memory_gb_match = re.match(r"([0-9]+)g", args.max_memory)
    if max_memory_gb_match is None:
        print(f"Failed to parse max memory: {args.max_memory}. Should be e.g. 8g to indicate 8 GB")
        sys.exit(-1)
    max_memory_gb = int(max_memory_gb_match.group(1))
    memory.max_usage = max_memory_gb * 1024 * 1024 * 1024

    return args.strategy, args.heuristic, args.agent_type


if __name__ == '__main__':

    strategy_name, heuristic_name, agent_type_name = parse_command_line_arguments()

    # Construct client name by removing all missing arguments and joining them together into a single string
    name_components = [agent_type_name, strategy_name, heuristic_name]
    client_name = " ".join(filter(lambda name: name is not None, name_components))

    # Send client name to server
    print(client_name, flush=True)

    # Load the level from the server
    level_lines = load_level_file_from_server()
    # Domain name is always second line in file
    domain_name = level_lines[1]


    # Setup domain specific structures
    level = None
    initial_state = None
    action_library = None
    goal_description = None
    heuristic = None
    if domain_name == 'hospital':
        level = HospitalLevel.parse_level_lines(level_lines)
        initial_state = HospitalState(level, level.initial_agent_positions, level.initial_box_positions)
        goal_description = HospitalGoalDescription(level, level.box_goals + level.agent_goals)

        # Construct the requested action library
        action_library = DEFAULT_HOSPITAL_ACTION_LIBRARY
        if initial_state.level.num_boxes == 0: # Remove pull and push actions if there are no boxes
            action_library = [
                action for action in action_library 
                if not isinstance(action, PullAction) \
                and not isinstance(action, PushAction)
            ]

        # Construct the requested heuristic
        if heuristic_name == 'goalcount':
            heuristic = HospitalGoalCountHeuristics()
        elif heuristic_name == 'advanced':
            heuristic = HospitalAdvancedHeuristics()

    # Some heuristics needs to preprocess the level to pre-compute distance lookup tables, matchings, etc.
    if heuristic is not None:
        heuristic.preprocess(level)

    # Construct the requested frontier
    frontier = None

    # If no specific strategy is requested, we implicitly assume it to be a BFS
    if strategy_name is None:
        strategy_name = 'bfs'

    if strategy_name == 'bfs':
        frontier = FrontierBFS()
    elif strategy_name == 'dfs':
        frontier = FrontierDFS()
    elif strategy_name == 'astar':
        frontier = FrontierAStar(heuristic)
    elif strategy_name == 'greedy':
        frontier = FrontierGreedy(heuristic)
    else:
        print(f"Unrecognized strategy {strategy_name}", file=sys.stderr)

    # If no specific agent type is requested, we implicitly assume it to be the "classic" type
    if agent_type_name is None:
        agent_type_name = 'classic'

    # Run the requested agent type
    if agent_type_name == 'classic':
        classic_agent_type(level, initial_state, action_library, goal_description, frontier)
    elif agent_type_name == 'decentralised':
        decentralised_agent_type(level, initial_state, action_library, goal_description, frontier)
    elif agent_type_name == 'helper':
        helper_agent_type(level, initial_state, action_library, goal_description, frontier)
    elif agent_type_name == 'nondeterministic':
        non_deterministic_agent_type(level, initial_state, action_library, goal_description)
    else:
        print(f"Unrecognized agent type! {agent_type_name}", file=sys.stderr)

