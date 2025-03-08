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
import socket
import numpy as np
import math
import threading
import cv2
from pupil_apriltags import Detector



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
                remaining = int.from_bytes(
                    client_socket.recv(4), byteorder='little')
                image_data = bytearray()

                # Read the image data
                while remaining > 0:
                    data = client_socket.recv(remaining)
                    remaining -= len(data)
                    image_data += data

                # Decode the full image
                image = cv2.imdecode(np.frombuffer(
                    image_data, np.uint8), cv2.IMREAD_COLOR)
                
                # Set the frame so we can access it from the main thread
                self.frame = {'image': image}

                # Convert the image to gray to detect the tags
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Detect the tags
                tags = self.detector.detect(gray)

                # Dimensions of the image
                height, width, _ = image.shape

                # Middle bottom of the image, i.e. the center of the bottom of the image (where the robot should aligns itself)
                self.middle_bottom = (width // 2, height)

                # Initialize the target distance and center
                min_tag_distance = np.inf  # Distance to the closest tag
                # Center of the closest tag initialized to the middle bottom of the image
                tag_center = self.middle_bottom
                tag_corners = None  # Corners of the closest tag
                
                if len(tags) == 0:
                    self.tag_in_view = False
                    continue

                # Go through each of the tags in the image found by the detector
                for tag in tags:

                    # get the center of the tag and calculate the distance to the bottom middle of the image
                    center = tuple([int(x) for x in tag.center])
                    distance = math.sqrt(
                        (center[0] - self.middle_bottom[0])**2 + (center[1] - self.middle_bottom[1])**2)
                    if distance < min_tag_distance:
                        min_tag_distance = distance
                        tag_center = center
                        tag_corners = tag.corners
                        closest_tag_id = tag.tag_id

                # Draw an outline of the target tag
                if tag_corners is not None:
                    for i in range(len(tag_corners)):
                        cv2.line(image, tuple(tag_corners[i-1, :].astype(int)), tuple(
                            tag_corners[i, :].astype(int)), (0, 0, 255), 2)

                    # Set the closest tag which is the tag with the shortest distance to the bottom middle of the image
                    self.closest_tag = {
                        'distance': min_tag_distance,
                        'tag_center': tag_center,
                        'corners': tag_corners,
                        'id': closest_tag_id}

                    self.tag_in_view = True
                else:
                    self.tag_in_view = False

            except:
                continue

            client_socket.close()

    def stop(self):
        self.stop_event.set()