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
import io
import socket

import msgpack
import numpy as np


class RobotInterface:

    def __init__(self, ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, 1234))
        self.unpacker = msgpack.Unpacker()
        self.next_command_id = 0

    def move(self, forward, left):
        """
        Commands the robot to drive to a specific position.

        The rotation of the robot will remain approximately constant during the motion.
        Expect that the actually driven distance will vary a few centimeters from the commanded values.
        The speed of the motion will be determined dynamically, i.e., the further it has to drive,
        the faster it will move.
        Note that this command clamps the values on the robot-side to +/- 3 meter, in order to prevent
        the robot from driving of to infinity if given an accidentally large value.

        Parameters
        ----------
        'forward' : float
            The distance to the target position along the robot's forward axis.
            A negative value indicates that the target position is behind the robot.
        'left' : float
            The distance to the target position along the robot's left axis.
            A negative value indicates that the target position is to the right of the robot.
        """
        move_cmd = {
            'type': 'move',
            'x': float(forward),
            'y': float(left)
        }
        assert np.isfinite(move_cmd["x"]) and np.isfinite(
            move_cmd["y"]
        ), "Forward and left must be real float numbers"
        command_id = self._send_command(move_cmd)
        self._await_completion(command_id)

    def turn(self, theta):
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
            "type": "turn",
            "theta": float(theta),
        }
        assert np.isfinite(turn_cmd["theta"]), "Theta be real float number"
        command_id = self._send_command(turn_cmd)
        self._await_completion(command_id)

    def say(self, sentence):
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
        tts_cmd = {
            "type": "tts",
            "sentence": sentence,
        }
        command_id = self._send_command(tts_cmd)
        self._await_completion(command_id)

    def configure_speech(self, speed=1.0, pitch=1.0, language="English"):
        """
        Commands the robot to modify its speech synthesis.
        Note: Only one of the robots 'R1' is capable of speaking Danish.
        The quality of the English synthesis is better than the Danish synthesis.

        Parameters
        ----------
        'speed' : float
            A multiplier modifying the speed of speech.
            0.5 is very slow, 2.0 is very fast. 0.8 is usually the easiest to understand.
        'pitch' : float
            A multiplier modifying the default pitch level.
            The supported range is [0.5, 2.0]
        'language' : string
            Either 'English' or 'Danish'. See note above on danish.
        """
        tts_cmd = {
            "type": "tts_configure",
            "speed": speed,
            "pitch": pitch,
            "language": language,
        }
        command_id = self._send_command(tts_cmd)
        self._await_completion(command_id)

    VALID_LED_GROUPS = {
        'eyes',
        'ears',
        'shoulders'
    }

    def set_leds(self, group, red, green, blue, fade_duration=0.0):
        """
        Commands the robot to modify the colors of its LEDs.

        The robot has three groups of LEDs:
        - The 'eyes' which can be controlled in the full RGB spectrum.
        - The 'ears' which can only be blue, but their intensity can still be controlled.
        - The 'shoulders' which can be controlled in the full RGB spectrum.

        Parameters
        ----------
        'red' : float
            The intensity of the red color in the range [0,1].
        'green' : float
            The intensity of the green color in the range [0,1].
        'blue' : float
            The intensity of the blue color in the range [0,1].
        'fade_duration' : float
            The robot will fade between the current color and the target color over this duration (in seconds)
            using a linear interpolation.
        """
        if group not in self.VALID_LED_GROUPS:
            raise ValueError(group + " is not a valid LED group name!")
        led_cmd = {
            "type": "leds",
            "group_name": group,
            "red": red,
            "green": green,
            "blue": blue,
            "fade_duration": fade_duration,
        }

        command_id = self._send_command(led_cmd)
        self._await_completion(command_id)

    def spin_eyes(self, red, green, blue, spin_duration, animation_duration):
        """
        Commands the robot to play a 'spin' animation with its eye LEDs.

        Parameters
        ----------
        'red' : float
            The intensity of the red color in the range [0,1].
        'green' : float
            The intensity of the green color in the range [0,1].
        'blue' : float
            The intensity of the blue color in the range [0,1].
        'spin_duration' : float
            The duration of a single spin in seconds
        'animation_duration' : float
            The duration of the entire animation in seconds
        """
        spin_cmd = {
            "type": "spin_eyes",
            "red": red,
            "green": green,
            "blue": blue,
            "spin_duration": spin_duration,
            "animation_duration": animation_duration,
        }

        command_id = self._send_command(spin_cmd)
        self._await_completion(command_id)

    def move_joints(self, joints, angles, speed):
        """
        Commands the robot to move its actuators (head, torso, arms) to the specified angles.

        E.g., to make the robot look down issue the command:
          robot.move_joints("HeadPitch", 0.2, 0.5)
        It is also possible move several joints simultaneously:
          robot.move_joints(["HeadPitch", "HeadYaw], [0.2, -0.2], 0.5)
        In this case, the n'th joint name is commanded to move to the n'th angle, i.e., in the above example
        the HeadPitch will be set to 0.2 radians and the HeadYaw will be set to -0.2.
        Further documentation of the names and motion range of the joints can be found at
        http://doc.aldebaran.com/2-5/family/pepper_technical/joints_pep.html

        Parameters
        ----------
        'joints' : string or [string]
            The names of the joints to actuate
        'angles' : float or [float]
            The angles for the actuators to target in radians
        'speed' : float
            The speed on a scale [0,1].
        """
        if not isinstance(joints, list):
            joints = [joints]
        if not isinstance(angles, list):
            angles = [angles]
        if len(joints) != len(angles):
            raise ValueError(
                "The number of joints and the number of angles specified must be identical!"
            )

        joint_cmd = {
            "type": "joints",
            "joints": joints,
            "angles": angles,
            "speed": speed,
        }

        command_id = self._send_command(joint_cmd)
        self._await_completion(command_id)

    def perform_animation(self, animation_name):
        """
        Commands the robot to perform a pre-scripted NaoQi animation.

        A couple of animations I find to be useful are:
        - 'animations/Stand/Gestures/Hey_1' - The robot waves
        - 'animations/Stand/Gestures/IDontKnow_2' - The robot looks confused.
        - 'animations/Stand/Gestures/Far_2' - The robot bids welcome.

        The full list of available animations can be found at
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html#pepp-pepper-list-of-animations-available-by-default
        """
        animation_cmd = {
            'type': 'animation',
            'name': animation_name
        }
        command_id = self._send_command(animation_cmd)
        self._await_completion(command_id)

    def wake_up(self):
        """
        Commands the robot to turn on its motors and perform a small self-check.

        If the robot is currently in the 'rest' state, it is not possible to control the motors until this command
        has been executed.
        """
        state_command = {
            'type': 'goto_state',
            'state': 'wake'
        }
        command_id = self._send_command(state_command)
        self._await_completion(command_id)

    def rest(self):
        """
        Commands the robot to enter a safe rest state before turning off its motors.

        Since the motors are completely powered off when in the rest state, it is preferable to enter this state whenever
        the robot will not be used for an extended amount of time.
        """
        state_command = {
            'type': 'goto_state',
            'state': 'rest'
        }
        command_id = self._send_command(state_command)
        self._await_completion(command_id)

    def reset_joints(self):
        """
        Commands the robot to enter a neutral position with all joints in their default position.
        """
        joint_cmd = {
            "type": "joints",
            "joints": [
                "HeadPitch",
                "HeadYaw",
                "LShoulderPitch",
                "RShoulderPitch",
                "LShoulderRoll",
                "RShoulderRoll",
                "LElbowYaw",
                "RElbowYaw",
                "LElbowRoll",
                "RElbowRoll",
                "LWristYaw",
                "RWristYaw",
                "LHand",
                "RHand",
                "HipPitch",
                "HipRoll",
                "KneePitch",
            ],
            "angles": [
                -0.1,
                0.0,
                1.57,
                1.57,
                0.1,
                -0.1,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.2,
                0.2,
                0.0,
                0.0,
                0.0,
            ],
            "speed": 0.2,
        }
        command_id = self._send_command(joint_cmd)
        self._await_completion(command_id)

    def capture_image(self, camera=0):
        """
        Commands the robot to capture an image with the specified camera.

        The robot has two camera: The top camera with id=0 and the bottom camera with id=1
        For further documentation on these cameras can be found at
        http://doc.aldebaran.com/2-5/family/pepper_technical/video_2D_pep_v18a.html#video-2d-pepper-v18a

        The returned image can then be used for a wealth of different image analyses.
        Some recommended libraries which can allow you to get up to speed includes:

        - Face recognition is fairly simple to implement using a library such as 'face_recognition'
          https://github.com/ageitgey/face_recognition
        - Pose detection can be implemented using various different deep learning models such as
          https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
        - Classic image analysis can be implemented using the venerable OpenCV library (https://opencv.org/)


        Parameters
        ----------
        'camera' : int
            Will use the top camera if set to 0 and the bottom camera if set to 1

        Returns
        -------
        image: np.ndarray
            The image is returned as a RGB numpy array of size [960, 1280, 3]
        """
        if camera < 0 or camera > 1:
            raise ValueError("Only 0 and 1 are valid camera identifiers")
        image_cmd = {
            'type': 'image_capture',
            'camera': camera
        }
        self._send_command(image_cmd)
        image_response = self._wait_for_response_type("image")
        width = image_response["width"]
        height = image_response["height"]
        image = np.frombuffer(image_response["pixels"], dtype=np.uint8).reshape(
            (height, width, 3)
        )
        return image

    MICROPHONE_IDS = {
        "left": 0,
        "right": 1,
        "front": 2,
        "rear": 3,
    }

    def begin_audio_recording(self, microphone="front"):
        """
        Commands the robot to start recording on the specified microphone.

        The robot has four microphones, all mounted on the head.
        They are named based on their direction: 'front', 'left', 'right' and 'rear'.
        Note: Only a single recording can be in-progress at a time.

        Parameters
        ----------
        'microphone': string
            One of 'front', 'left', 'right' or 'rear'
        """
        if microphone not in self.MICROPHONE_IDS:
            raise ValueError(f"'{microphone}' is not a supported microphone!")
        recording_cmd = {
            "type": "record_audio",
            "is_begin": True,
            "microphone": self.MICROPHONE_IDS[microphone],
        }
        self._send_command(recording_cmd)

    def end_audio_recording(self):
        """
        Commands the robot to end the current recording and return the recording.

        The returned audio file can then easily be used for Speech Recognition using a library such as
        'SpeechRecognition' which can be found at https://github.com/Uberi/speech_recognition#readme.

        Returns
        -------
        recording: An io.BytesIO buffer containing a 16000 Hz Wave file.
        """
        recording_cmd = {
            'type': 'record_audio',
            'is_begin': False,
            'microphone': 0
        }
        self._send_command(recording_cmd)
        recording_response = self._wait_for_response_type("audio")
        return io.BytesIO(recording_response["audio"])

    def observe(self, camera=1, target_tag_id=-1):
        """
        Scans for AprilTags using the specified camera and reports their distance and relative angle.

        Note that due to non-linearities in the camera lens, the distances and relative angles might not be exact.
        For just determining the presence of objects in a cell, this is no issue, but for a positioning algorithm
        this could produce significant issues. Talk to the TA if you wish to know more about these issues.

        Parameters
        ----------
        camera: int
            The robot will observe using the top camera if camera=0 and the bottom camera if camera=1
        target_tag_id: int
            The robot will try to obtain a more accurate distance and angle measurement of a specific tag by actively
             looking towards this tag. This avoids non-linearities in the lens, but is a bit slow.

        Returns
        -------
        landmarks: [dict]
            A list of landmarks, where each landmark is a dictionary with the following keys:
            - 'id' - The id encoded by the AprilTag
            - 'angle' - The angle of the AprilTag relative to the robots forward axis.
            - 'distance' - The ground distance to the AprilTag.
        """
        observe_cmd = {
            "type": "observe",
            "camera": camera,
            "target": target_tag_id,
        }
        self._send_command(observe_cmd)
        observation = self._wait_for_response_type("observation")
        return observation["landmarks"]

    def odometry_measure(self):
        """
        Reads the robots own position and rotation estimate based upon odometric measurements.

        The robots wheels are equipped with rotation encoders which can measure how far the wheels have been driven,
        thus allowing the robot to estimate its own position and rotation by integrating over the measured movements.
        This estimate can be used to compensate for some of the motor error, but it will likewise accumulate an error
        over time.
        The returned measurements are in a 'reference coordinate system' which is simply a coordinate system aligned
        with the initial position of the robot, i.e., the x-axis points forward and the y-axis points left in the position
        where the robot initially started (or the odometric system was last reset).

        Returns
        -------
        measurement: numpy.array of size 3
            A vector [x, y, theta] containing the robots position and rotation in the reference coordinate system.


        """
        odometry_cmd = {
            "type": "odometry",
            "is_reset": False,
        }
        self._send_command(odometry_cmd)
        response = self._wait_for_response_type("odometry")
        return np.array(response["measurements"])

    def odometry_reset(self):
        """
        Resets the robots internal odometry system such that the current position and rotation becomes the origin and
        basis of reference coordinate system, that is, performing an robot.odometry_measure() immediately afterwards
         would result in a measurement of [0,0,0].

        Useful for when some kind of external compensation have been performed, e.g., a manual or visual correction.
        """
        odometry_cmd = {
            "type": "odometry",
            "is_reset": True,
        }
        self._send_command(odometry_cmd)

    TOUCH_SENSOR_NAMES = {
        "head_front": "Head/Touch/Front",
        "head_middle": "Head/Touch/Middle",
        "head_rear": "Head/Touch/Rear",
        "left_hand": "LHand/Touch/Back",
        "right_hand": "RHand/Touch/Back",
        "left_bumper": "Bumper/FrontLeft",
        "right_bumper": "Bumper/FrontRight",
        "back_bumper": "Bumper/Back",
    }

    def check_touch_sensor(self, sensor_name):
        """
        Queries the robot whether the requested touch sensor has been activated since it was last queried.

        The robot has the the following sensors:
        - 'head_front', 'head_middle', 'head_rear' on the top of tis head.
        - 'left_hand', 'right_hand' on the back of each hand.
        - 'left_bumper', 'right_bumper', 'back_bumper' on its wheel base.

        Parameters
        ----------
        sensor_name: string
            One of the sensor names given above
        """
        if sensor_name not in self.TOUCH_SENSOR_NAMES:
            raise ValueError(f"{sensor_name} is not a valid touch sensor!")
        touch_check_cmd = {
            "type": "check_touch",
            "sensor": self.TOUCH_SENSOR_NAMES[sensor_name],
        }
        self._send_command(touch_check_cmd)
        response = self._wait_for_response_type("touch")
        return response["was_triggered"]

    def __del__(self):
        if self.socket:
            self.socket.close()

    def _send_command(self, command):
        command_id = self.next_command_id
        command["command_id"] = command_id
        self.next_command_id += 1
        payload = msgpack.packb(command)
        self.socket.send(payload)
        return command_id

    def _await_completion(self, command_id):
        while True:
            completion = self._wait_for_response_type("completion")
            if completion["command_id"] == command_id:
                return

    def _receive_response(self):
        # First we need to check whether we have any previously received but not yet parsed messages
        for msg in self.unpacker:
            return msg
        # If not, we read from the network buffer, feed it into the unpacker and check again
        while True:
            self.unpacker.feed(self.socket.recv(4096))
            for msg in self.unpacker:
                return msg

    def _wait_for_response_type(self, response_type):
        while True:
            response = self._receive_response()
            if "type" in response and response["type"] == response_type:
                return response

    def shutdown(self):
        if self.socket:
            shutdown_cmd = {
                'type': 'shutdown'
            }
            self._send_command(shutdown_cmd)
            self.socket.close()
