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
Working with the robot agent type is slightly different from the previous agent types.
- First of all, you will need to install some additional packages 'numpy' and 'msgpack'.
  Both can be install using pip, e.g., 'pip install numpy msgpack'. The exact details might
  depend on your platform and Python installation.
- Secondly, we will not be using the Java server when working with the robot, and the command
  used to invoke the search client on the terminal is therefore slightly different for example:
    'python searchclient/searchclient.py -robot -ip 192.168.0.102 -level levels/SAsoko1_04.lvl'
  will run the searchclient using the 'robot' agent type, on the robot with the ip 192.168.0.102.
- In order to connect to the robots, you need to be connected to the R2DTU hotspot. In order to
  reduce the load on this hotspot, please disconnect from this hotspot between your sessions.
- We have two robots, identifiable based upon the 'R1' and 'R2' on their tablets.
  The ip addresses of the two robots are
    R1: '192.168.0.105'
    R2: '192.168.0.106'
- A good start would be to start with something similar to the 'classic' agent type and then
  replace the 'print(joint_action_to_string(joint_action), flush=True)' with calls to the 'robot'
  interface.
"""
import math

from search.domain import Level, ActionSet
from robot.robot_interface import RobotInterface
from search.frontiers import Frontier

def robot_agent(
    level: Level,
    action_library: ActionSet,
    frontier: Frontier,
    robot: RobotInterface,
):
    # Get the initial state and goal description from the level
    initial_state = level.initial_state()
    goal_description = level.goal_description()

    # You can delete the following line (it is used to silence the type checker)
    _ = initial_state, goal_description
    
    # Write your robot agent type here
    # What follows is a small example of how to interact with the robot.
    # You should browse through 'robot_interface.py' to get a full overview of all the available functionality

    # Wake up robot, if you are the first to use it, and run motor check
    robot.wake_up()

    # Communicate using its speech synthesis
    robot.say("Hello I am Pepper!")

    # Pre-scripted animation
    robot.perform_animation("animations/Stand/Gestures/Hey_1")

    # Drive 0.5 meter forward
    robot.move(0.5, 0.0)
    # Turn around 90 degrees (pi/2 radians)
    robot.turn(math.pi / 2.0)
    # Drive 0.5 meter to the left
    robot.move(0.0, 0.5)
    # Turn back 90 degrees (-pi/2 radians)
    robot.turn(-math.pi / 2.0)
