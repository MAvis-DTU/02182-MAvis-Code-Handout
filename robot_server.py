import socket
import msgpack
import sys
import os
import naoqi
import time
import json
import re
import signal

from psutil import process_iter
from signal import SIGKILL

from scp import SCPClient
import paramiko

from scipy.io.wavfile import write
from threading import Thread

import json

"""
Using the robot agent type differs from previous agent types.
  - Firstly, install additional packages 'scp' and 'msgpack'.
    Use pip for installation, like this: 
        'python2 -m pip install numpy msgpack'. 
    Exact steps may vary based on your platform and Python 
    installation. Installing 'scp' also installs the 'paramiko' package.

  - Secondly, you don't need the Java server for the robot - although you can. So, the command
    to start the search client in the terminal is different, for example:
        'python searchclient/searchclient.py -robot -ip 192.168.1.102 -level levels/SAsoko1_04.lvl'
    runs the searchclient with the 'robot' agent type on the robot at IP 192.168.1.102.

  - To connect to the robots, connect to the Pepper hotspot. To reduce
    the load on the hotspot, please disconnect between your sessions.
    
  - A good starting point is using something similar to the 'classic' agent type and then
    replacing it with calls to the 'robot' interface.
"""


# for linux and mac
# export PYTHONPATH=${PYTHONPATH}:/home/seb/Downloads/python-sdk/lib/python2.7/site-packages

# This is the map of ip addresses to port numbers for the server, based on the ip address of the robot. 
# The IP can change, but the port should not. If the IP changes, the port number should be updated in the server code.


