import cv2
import mediapipe as mp
import numpy as np
import math
import time
import sys

from game_ui import GameUI
from PunchDetector import PunchDetector
from sound_effect import SoundEffect
from Speed import Speed
from datetime import datetime
from punchanimation import PunchAnimation

# from blaizian.cv2constants import CV_VIDEO_CAPTURE_DEVICE

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

punchanimation = PunchAnimation("assets/punchanimation.gif")

QUEUE_SIZE = 10
COOLDOWN = 0

game_ui = GameUI()
punch_detector = PunchDetector()
speed = Speed(QUEUE_SIZE)
punch_sound = SoundEffect(
    "assets/Punch.mp3", cooldown=1.0
)  # Set a 1-second cooldown for the punch sound
ignore_left, ignore_right = 0, 0

duration = 100
start_time = datetime.now()


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def detectBlock(landmarks):
    """
    Simple logic to detect a block:
    Checks if elbows are tucked into shoulders and wrists are covering face
    """
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

    # Detect a "block" motion
    left_tuck = (
        calculate_distance(
            [left_elbow.x, left_elbow.y], [left_shoulder.x, left_shoulder.y]
        )
        < 0.05
    )
    right_tuck = (
        calculate_distance(
            [right_elbow.x, right_elbow.y], [right_shoulder.x, right_shoulder.y]
        )
        < 0.05
    )

    left_wrist_face = (
        calculate_distance([left_wrist.x, left_wrist.y], [nose.x, nose.y]) < 0.1
    )
    right_wrist_face = (
        calculate_distance([right_wrist.x, right_wrist.y], [nose.x, nose.y]) < 0.1
    )

    return left_tuck and right_tuck and left_wrist_face and right_wrist_face


class VideoCamera(object):
    def __init__(self, page_width, page_height):
        self.video = cv2.VideoCapture(1)
        # FIX BELOW
        self.video.set(3, page_width / 1.75)  # 3 -> WIDTH
        self.video.set(4, page_height / 1.75)  # 4 -> HEIGHT

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    def get_block(self):
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                print("Error: Cannot access the camera.")
                break

            # Flip the frame for a mirrored effect
            frame = cv2.flip(frame, 1)

            # Convert frame to RGB (required by MediaPipe)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

                # Extract landmarks
                landmarks = results.pose_landmarks.landmark

                # Detect jabs
                block = detectBlock(landmarks)
                if block:
                    cv2.putText(
                        frame,
                        "Block",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes()

    def score_mode(self):
        global ignore_left, ignore_right
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                print("Error accessing the camera.")
                break

            # Flip the frame for a mirrored view
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe
            results = pose.process(rgb_frame)

            # Get time and show timer
            active_time = (
                duration - (datetime.now() - start_time).seconds
            )  # converting into seconds

            if active_time > 0:
                cv2.putText(
                    frame,
                    str(active_time),
                    (frame.shape[1] - 100, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 0, 0),
                    3,
                )
            else:
                # Define the text
                text = "GAME OVER!"

                # Font settings
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 3
                color = (0, 0, 225)  # Red color
                thickness = 5

                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(
                    text, font, font_scale, thickness
                )

                # Calculate the position for the text to appear in the center
                frame_height, frame_width, _ = frame.shape
                x = (frame_width - text_width) // 2
                y = (frame_height + text_height) // 2
                cv2.putText(
                    frame,
                    text,
                    (x + 2, y + 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    color,
                    thickness,
                )

            # Update the game command
            game_ui.update_command()

            # Get the current time
            current_time = time.time()

            if results.pose_landmarks:
                if 0 < ignore_left <= COOLDOWN:
                    ignore_left += 1
                else:
                    ignore_left = 0

                if 0 < ignore_right <= COOLDOWN:
                    ignore_right += 1
                else:
                    ignore_right = 0
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

                # Extract landmarks
                landmarks = results.pose_landmarks.landmark
                left_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                left_hand = landmarks[mp_pose.PoseLandmark.RIGHT_INDEX.value]

                right_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_hand = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]

                right_wrist_position = (
                    right_wrist.x * frame.shape[1],
                    right_wrist.y * frame.shape[0],
                )
                left_wrist_position = (
                    left_wrist.x * frame.shape[1],
                    left_wrist.y * frame.shape[0],
                )

                right_hand_position = (
                    right_hand.x * frame.shape[1],
                    right_hand.y * frame.shape[0],
                )
                left_hand_position = (
                    left_hand.x * frame.shape[1],
                    left_hand.y * frame.shape[0],
                )

                right_average, left_average = speed.calculate_speeds(
                    current_time, right_wrist_position, left_wrist_position
                )

                # Detect punches
                left_jab, right_jab = punch_detector.detect_jab(
                    left_wrist,
                    left_shoulder,
                    left_average,
                    right_wrist,
                    right_shoulder,
                    right_average,
                )

                # Check for correct punches based on the current command
                current_command = game_ui.current_command
                if current_command == "Left Jab" and left_jab and not ignore_left:
                    ignore_left += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(left_hand_position)
                        game_ui.increment_score()
                        game_ui.clear_command()

                elif current_command == "Right Jab" and right_jab and not ignore_right:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_hand_position)
                        game_ui.increment_score()
                        game_ui.clear_command()

            # Display the game UI (commands and score)
            frame = punchanimation.draw(frame)

            frame = game_ui.display(frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes()

    def free_mode(self):
        global ignore_left, ignore_right
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                print("Error accessing the camera.")
                break

            # Flip the frame for a mirrored view
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe
            results = pose.process(rgb_frame)

            # Get the current time
            current_time = time.time()

            if results.pose_landmarks:
                if 0 < ignore_left <= COOLDOWN:
                    ignore_left += 1
                else:
                    ignore_left = 0

                if 0 < ignore_right <= COOLDOWN:
                    ignore_right += 1
                else:
                    ignore_right = 0
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

                # Extract landmarks
                landmarks = results.pose_landmarks.landmark
                left_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                left_hand = landmarks[mp_pose.PoseLandmark.RIGHT_INDEX.value]

                right_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_hand = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]

                right_wrist_position = (
                    right_wrist.x * frame.shape[1],
                    right_wrist.y * frame.shape[0],
                )
                left_wrist_position = (
                    left_wrist.x * frame.shape[1],
                    left_wrist.y * frame.shape[0],
                )

                right_hand_position = (
                    right_hand.x * frame.shape[1],
                    right_hand.y * frame.shape[0],
                )
                left_hand_position = (
                    left_hand.x * frame.shape[1],
                    left_hand.y * frame.shape[0],
                )

                right_average, left_average = speed.calculate_speeds(
                    current_time, right_wrist_position, left_wrist_position
                )

                # Detect punches
                left_jab, right_jab = punch_detector.detect_jab(
                    left_wrist,
                    left_shoulder,
                    left_average,
                    right_wrist,
                    right_shoulder,
                    right_average,
                )

                # Check for correct punches based on the current command
                if left_jab and not ignore_left:
                    ignore_left += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(left_hand_position)

                elif right_jab and not ignore_right:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_hand_position)

            # Display the game UI (commands and score)
            frame = punchanimation.draw(frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes()
