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
from robot.robot_utils import VideoStreamThread
from threading import Thread
import paramiko
from scp import SCPClient
import math
import sys

import cv2
import numpy as np
import qi
import time
import json
import re

from search import print_debug

qi.logging.setLevel(qi.logging.ERROR)


# This is the map of ip addresses to port numbers for the server, based on the ip address of the robot.
# The IP can change, but the port should not. If the IP changes, the port number should be updated in the server code.


class RobotClient:
    def __init__(self, ip: str, config_file: str = "robot/robot_config.json", vision: bool = False):
        self.ip: str = ip
        self.username: str = None
        self.password: str = None
        self.port: int = None
        self.vision: bool = vision
        self.vision_port: int = None
        self.vision_thread: VideoStreamThread = None
        self.config_file = config_file

        self.__load_config()
        ssh = self.__connect_to_robot_SSH()
        self.scp = SCPClient(ssh.get_transport())

        self.__initialize_ALProxies()
        self.__initialize_robot()

        # Mapping of the directions to the angles (use these to turn the robot in the right direction i.e. the shortest path to the direction)
        self.direction_mapping = {
            'Move(N)': 90,
            'Move(E)': 0,
            'Move(S)': 270,
            'Move(W)': 180,
            'Push(N,N)': 90,
            'Push(E,E)': 0,
            'Push(S,S)': 270,
            'Push(W,W)': 180
        }

    def __load_config(self):
        """
        Load the robot configuration from the robot config file.
        The configuration file contains the robot configuration such as the username, password, port and vision port.
        """
        # Load the configuration file
        try:
            with open(self.config_file, 'r') as config_file:
                config = json.load(config_file)
        except Exception as e:
            raise Exception(
                "Could not load robot configuration - file not found.", e)

        if self.ip not in config:
            raise Exception(
                "Robot's IP not in configuration file, please update the configuration file with the correct robot IP.")

        robot_config = config.get(self.ip)

        self.username = robot_config['username']
        self.password = robot_config['password']
        self.port = int(robot_config['port'])
        self.vision_port = int(robot_config['vision_port'])

    def __connect_to_robot_SSH(self) -> paramiko.SSHClient:
        """
        Connect to the robot using SSH, and also make a separate connection for the vision stream.
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(self.ip, username=self.username,
                        password=self.password)

            # If vision is enabled, run the ./pepper_cameras script to start the video stream
            if self.vision:
                ssh_vision = paramiko.SSHClient()
                ssh_vision.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                ssh_vision.load_system_host_keys()
                ssh_vision.connect(
                    self.ip, username=self.username, password=self.password)
                _, stdout_vision, _ = ssh_vision.exec_command(
                    './pepper_cameras', get_pty=True)
                port = None
                for i, line in enumerate(iter(stdout_vision.readline, "")):
                    if i == 6:
                        # print_debug("Reading vision port:")
                        # print_debug("line:", line)
                        port = ''.join(re.findall(r'\d+', line))
                        port = int(''.join(map(str, port)))
                        break

                if port is not None and port != self.vision_port:
                    # save the port number for the video stream in the json file
                    with open(self.config_file, 'r') as config_file:
                        config = json.load(config_file)
                        credentials = config
                        robot_cred = credentials.get(self.ip)
                        robot_cred['vision_port'] = port
                        config[self.ip] = robot_cred
                    with open(self.config_file, 'w') as config_file:
                        json.dump(config, config_file)

            return ssh
        except paramiko.AuthenticationException:
            print_debug(
                "Authentication failed, please verify your credentials.")
            raise

    def __initialize_ALProxies(self):
        """Lazy initialization of ALProxies."""

        self.session = qi.Session()

        try:
            self.session.connect("tcp://" + self.ip + ":9559")
        except RuntimeError:
            raise Exception("Can't connect to Naoqi at ip \"" +
                            self.ip + "\" on port 9559.")

        self.tts = self.session.service("ALTextToSpeech")
        self.motion = self.session.service("ALMotion")
        self.behavior = self.session.service("ALBehaviorManager")
        self.tracker = self.session.service("ALTracker")
        self.posture = self.session.service("ALRobotPosture")
        self.mem = self.session.service("ALMemory")
        self.asr = self.session.service("ALSpeechRecognition")
        self.leds = self.session.service("ALLeds")
        self.video = self.session.service("ALVideoDevice")
        self.recorder = self.session.service("ALAudioRecorder")
        self.player = self.session.service("ALAudioPlayer")
        self.tablet = self.session.service("ALTabletService")
        self.system = self.session.service("ALSystem")
        self.pm = self.session.service("ALPreferenceManager")
        self.touch = self.session.service("ALTouch")

    def __initialize_robot(self):
        """
        Initialize the robot to a server pose.
        """
        # Setting collision protection False (will interfere with motion based ALProxies if True)
        self.motion.setExternalCollisionProtectionEnabled("Move", False)
        self.motion.setExternalCollisionProtectionEnabled("Arms", False)

        # Wake up robot (if not already up) and go to standing posture)
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.5)

        # Robot anounces that it is ready
        self.say("I am ready")

        # Print the robot's IP and vision status to the console
        print_debug('Robot with IP: %r with vision %r initialized' %
                    (self.ip, self.vision))

    def instantiate_vision_processes(self, ip: str, vision_port: int) -> VideoStreamThread:
        """
        Instantiates the vision processes on the robot.

        Parameters
        ----------
        'ip' : string
            The IP address of the robot.
        'vision_port' : int
            The port number for the vision process on the robot. Which is fetched from the robot config file.

        Returns
        -------
            The video thread that will run the vision process and images can be accessed from the thread.
        """

        # Create video thread that will run the vision process and images can be accessed from the thread
        self.video_thread = VideoStreamThread(ip, vision_port)
        self.video_thread.start()
        return self.video_thread

    def forward(self, distance: float, block: bool = True) -> None:
        """
        Commands the robot to move forward a given distance in meters. 

        Parameters
        ----------
        'distance' : float
            The distance to move forward in meters.
        'block' : bool
            If true, the robot will wait until the motion is completed before continuing with the next command.
            If false, the robot will continue immediately. 
        """
        if block == False:
            Thread(target=(lambda: self.motion.moveTo(distance, 0, 0))).start()
        else:
            self.motion.moveTo(distance, 0, 0)

    def backward(self, distance: float, block: bool = True) -> None:
        self.forward(-distance, block)

    def say(self, sentence: str, language: str = "English") -> None:
        """
        Commands the robot to speak out the given sentence.

        The speech is generated using the onboard text-to-speech synthesis.
        Its intonation can sometimes be a bit strange. It is often possible to improve the
        understandability of the speech by inserting small breaks a key location in the sentence.
        This can be accomplished by inserting \\pau=$MS\\ commands, where $MS is the length of the
        break in milliseconds, e.g., robot.say("Hello \\pau=500\\ world!") will cause the robot to
        pause for 500 milliseconds before continuing with the sentence.

        Parameters
        ----------
        'sentence' : string
            The sentence to be spoken out loud.
        """
        Thread(target=(
            lambda: self.tts.say(sentence) if language == "English" else self.tts.say(sentence, language))).start()

    def turn_counter_clockwise(self, angle: float, block: bool = True) -> None:
        """
        Commands the robot to turn around its vertical axis.

        The position of the robot will remain approximately constant during the motion.
        Expect that the actually turned angle will vary a few degrees from the commanded values.
        The speed of the motion will be determined dynamically, i.e., the further it has to turn,
        the faster it will move.

        Parameters
        ----------
        'angle' : float
            The angle to turn in radians in the counter-clockwise direction.
        """
        if block == False:
            Thread(target=(lambda: self.motion.moveTo(0, 0, angle))).start()
        else:
            self.motion.moveTo(0, 0, angle)

    def turn_clockwise(self, angle: float, block: bool = True) -> None:
        self.turn_counter_clockwise(-angle, block)

    def stand(self) -> None:
        """
        Commands the robot to stand up in a straight position. This should be called often to ensure the actuators dont overhead and are not damaged.
        """
        self.posture.goToPosture("Stand", 0.5)

    def head_position(self, yaw: float, pitch: float, relative_speed: float = 0.05) -> None:
        """
        Commands the robot to move its head to a specific position.

        The head can be moved in two directions: yaw and pitch.

        Parameters
        ----------
        'yaw' : float
            The angle to move the head in the horizontal direction. 
            Must be in range [-2.0857, 2.0857] radians or [-119.5, 119.5] degrees.
        'pitch' : float
            The angle to move the head in the vertical direction.
            Must be in range [-0.7068, 0.6371] radians or [-40.5, 36.5] degrees.
        'relative_speed' : float
            The relative max speed of the head motion. 
            Must be in range [0, 1]. 
            Avalue of 1.0 will move the head as fast as possible, while a value of 0 will move the head as slow as possible.
        """
        self.motion.setStiffnesses("Head", 1.0)
        self.motion.setAngles(["HeadYaw", "HeadPitch"], [
                              yaw, pitch], relative_speed)

    def listen(self, duration: int = 3, channels: list[int] = [0, 0, 1, 0], playback: bool = False) -> None:
        '''
        Commands the robot to listen for a given duration.

        Parameters:
        -----------
        'duration' : int
            The duration of the listening in seconds.
        'channels' : list
            The channels to listen on. The default is [0,0,1,0] which 
            means that the robot will listen on the front microphone. 
            You can also listen on other channels by changing the list.
        playback : bool
            If true, the robot will play back the audio it has recorded.

        Returns:
        --------
            The audio data recorded by the robot is saved in a folder
            /tmp/ on the given computer. This can then used for speech
            recognition using Whisper.

        '''
        # enable face tracking
        self.start_face_tracking()

        # make eyes green for listening
        self.leds.fadeRGB("FaceLeds", 0, 1, 0, 0.5)

        # start recording
        robot.recorder.startMicrophonesRecording(
            "/home/nao/test.wav", "wav", 16000, [0, 0, 1, 0])
        print_debug('Started recording')

        # look slightly up
        self.head_position(0, -0.1)

        # wait for duration
        time.sleep(duration)

        # stop recording
        robot.recorder.stopMicrophonesRecording()

        # load the file
        print_debug('Done recording')
        fileId = robot.player.loadFile("/home/nao/test.wav")

        # play the file if playback is True
        if playback:
            print_debug('playing sound first')
            robot.player.play(fileId)

        # Get the audio data but do not pass through socket.
        # Instead save it locally for faster speech to text!
        self.download_file('test.wav')

        self.leds.fadeRGB("FaceLeds", 0, 0, 1, 0.5)

        # stop face tracking
        self.stop_tracking()

        # look back to straight ahead - thats where humans look when they walk)
        self.head_position(0, 0)

    def start_face_tracking(self) -> None:
        targetName = "Face"
        faceWidth = 0.1

        self.tracker.registerTarget(targetName, faceWidth)

        # Then, start tracker.
        self.tracker.track(targetName)

    def stop_tracking(self) -> None:
        self.tracker.stopTracker()

    def download_file(self, file_name):
        """
        Download a file from robot to ./tmp folder in root.
        ..warning:: Folder ./tmp has to exist!
        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.get(file_name, local_path="tmp/")
        print_debug("[INFO]: File tmp/" + file_name + " downloaded")
        self.scp.close()

    def declare_direction(self, move: str) -> None:
        '''
        Commands the robot to say the direction it is moving in. 

        Parameters
        ----------
        'move' : string
            The direction the robot is moving in.

        Returns
        -------
            Makes the robot say the direction it is moving in.
        '''

        direction = {
            'Move(N)': "I am going North",
            'Move(E)': 'I am going East',
            'Move(S)': 'I am going South',
            'Move(W)': 'I am going West',
            'Push(N,N)': 'I am pushing North',
            'Push(E,E)': 'I am pushing East',
            'Push(S,S)': 'I am pushing South',
            'Push(W,W)': 'I am pushing West'
        }
        self.say(direction[move])

    def localization_controller(self, video_thread: VideoStreamThread) -> None:
        # start by tilting the head down so the april tag in the next cell is in the middle of the image
        self.head_position(0, math.radians(22.5), relative_speed=0.1)
        time.sleep(1)

        while video_thread.frame is None:
            print_debug('Waiting for video thread')
            time.sleep(0.5)

        # TODO: Your localization controller here. Remember to look at video_thread.closest_tag and video_thread.middle_bottom!
        raise NotImplementedError()
        self.stand()  # stand up and get ready for next action in plan!

    def shutdown(self):
        if self.vision_thread:
            self.vision_thread.stop()

        self.motion.rest()