class RealRobot:
    def __init__(self, ip, vision=False):

        # Set the ip address of the robot
        self.ip = ip

        # Set some class variables to be used later
        self.username = None
        self.password = None
        self.port = None
        self.vision = vision

        # Load the configuration for the robot
        self.load_config()

        # Connect to robot using the config to retrieve files from robot (scp)
        ssh = self.connect_to_robot_SSH()

        # Create SCPClient, this is used to download files from the robot
        self.scp = SCPClient(ssh.get_transport())

        # Standard ALProxies
        self.initialize_ALProxies()

        # Initialize the robot to a server pose (the pose it should be in when the server starts)
        self.initialize_server_pose()


    def load_config(self):
        """
        Loads configuration for the robot based on its IP. 
        Make sure that the configuration file is in the same directory as the script.
        """
        print("Loading configuration...")
    
        # Load the configuration file
        try:
            with open('robot_config.json', 'r') as config_file:
                config = json.load(config_file)
        except:
            raise Exception("Configuration went wrong - file not found.")
        
        # Get the robot credentials from the config file
        credentials = config.get('robot_config', {})

        # simple check to see if the robot IP is in the configuration file
        if ip not in credentials:
            raise Exception("Robot's IP not in configuration file, please update the configuration file with the correct robot IP.")
        
        robot_cred = credentials.get(self.ip)

        # Set the username, password and port based on the robot credentials
        if robot_cred:
            self.username = robot_cred['username']
            self.password = robot_cred['password']
            self.port = int(robot_cred['port'])

    def connect_to_robot_SSH(self):
        """
        Connect to the robot using SSH, and also make a separate connection for the vision stream.
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(self.ip, username=self.username, password=self.password)
            
            # If vision is enabled, run the ./pepper_cameras script to start the video stream
            if self.vision:
                ssh_vision = paramiko.SSHClient()
                ssh_vision.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_vision.load_system_host_keys()
                ssh_vision.connect(self.ip, username=self.username, password=self.password)
                _, stdout_vision, _ = ssh_vision.exec_command('./pepper_cameras', get_pty=True)
                for i, line in enumerate(iter(stdout_vision.readline, "")):
                    if i == 6:
                        #print(line, end="")
                        port = ''.join(re.findall(r'\d+', line))
                        port = int(''.join(map(str, port)))
                        break

                # save the port number for the video stream in the json file
                with open('robot_config.json', 'r') as config_file:
                    config = json.load(config_file)
                    credentials = config.get('robot_config', {})
                    robot_cred = credentials.get(self.ip)
                    robot_cred['vision_port'] = port
                    config['robot_config'][self.ip] = robot_cred
                with open('robot_config.json', 'w') as config_file:
                    json.dump(config, config_file)
                   
            return ssh
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials.")

    def initialize_ALProxies(self):
        """Lazy initialization of ALProxies."""

        self.tts = naoqi.ALProxy("ALTextToSpeech", ip, 9559)
        self.motion = naoqi.ALProxy("ALMotion", ip, 9559)
        self.behavior = naoqi.ALProxy("ALBehaviorManager", ip, 9559)
        self.tracker = naoqi.ALProxy("ALTracker", ip, 9559)
        self.posture = naoqi.ALProxy("ALRobotPosture", ip, 9559)
        self.mem = naoqi.ALProxy("ALMemory", ip, 9559)
        self.session = self.mem.session()
        self.mem = self.session.service("ALMemory")
        self.asr = naoqi.ALProxy("ALSpeechRecognition", ip, 9559)
        self.leds = naoqi.ALProxy("ALLeds", ip, 9559)
        self.video = naoqi.ALProxy("ALVideoDevice", ip, 9559)
        self.recorder = naoqi.ALProxy("ALAudioRecorder", ip, 9559)
        self.player = naoqi.ALProxy("ALAudioPlayer", ip, 9559)
        self.tablet = naoqi.ALProxy("ALTabletService", ip, 9559)
        self.system = naoqi.ALProxy("ALSystem", ip, 9559)
        self.pm = naoqi.ALProxy("ALPreferenceManager", ip, 9559)
        self.touch = naoqi.ALProxy("ALTouch", ip, 9559)

    def initialize_server_pose(self):
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
        print('\nRobot with IP: %r with vision %r initialized' % (self.ip, self.vision))
        

    def download_file(self, file_name):
        """
        Download a file from robot to ./tmp folder in root.
        ..warning:: Folder ./tmp has to exist!
        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.get(file_name, local_path="/tmp/")
        print("[INFO]: File " + file_name + " downloaded")
        self.scp.close()

    def say(self, sentence, language="English"):
        Thread(target=(
            lambda: self.tts.say(sentence) if language == "English" else self.tts.say(sentence, language))).start()

    def forward(self, dist, block = False):
        if block == False:
            Thread(target=(lambda: self.motion.moveTo(dist, 0, 0))).start()
        else:
            self.motion.moveTo(dist, 0, 0)

    def turn(self, dist, block=False):
        if block == False:
            Thread(target=(lambda: self.motion.moveTo(0, 0, dist))).start()
        else:
            self.motion.moveTo(0, 0, dist)

    def stand(self):
        self.posture.goToPosture("Stand", 0.5)

    def head_position(self, yaw, pitch, relative_speed=0.05):
        self.motion.setStiffnesses("Head", 1.0)
        self.motion.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], relative_speed)

    def offLeds(self,leds="AllLeds"):
        """
        Turn off the leds on the robot. Feel free to add this on the robot interface if you need it.
        """
        robot.leds.off(leds)

    def onLeds(self,leds="AllLeds"):
        """
        Turn on the leds on the robot. Feel free to add this on the robot interface if you need it.
        """
        robot.leds.on(leds)

    def sensor_touched(self, sensor):

        # Get list of sensor_status in the form of a list: [['Head', False, []], ['LArm', False, []], ... ]]
        sensor_list = robot.touch.getStatus()

        # Create sensor dictionary to get sensor info
        sensor_dict = {     'Head': 0,
                            'LArm': 1,
                            'Leg': 2,
                            'RArm': 3,
                            'LHand': 4,
                            'RHand': 5,
                            'Bumper/Back': 6,
                            'Bumper/FrontLeft': 7,
                            'Bumper/FrontRight': 8,
                            'Head/Touch/Front': 9,
                            'Head/Touch/Middle': 10,
                            'Head/Touch/Rear': 11,
                            'LHand/Touch/Back': 12,
                            'RHand/Touch/Back': 13,
                             'Base': 14
                            }

        # Return the boolean value of the sensor: True if touched, False if untouched
        return sensor_list[sensor_dict[sensor]][1]
    
    def listen(self, duration=3, channels = [0,0,1,0],playback=False):

        # enable face tracking
        self.face_tracking(True)

        # make eyes green for listening
        self.leds.fadeRGB("FaceLeds", 0,1,0,0.5)

        # start recording
        robot.recorder.startMicrophonesRecording("/home/nao/test.wav", "wav", 16000,[0,0,1,0])
        print('Started recording')
        
         # look slightly up
        self.head_position(0,-0.1)

        # wait for duration
        time.sleep(duration)

        # stop recording
        robot.recorder.stopMicrophonesRecording()

        # load the file
        print('Done recording')
        fileId = robot.player.loadFile("/home/nao/test.wav")

        
        # play the file if playback is True
        if playback:
            print('playing sound first')
            robot.player.play(fileId)

        
        # Get the audio data but do not pass through socket. 
        # Instead save it locally for faster speech to text!
        self.scp.get('test.wav', local_path=str(os.getcwd())+"/tmp/")
        print("[INFO]: File " + 'test.wav' + " downloaded to " + str(os.getcwd())+"/tmp/")
        self.scp.close()
        self.leds.fadeRGB("FaceLeds", 0,0,1,0.5)

        # stop face tracking
        self.face_tracking(False)

        # look back to straight ahead - thats where humans look when they walk)
        self.head_position(0,0)

    def face_tracking(self,track=True):
        if track:# Add target to track.
            targetName = "Face"
            faceWidth = 0.1
            
            self.tracker.registerTarget(targetName, faceWidth)

            # Then, start tracker.
            self.tracker.track(targetName)

        else:
            self.tracker.stopTracker()
    
    
    def command(self, data):
        #tested
        if data['type'] == 'say':
                self.say(str(data['sentence']))

        #tested
        if data['type'] == 'forward':
            self.forward(float(data['distance']),bool(data['block']))

        #not tested
        if data['type'] == 'turn':
            self.turn(float(data['angle']),bool(data['block']))

        #not tested
        if data['type'] == 'stand':
            self.stand()

        #not tested
        if data['type'] == 'head_position':
            self.head_position(float(data['yaw']),float(data['pitch']), float(data['relative_speed']))

        #not tested
        if data['type'] == 'shutdown':
            self.shutdown()
        
        if data['type'] == 'listen':
            self.listen(float(data['duration']),data['channels'],bool(data['playback']))

