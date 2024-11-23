import mediapipe as mp
import cv2
from pygame import mixer
import time
import threading


class PunchTracker:
    """Tracks punches based on wrist and shoulder positions."""

    def __init__(self, game_ui):
        self.game_ui = game_ui

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize Pygame mixer for punch sound
        mixer.init()
        self.punch_sound = mixer.Sound("Punch.mp3")  # Replace with your sound file path
        self.punch_sound.set_volume(1.0)  # Ensure max volume
        self.channel = mixer.Channel(0)  # Assign dedicated channel for punch sound

        # Variables for punch cooldown and state
        self.last_punch_time = 0
        self.punch_cooldown = 1  # Cooldown time (in seconds) between punch sounds
        self.punch_active = {"left_jab": False, "right_jab": False}  # Track ongoing punches

        # Threading for asynchronous MediaPipe processing
        self.lock = threading.Lock()
        self.latest_results = None

    def detect_jab(self, landmarks):
        """
        Detect a jab motion based on wrist and shoulder positions.
        A jab is detected if the wrist moves forward (in the x-axis) relative to the shoulder.
        """
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]

        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]

        # Detect jabs based on forward motion (x-axis) and position relative to the elbow
        left_jab = (left_wrist.x > left_shoulder.x + 1.2 and
                    left_wrist.x > left_elbow.x)
        right_jab = (right_wrist.x < right_shoulder.x - 1.2 and
                     right_wrist.x < right_elbow.x)

        return right_jab, left_jab

    def process_frame(self, frame):
        """
        Process the frame, detect punches, play sound with cooldown, and update the score.
        """
        current_time = time.time()  # Track current time for cooldown logic

        # Convert the frame to RGB (required by MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Asynchronous MediaPipe processing
        self.run_pose_processing(rgb_frame)

        # Access the latest processed results
        with self.lock:
            results = self.latest_results

        if results and results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Detect jabs
            right_jab, left_jab = self.detect_jab(results.pose_landmarks.landmark)

            # Process left jab
            if self.game_ui.current_command == "Left Jab" and left_jab and not self.punch_active["left_jab"]:
                if self.play_punch_sound(current_time):  # Only increment score if sound is played
                    self.game_ui.increment_score()
                    self.punch_active["left_jab"] = True  # Mark punch as active

            # Reset left jab state when punch ends
            if not left_jab:
                self.punch_active["left_jab"] = False

            # Process right jab
            if self.game_ui.current_command == "Right Jab" and right_jab and not self.punch_active["right_jab"]:
                if self.play_punch_sound(current_time):  # Only increment score if sound is played
                    self.game_ui.increment_score()
                    self.punch_active["right_jab"] = True  # Mark punch as active

            # Reset right jab state when punch ends
            if not right_jab:
                self.punch_active["right_jab"] = False

        return frame

    def play_punch_sound(self, current_time):
        """
        Play punch sound with cooldown to avoid rapid repetition.

        Returns:
            bool: True if the sound was played, False if on cooldown.
        """
        if current_time - self.last_punch_time > self.punch_cooldown:
            self.channel.play(self.punch_sound)
            self.last_punch_time = current_time
            return True
        return False

    def run_pose_processing(self, rgb_frame):
        """
        Run MediaPipe pose processing asynchronously to reduce frame processing time.
        """
        def process():
            results = self.pose.process(rgb_frame)
            with self.lock:
                self.latest_results = results

        threading.Thread(target=process, daemon=True).start()