if __name__ == '__main__':
    # get the ip address of the robot
    ip = sys.argv[1]

    # create a robot object and pass the ip address, and set vision to True (set to False, if you don't want to use the vision)
    robot = RobotClient(ip, vision=True)

    robot.say("Hello, I am Pepper!")

    robot.forward(0.2)
    robot.backward(0.2)

    robot.turn_counter_clockwise(math.radians(45))
    robot.turn_clockwise(math.radians(45))

    robot.head_position(-1.0, 0.0)
    time.sleep(3)
    robot.head_position(0.0, 0.0)

    robot.stand()

    robot.say("Listening")
    robot.listen(5, playback=True)

    robot_vision = robot.instantiate_vision_processes(ip, robot.vision_port)

    # Wait for vision thread to start
    while robot_vision.frame is None:
        print_debug("Waiting for vision thread to start...")
        time.sleep(1)

    # Look for tags in the image
    robot.head_position(0, math.radians(22.5), relative_speed=0.1)
    if robot_vision.tag_in_view:
        print_debug("Closest tag to the bottom middle of the image:",
              robot_vision.closest_tag)
        print_debug("Middle bottom of the image:", robot_vision.middle_bottom)
    else:
        print_debug("No tag in view")

    try:
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

            if robot_vision.frame is None:
                continue

            cv2.imshow(f"Robot {ip} Vision", robot_vision.frame['image'])

            if robot_vision.tag_in_view:
                target_center = robot_vision.closest_tag['tag_center']
                print("Tag Center: ", target_center)

    except KeyboardInterrupt:
        pass

    robot_vision.stop()
    robot.shutdown()
