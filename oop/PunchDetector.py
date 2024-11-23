import mediapipe as mp
import math
import time
from pygame import mixer
import cv2


class PunchDetector:
    """Singleton class for detecting different types of punches."""

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PunchDetector, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize Pygame mixer for punch sound
        mixer.init()
        self.punch_sound = mixer.Sound("Punch.mp3")  # Replace with your sound file path

        # Variables for punch cooldown and reset
        self.last_punch_time = 0
        self.punch_cooldown = 0.5  # Minimum time between punches
        self.punch_active = {"left_jab": False, "right_jab": False}

    def detect_jab(self, leftWrist, leftShoulder, leftElbow, rightWrist, rightShoulder, rightElbow):
        """
        Detect a jab motion using x, z coordinates of wrist, shoulder, and elbow.
        """
        # Calculate relative forward motion using x and z coordinates
        left_jab = (leftWrist[0] < leftShoulder[0] + 0.1 and
                    leftWrist[2] < leftElbow[2] - 0.1)  # Forward motion in z
        right_jab = (rightWrist[0] > rightShoulder[0] - 0.1 and
                     rightWrist[2] < rightElbow[2] - 0.1)  # Forward motion in z

        return left_jab, right_jab

    def process_pose(self, landmarks, frame, current_time, game_ui):
        """
        Process pose landmarks to detect punches, check against the current command,
        play sound, and update score.
        """
        # Extract landmark positions
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].z]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].z]
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]

        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].z]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]

        # Detect jabs
        left_jab, right_jab = self.detect_jab(left_wrist, left_shoulder, left_elbow,
                                              right_wrist, right_shoulder, right_elbow)

        # Check against current command
        if left_jab and game_ui.current_command == "Left Jab" and not self.punch_active["left_jab"]:
            self.trigger_punch("Left Jab", current_time, game_ui)
            self.punch_active["left_jab"] = True
        elif not left_jab:
            self.punch_active["left_jab"] = False  # Reset state for next detection

        if right_jab and game_ui.current_command == "Right Jab" and not self.punch_active["right_jab"]:
            self.trigger_punch("Right Jab", current_time, game_ui)
            self.punch_active["right_jab"] = True
        elif not right_jab:
            self.punch_active["right_jab"] = False  # Reset state for next detection

        # Debugging: Display key points
        self.debug_landmarks(frame, landmarks)

        return frame

    def trigger_punch(self, punch_type, current_time, game_ui):
        """Trigger punch logic: play sound, update score, and apply cooldown."""
        if current_time - self.last_punch_time > self.punch_cooldown:
            game_ui.increment_score()
            self.play_punch_sound()
            self.last_punch_time = current_time

    def play_punch_sound(self):
        """Play punch sound."""
        self.punch_sound.play()

    def debug_landmarks(self, frame, landmarks):
        """Display key landmark positions for debugging."""
        for i, landmark in enumerate(landmarks):
            x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
            cv2.putText(frame, f"{i}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