# Define a signal handler to catch Ctrl+C
def signal_handler(sig, frame):
    print(' Ctrl+C pressed. Closing sockets...')
    sys.exit(0)

# Define the server program
def server_program(robot):
    # make sure to catch the signal
    signal.signal(signal.SIGINT, signal_handler)

    # Get the hostname and port
    host = socket.gethostbyname('localhost')

    # Base port number for all robots off of ip address
    port = robot.port

    # instantiate the server using socket
    server_socket = socket.socket()  

    # Look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # Ronfigure how many client the server can listen simultaneously
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection

    # print the address of the client
    print("Connection from: " + str(address))

    while True:
        try: 
            # Receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024)

            # check if we have package waiting
            if not data:
                # if data is not received break
                break

            # Unpack bytes into data dict
            data = msgpack.unpackb(data, raw=False)

            # Execute command from data dict
            robot.command(data)

            # or try this if you want to use the class
            # robot.command(data)

            #print the data we got from client
            print("from connected user: " + str(data))

            # send data to the client socket
            data = 'Server got ran command ' + str(data['type'])

            #send data back to client
            conn.send(data.encode()) 

        except KeyboardInterrupt:
            print('Ctrl+C pressed. Closing sockets...')
            # Close all sockets
            server_socket.close()  # Add your sockets here
            sys.exit(0)
            
    conn.close()  # close the connection


if __name__ == '__main__':
    # get the ip address of the robot
    ip = sys.argv[1]
    
    # create a robot object and pass the ip address, and set vision to True (set to False, if you don't want to use the vision)
    robot = RealRobot(ip, vision=True)

    # start the server that converts the commands (Python 3.x) to robot commands (Python 2.7)
    server_program(robot)