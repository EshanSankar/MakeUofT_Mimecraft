import socket
import sys
import threading
import json
import serial
import struct
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
from screeninfo import get_monitors
import pygetwindow as gw
import time
from utils import *
import mediapipe as mp
import cv2
import math

# Global variables for thread
MAX_X = get_monitors()[0].width
MAX_Y = get_monitors()[0].height


# Serial Reader Thread
#####################################
class SerialReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('COM5', 115200, timeout=1)
        self.roll = 0.0
        self.pitch = 0.0
        self.running = True
        self.lock = threading.Lock()
        self.ser.reset_input_buffer()

    def run(self):
        while self.running:
            roll, pitch = self.read_packet()
            if roll is not None and pitch is not None:
                with self.lock:
                    self.roll = roll
                    self.pitch = pitch

    def read_packet(self):
        while self.running:
            byte = self.ser.read(1)
            if byte == b'\xAA':
                next_byte = self.ser.read(1)
                if next_byte == b'\x55':
                    break
        data = self.ser.read(8)
        if len(data) != 8:
            return None, None
        roll = struct.unpack('<f', data[:4])[0]
        pitch = struct.unpack('<f', data[4:])[0]
        return roll, pitch

    def stop(self):
        self.running = False
        self.ser.close()


# Camera Processor Thread
#####################################
class CameraProcessor(threading.Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = True
        self.frame = None
        self.lock = threading.Lock()
        self.results = None
        self.prev_states = []
        self.prev_right_arm = None
        self.prev_left_arm = None

    def run(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_holistic = mp.solutions.holistic
        
        cap = cv2.VideoCapture(0)
        
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Process frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Update shared data
                with self.lock:
                    self.results = results
                    self.frame = image
                
                # Detect commands
                self.detect_commands(results)
                
                # Display
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
                cv2.imshow("Output", image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        cap.release()
        cv2.destroyAllWindows()

    def detect_commands(self, results):
        commands = {
            "keyboard": "w_release",
            "right_click": False,
            "left_click": False,
        }

        is_walking, self.prev_states = check_walking(
            results.pose_landmarks, self.prev_states
        )
        right_arm, self.prev_right_arm = detect_arm_swing(
            results.pose_landmarks, self.prev_right_arm
        )
        left_arm, self.prev_left_arm = detect_arm_swing(
            results.pose_landmarks, self.prev_left_arm
        )

        commands["keyboard"] = "w_press" if is_walking else "w_release"
        commands["right_click"] = right_arm
        commands["left_click"] = left_arm

        self.controller.handle_command(commands)

    def stop(self):
        self.running = False


# Input Controller
#####################################
class InputController:
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.current_keys = set()
        self.scaling_factor = 0.01
        self.initialize = False
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_roll = 0
        self.current_pitch = 0

    def handle_keyboard(self, keyboard_data):
        if keyboard_data == "w_press" and "w" not in self.current_keys:
            self.keyboard.press("w")
            self.current_keys.add("w")
        elif keyboard_data == "w_release" and "w" in self.current_keys:
            self.keyboard.release("w")
            self.current_keys.remove("w")

    def handle_mouse(self, right_click, left_click):
        if right_click:
            self.mouse.click(Button.right)
        if left_click:
            self.mouse.click(Button.left)
            
    def handle_eyes(self, y, x):
        y = -1 * y
        if (x < 10 and x > -10) and (y < 10 and y > -10): 
            self.mouse.position = (MAX_X/2, MAX_Y/2)
            return
        
        if x > 10 or x < -10:        
            dx = x * self.scaling_factor
        else:
            dx = 0
        if y > 10 or y < -10:
            dy = y * self.scaling_factor
        else:
            dy = 0
        
        # print(f"Dx : {dx} | Dy : {dy}")

        # Get current position and calculate new position
        if (not self.initialize):
            current_x, current_y = self.mouse.position
            self.current_x = current_x
            self.current_y = current_y
            self.initialize = True
            self.current_roll = x
            self.current_pitch = y
        
            
        if (self.current_roll > x and dx > 0) or (self.current_roll < x and dx < 0): 
            # dx = 0
            # self.current_roll = x
            self.current_x = MAX_X / 2
            dx = 0
        if (self.current_pitch > y and dy > 0) or (self.current_pitch < y and dy < 0):
            # dy = 0
            # self.current_pitch = y
            self.current_y = MAX_Y / 2 
            dy = 0
        
        self.current_roll = x
        self.current_pitch = y
        
        new_x = min(self.current_x + dx, MAX_X)
        new_y = min(self.current_y + dy, MAX_Y)

        self.current_x = new_x
        self.current_y = new_y

        # Move mouse absolutely to clamped position
        self.mouse.position = (int(new_x), int(new_y))
        

    def handle_command(self, data):
        self.handle_keyboard(data["keyboard"])
        self.handle_mouse(data["right_click"], data["left_click"])


if __name__ == "__main__":
    controller = InputController()
    
    # Start threads
    serial_thread = SerialReader()
    camera_thread = CameraProcessor(controller)
    
    serial_thread.start()
    camera_thread.start()

    try:
        while True:
            # Get latest serial data
            with serial_thread.lock:
                roll = serial_thread.roll
                pitch = serial_thread.pitch
            
            # Handle eye tracking in main thread
            controller.handle_eyes(roll, pitch)
            
            time.sleep(0.001)

    except KeyboardInterrupt:
        # Cleanup
        serial_thread.stop()
        camera_thread.stop()
        serial_thread.join()
        camera_thread.join()