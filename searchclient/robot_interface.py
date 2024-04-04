import socket
import msgpack
import time
import math
import sys
import json
import paramiko
import cv2
import signal
import re
import threading
import numpy as np
import subprocess
from pupil_apriltags import Detector



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
    runs the searchclient with the 'robot' agent type on the robot at IP 192.168.0.102.

  - To connect to the robots, connect to the Pepper hotspot. To reduce
    the load on the hotspot, please disconnect between your sessions.
    
  - A good starting point is using something similar to the 'classic' agent type and then
    replacing it with calls to the 'robot' interface.
"""

# for linux and mac
# export PYTHONPATH=${PYTHONPATH}:/home/seb/Downloads/python-sdk/lib/python2.7/site-packages

def degrees_to_radians(degree):
    '''
    :param degree: angle in degrees  
    :return: angle in radians
    '''
    return degree * (math.pi / 180)

# Robot Client Class for use with the robot server class that will translate python3 commands to the robot server
class RobotClient():
    def __init__(self, ip):

        # Set the ip address of the robot
        self.ip = ip

        # Set some class variables to be used later
        self.username = None
        self.password = None
        self.port = None
        self.vision_port = None
        self.video_stream = True # only shows if get_vision is called

        # Maps the ip to a port number for the server (IP can change, port should not)
        self.load_config()

        # We will use the same host as the server
        self.host = socket.gethostbyname('localhost')  # as both code is running on same pc

        self.client_socket = socket.socket()  # instantiate
        self.client_socket.connect((self.host, self.port))  # connect to the server

        

        # Mapping of the directions to the angles (use these to turn the robot in the right direction i.e. the shortest path to the direction)
        self.direction_mapping = { 'Move(N)': 90,
                        'Move(E)': 0,
                        'Move(S)': 270,
                        'Move(W)': 180,
                        'Push(N,N)': 90,
                        'Push(E,E)': 0,
                        'Push(S,S)': 270,
                        'Push(W,W)': 180}

    def load_config(self):
        """
        Load the robot configuration from the robot_config.json file.
        The configuration file contains the robot credentials such as the username, password, port and vision port.
        """
        try:
            # Load the configuration file
            with open('robot_config.json', 'r') as config_file:
                config = json.load(config_file)
            
            # Get the robot credentials from the config file
            credentials = config.get('robot_config', {})
            robot_cred = credentials.get(self.ip)

            # Set the username, password and port based on the robot credentials
            if robot_cred:
                self.username = robot_cred['username']
                self.password = robot_cred['password']
                self.port = int(robot_cred['port'])
                self.vision_port = int(robot_cred['vision_port'])

        except FileNotFoundError:
            print("Configuration went wrong - file not found.")

    def robot_vision_live_feed(self):
        #TODO: Might not be needed, but you can use this to get the vision stream from the robot by copying the code from VideoStreamThread into a python3 file called robot_vision.py and running it in a subprocess.

        #run robot_vision.py in a subprocess with ip and vision_port as arguments
        subprocess.run(['python3', 'robot_vision_live_feed.py', self.ip, str(self.vision_port)])

    def instantiate_vision_processes(self, ip, vision_port):
        """
        Instantiates the vision processes on the robot.

        Parameters
        ----------
        'ip' : string
            The IP address of the robot.
        'vision_port' : int
            The port number for the vision process on the robot. Which is fetched from the robot_config.json file.

        Returns
        -------
            The video thread that will run the vision process and images can be accessed from the thread.
        """

        # Create video thread that will run the vision process and images can be accessed from the thread
        video_thread = VideoStreamThread(ip, vision_port)
        video_thread.start()
        return video_thread
    
    def forward(self,distance,block):
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

        forward_cmd = {
            'type': 'forward',
            'distance': float(distance),
            'block': block
        }
        message = msgpack.packb(forward_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024).decode() 
    
    def say(self, s):

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

        say_cmd = {
            'type': 'say',
            'sentence': s
        }
        message = msgpack.packb(say_cmd, use_bin_type=True)
        self.client_socket.send(message)  # send message
        data = self.client_socket.recv(1024)

    def turn(self,angle,block):
        """
        Commands the robot to turn around its vertical axis.

        The position of the robot will remain approximately constant during the motion.
        Expect that the actually turned angle will vary a few degrees from the commanded values.
        The speed of the motion will be determined dynamically, i.e., the further it has to turn,
        the faster it will move.

        Parameters
        ----------
        'theta' : float
            The angle to turn in radians in the counter-clockwise direction.
        """

        turn_cmd = {
            'type': 'turn',
            'angle': float(angle),
            'block': block
        }
        message = msgpack.packb(turn_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)
    
    def stand(self):
        """
        Commands the robot to stand up in a straight position. This should be called often to ensure the actuators dont overhead and are not damaged.
        """

        stand_cmd = {
            'type': 'stand'
        }
        message = msgpack.packb(stand_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)
    
    def head_position(self, yaw, pitch, relative_speed=0.05):
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

        head_cmd = {
            'type': 'head_position',
            'yaw': float(yaw),
            'pitch': float(pitch),
            'relative_speed': float(relative_speed)
        }
        message = msgpack.packb(head_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def listen(self, duration=3, channels=[0,0,1,0],playback=False):
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

        listen_cmd = {
            'type': 'listen',
            'duration': duration,
            'channels': channels,
            'playback': playback
        }
        message = msgpack.packb(listen_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def shutdown(self):
        """
        Commands the robot to shutdown. This will turn off the robot and the server.
        """

        shutdown_cmd = {
            'type': 'shutdown'
        }
        message = msgpack.packb(shutdown_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def move(x,y,theta,block):
        '''
        Commands the robot to move to a given position and orientation. Three degrees of freedom are specified: 
        the x and y coordinates of the position and the orientation theta. The position is specified in meters
        relative to the robot's initial position. The orientation is specified in radians relative to the robot's
        initial orientation. 

        Parameters
        ----------
        'x' : float
            The x coordinate of the position in meters.
        'y' : float
            The y coordinate of the position in meters.
        'theta' : float
            The orientation in radians.
        'block' : bool
            If true, the function will block until the robot has reached the target position.
        '''

        move_cmd = { 
            'type': 'move',
            'x': float(x),
            'y': float(y),
            'theta': float(theta),
            'block': block
        }
        message = msgpack.packb(move_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def close(self):
        if self.client_socket:
            self.client_socket.close()
    
    def declare_direction(self, move):
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

        direction = {'Move(N)': "I am going North",
                     'Move(E)': 'I am going East',
                     'Move(S)': 'I am going South',
                     'Move(W)': 'I am going West',
                     'Push(N,N)': 'I am pushing North',
                     'Push(E,E)': 'I am pushing East',
                     'Push(S,S)': 'I am pushing South',
                     'Push(W,W)': 'I am pushing West'}
        return robot.say(direction[move])
    

    def localization_controller(self,video_thread):
        # start by tilting the head down so the april tag in the next cell is in the middle of the image
        self.head_position(0, degrees_to_radians(22.5), relative_speed=0.1)
        
        # TODO: Your localization controller here. Remember to look at video_thread.closest_tag and video_thread.middle_bottom! 
        
        #time.sleep(1)
        #self.stand() # stand up and get ready for next action in plan!
        

class VideoStreamThread(threading.Thread):

    '''
    Thread to get the vision stream from the robot! It will run in the background and the frame can be accessed from the main thread.
    The frame will be updated in the run method of the thread, so the frame can be accessed from the main thread. 
    Three important things can be accessed from the main thread:
    - The frame: The image frame from the robot's camera
    - The closest tag: The closest tag to the bottom middle of the image
    - The middle bottom: The middle bottom of the image (where the robot should align itself)

    You can then use the frame and the closest tag to build a simple robot controller that aligns the robot with the closest tag. This should not be too difficult, as you can use the closest tag to calculate the distance and the angle to the tag. You can then use this information to move the robot towards the tag.
    '''
    
    def __init__(self, ip, vision_port):
        super().__init__()
        self.ip = ip
        self.frame = None
        self.closest_tag = None

        self.stop_event = threading.Event()
        self.vision_port = vision_port
        
        self.detector = Detector(
        families="tagStandard41h12",
        nthreads=1,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=2,
        decode_sharpening=0.25,
        debug=0
    )

    def run(self):
        while not self.stop_event.is_set():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.ip, self.vision_port))
            
            try:
                # Get the image data
                remaining = int.from_bytes(client_socket.recv(4), byteorder='little')
                image_data = bytearray()

                # Read the image data
                while remaining > 0:
                    data = client_socket.recv(remaining)
                    remaining -= len(data)
                    image_data += data

                # Decode the full image
                image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

                # Convert the image to gray to detect the tags
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Detect the tags
                tags = self.detector.detect(gray)

                # Dimensions of the image
                height, width, _ = image.shape

                # Middle bottom of the image, i.e. the center of the bottom of the image (where the robot should aligns itself)
                self.middle_bottom = (width // 2, height)

                # Initialize the target distance and center
                target_distance = np.inf # Distance to the closest tag
                target_center = self.middle_bottom # Center of the closest tag initialized to the middle bottom of the image
                target_corners = None # Corners of the closest tag

                # Go through each of the tags in the image found by the detector
                for tag in tags:

                    # get the center of the tag and calculate the distance to the bottom middle of the image
                    center = tuple([int(x) for x in tag.center])
                    distance = math.sqrt((center[0] - self.middle_bottom[0])**2 + (center[1] - self.middle_bottom[1])**2)
                    if distance < target_distance:
                        target_distance = distance
                        target_center = center
                        target_corners = tag.corners
                
                # Draw an outline of the target tag
                if target_corners is not None:
                    for i in range(len(target_corners)):
                        cv2.line(image, tuple(target_corners[i-1, :].astype(int)), tuple(target_corners[i, :].astype(int)), (0, 0, 255), 2)
                    
                    # Set the closest tag which is the tag with the shortest distance to the bottom middle of the image
                    self.closest_tag = {'distance': target_distance, 
                    'target_center':target_center,
                    'corners':target_corners}

                # Set the frame so we can access it from the main thread
                self.frame = {'image':image}
                
            except:
                continue

            client_socket.close()
            
    def stop(self):
        self.stop_event.set()


if __name__ == '__main__':
    
    #ip = sys.argv[1]
    ip = '192.168.1.110'

    # connect to the server and robot
    robot = RobotClient(ip) # on the server side, we print the message to see if the connection is successful: print(f"Connection from {address} has been established!")

    # how to make the robot say something
    #robot.say("Hello, I am a robot starting vision")
    #time.sleep(3)

    # listen
    #robot.listen(duration=5, channels=[0,0,1,0], playback=True) # this is used to implement whisper

    # lets move the robot forward
    #robot.forward(-0.2, True) # move the robot forward and block until the robot has moved
    
    # we can also turn the robot
    #robot.turn(degrees_to_radians(90), True) # turn the robot 90 degrees and block until the robot has turned

    # we can also make the robot stand
    #robot.stand()

    # we can also move the head to the left or right
    #robot.head_position(0, degrees_to_radians(17.5)) # move the head to the middle position
    
    # this is how you can start the vision stream (which will be hidden but running in the background)
    robot_vision = robot.instantiate_vision_processes(ip, robot.vision_port)

    # this calls the localization controller that you need to implement
    #robot.localization_controller(robot_vision)

    # This is how we can show the stream. This however will block the main thread, so you will need to stop the stream to continue with the program
    # You can finish the robot_vision_live_feed function to show the stream in a separate window, this requires some work but will allow you to run a different python file as a subprocess
    
    while True:
        if robot_vision.frame is not None: 
            cv2.imshow(f"Robot {ip} Vision", robot_vision.frame['image'])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break



    
