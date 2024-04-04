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
Using the robot agent type differs from previous agent types.
  - Firstly, install additional package 'msgpack'.
    Use pip for installation, like this: 
        'python -m pip install numpy msgpack'. 
    Exact steps may vary based on your platform and Python 
    installation. 
  - Secondly, you don't need the Java server for the robot. So, the command
    to start the search client in the terminal is different, for example:
        'python searchclient/searchclient.py -robot -ip 192.168.0.102 -level levels/SAsoko1_04.lvl'
    runs the searchclient with the 'robot' agent type on the robot at IP 192.168.0.102. See a
    list of robot IPs at the github page for the course.
  - To connect to the robots, connect to the Pepper hotspot. To reduce
    the load on the hotspot, please disconnect between your sessions.
    
  - A good starting point is using something similar to the 'classic' agent type and then
    replacing it with calls to the 'robot' interface.
"""
from utils import *
from robotinterface import * 
from domains.hospital.actions import ROBOT_ACTION_LIBRARY
from search_algorithms.graph_search import graph_search
import time


def robot_agent_type(level, initial_state, ROBOT_ACTION_LIBRARY, goal_description, frontier, robot_ip):

    # Write your robot agent type here! Here is some help to get you started...

    # Like the classic agent type, we need to create an action set where all agents can perform all the available actions
    action_set = [ROBOT_ACTION_LIBRARY] * level.num_agents

    # What follows is a small example of how to interact with the robot.
    # You should browse through 'robot_interface.py' to get a full overview of all the available functionality
    robot = RobotClient(robot_ip)

    # Test out the robots microphone. The server will let you know when the robot is listening.
    robot.listen(3, playback=True)

    # test the robots speech
    robot.stand()

    # The robot will announce that it is executing the plan
    robot.say('I am executing plan. Please watch out!')

    # OBS! Remember, the robot cannot solve all levels. It might be necessary to check if the plan is empty, or if it has failed.

    # Wait until the robot is done speaking
    time.sleep(3)

    # close the connection
    robot.close()