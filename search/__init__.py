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
This documentation is for the `search` module itself. For documentation on the
CLI endpoint, see the README or run `python client.py -h`.

# Overview

The `search` module (when filled out with your solutions) implements all the
functionality needed to solve planning problems in the hospital domain. It
consists of 4 main submodules:

- `agents`:
- `algorithms`:
- `strategies`:
- `domain`:

Agents are the entities that interact with the MAvis server. They are responsible
for sending actions to the server and receiving responses on the success of those
actions.

Algorithms are the specific search algorithms used by the agents to solve the planning problems.

Strategies are the different frontier strategies that can be used in the search algorithms.

Domain contains the classes and functions that define the hospital domain, allowing the search
algorithms to use joint actions to generate new states.


```mermaid
graph LR;
    A[MAvis Server]--Action Successes-->B[Agent];
    B--Joint Actions-->A;
    B--Initial State-->C[Search Algorithm];
    C--Solution-->B;
```

This module also defines utilities for memory tracking and printing search status.
"""
import sys


def print_debug(*args, **kwargs):
    """
    Print a debug message to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)
