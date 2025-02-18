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
This module contains functions for the agents to communicate with the server.
They are simply wrappers around the standard input and output streams (stdin and stdout).
"""
import sys

from search.domain.actions import JointAction


def send_joint_action(joint_action: JointAction) -> list[bool]:
    """
    Sends a joint action to the server and reads back the success status of each action.
    """
    print(joint_action_to_string(joint_action), flush=True)
    return parse_response(read_line())


def joint_action_to_string(joint_action: JointAction) -> str:
    """
    Converts a joint action to its representation.
    """
    joint_action_names = (action.name for action in joint_action)
    return "|".join(joint_action_names)


def parse_response(response: str) -> list[bool]:
    """
    Converts a response string from the server to a list of booleans denoting
    the success status of each action in the previously submitted joint action.
    """
    return [part == "true" for part in response.split("|")]


def read_line() -> str:
    """
    Reads a line from the server via stdin.
    """
    return sys.stdin.readline().rstrip()
