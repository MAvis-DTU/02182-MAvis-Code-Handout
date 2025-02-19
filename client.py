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
import re
import debugpy

from search.algorithms.monitoring import memory_tracker

from search.agents import (
    classic_agent,
    decentralised_agent,
    helper_agent,
    non_deterministic_agent,
    goal_recognition_agent,
    robot_agent
)
from search.agents.server_communication import read_line
from search.domain.actions import DEFAULT_HOSPITAL_ACTION_LIBRARY
from search.domain import (
    Level,
    AdvancedHeuristic,
    GoalCountHeuristic,
)
from search.frontiers import BFSFrontier, DFSFrontier, AStarFrontier, GreedyFrontier
from robot.robot_interface import RobotInterface


def load_level_file_from_server():
    lines = []
    while True:
        line = read_line()
        lines.append(line)
        if line.startswith("#end"):
            break

    return lines


def load_level_file_from_path(path):
    with open(path, "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    return lines


def create_parser():
    parser = argparse.ArgumentParser(
        description="Search-client for MAvis using state-space graph search.\n"
                    "Example usage:\n"
                    "  python3 client.py classic --strategy bfs\n"
                    "  python3 client.py robot --ip 192.168.1.100 --strategy astar  --heuristic goalcount",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Global options
    parser.add_argument('--max-memory', metavar="<GB>", type=str, default="4g",
                        help="The maximum memory allowed (e.g., 4g for 4 GB).")
    parser.add_argument('--debug', action='store_true',
                        default=False, help='Enable debug mode.')
    parser.add_argument("--level", type=str, default="",
                        help="Load level file from the filesystem instead of the server")
    # Action library selection
    parser.add_argument(
        "--action-library",
        choices=["default"],
        default="default",
        help="Select the action library. Default is 'default'.",
    )

    subparsers = parser.add_subparsers(
        dest="agent_type",
        required=True,
        help="Select the agent type to use",
    )

    # Create a parent parser for strategy-related arguments
    strategy_parent = argparse.ArgumentParser(add_help=False)
    strategy_parent.add_argument(
        "--strategy",
        choices=["bfs", "dfs", "astar", "greedy"],
        default="bfs",
        help="Select the search strategy. Default is BFS."
    )
    strategy_parent.add_argument(
        "--heuristic",
        choices=["goalcount", "advanced"],
        help="Select the heuristic (only relevant for A* and Greedy)."
    )
    # Classic agent subcommand
    classic_parser = subparsers.add_parser(
        "classic",
        help="Use a classic centralized agent using graph search",
        parents=[strategy_parent]
    )

    # Decentralised agent subcommand
    decentralised_parser = subparsers.add_parser(
        "decentralised",
        help="Use a decentralised planning agent",
        parents=[strategy_parent]
    )

    # Helper agent subcommand
    helper_parser = subparsers.add_parser(
        "helper",
        help="Use a helper agent",
        parents=[strategy_parent]
    )

    # Non-deterministic agent subcommand
    nondet_parser = subparsers.add_parser(
        "nondeterministic",
        help="Use a non-deterministic agent using AND-OR graph search",
    )
    nondet_parser.add_argument(
        "--no-iterative-deepening",
        action="store_true",
        default=False,
        help="Disable iterative deepening"
    )

    # Goal recognition agent subcommand
    goalrec_parser = subparsers.add_parser(
        "goalrecognition",
        help="Use a goal recognition agent using the all optimal plans for the actor and AND-OR-GRAPH-SEARCH for the helper",
        parents=[strategy_parent]
    )

    # Robot agent subcommand
    robot_parser = subparsers.add_parser(
        "robot",
        help="A planning agent which forwards the actions to a connected pepper robot.",
        parents=[strategy_parent]
    )
    robot_parser.add_argument(
        "--ip", type=str, required=True, help="IP address of the physical robot"
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Set memory tracker (same as before)
    max_memory_match = re.match(r"([0-9]+)g", args.max_memory)
    if not max_memory_match:
        parser.error("Invalid max memory format. Use e.g. 4g for 4 GB.")
    max_memory_gb = int(max_memory_match.group(1))
    memory_tracker.set_max_usage(max_memory_gb * 1024 * 1024 * 1024)

    # Construct client name by removing all missing arguments and joining them together into a single string
    name_components = [
        args.agent_type,
        (strategy_name := getattr(args, "strategy", "")),
        (heuristic_name := getattr(args, "heuristic", "")),
        (action_library_name := getattr(args, "action_library")),
    ]
    client_name = " ".join([n for n in name_components if n is not None])

    # Send client name to server
    print(client_name, flush=True)

    if args.debug:
        debugpy.listen(("localhost", 1234))
        debugpy.wait_for_client()
        debugpy.breakpoint()

    # Load the level from the server unless level path is specified
    level_lines = (
        load_level_file_from_path(level_path)
        if (level_path := getattr(args, "level", None))
        else load_level_file_from_server()
    )
    # Domain name is always second line in file
    domain_name = level_lines[1]
    if domain_name != "hospital":
        raise ValueError(f"Invalid domain name: {domain_name}")

    # Construct the level object
    level = Level.parse_level_lines(level_lines)

    # Construct the requested action library
    action_library = None
    if action_library_name is None\
            or action_library_name == "default":
        action_library = DEFAULT_HOSPITAL_ACTION_LIBRARY

    # Construct the requested heuristic
    heuristic = None
    if heuristic_name == "goalcount":
        heuristic = GoalCountHeuristic()
    elif heuristic_name == "advanced":
        heuristic = AdvancedHeuristic()

    # Some heuristics needs to preprocess the level to pre-compute distance lookup tables, matchings, etc.
    if heuristic is not None:
        heuristic.preprocess(level)

    # Construct the requested frontier
    frontier = None
    if not strategy_name:  # When no frontier is required
        pass
    elif strategy_name == "bfs":
        frontier = BFSFrontier()
    elif strategy_name == "dfs":
        frontier = DFSFrontier()
    elif strategy_name == "astar":
        frontier = AStarFrontier(heuristic)
    elif strategy_name == "greedy":
        frontier = GreedyFrontier(heuristic)
    else:
        raise ValueError(f"Invalid strategy: {strategy_name}")

    # Run the requested agent type
    if (agent_type_name := getattr(args, "agent_type")) == "classic":
        classic_agent(level, action_library, frontier)
    elif agent_type_name == "decentralised":
        decentralised_agent(level, action_library, frontier)
    elif agent_type_name == "helper":
        helper_agent(level, action_library, frontier)
    elif agent_type_name == "nondeterministic":
        non_deterministic_agent(level, action_library, not getattr(
            args, "no_iterative_deepening", False))
    elif agent_type_name == "goalrecognition":
        goal_recognition_agent(level, action_library, frontier)
    elif agent_type_name == "robot":
        if not (robot_ip := getattr(args, "ip", None)):
            raise ValueError(
                "IP adress required when using the robot agent type!")
        robot = RobotInterface(robot_ip)
        try:
            robot_agent(level, action_library, frontier, robot)
        except Exception as e:
            print("Robot agent terminated with error", e)
            robot.shutdown()
            raise
        robot.shutdown()
    else:
        ValueError(f"Unrecognized agent type: {agent_type_name}")


if __name__ == "__main__":
    main()
