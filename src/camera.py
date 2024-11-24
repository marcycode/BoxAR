import cv2
import mediapipe as mp
import numpy as np
import math
import time
import sys

from game_ui import GameUI
from punch_detector import PunchDetector
from sound_effect import SoundEffect
from speed import Speed
from datetime import datetime
from punch_animation import PunchAnimation
from challenge import ChallengeManager
from multiplayer import MultiPlayerManager, MultiPlayerConnectionData
from update_hook import EventManager
from observer import CollisionObserver
from cooldown_bar import CooldownBar
from cv2constants import CV_VIDEO_CAPTURE_DEVICE
import os
from block import Block

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
block = Block()

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

duration = 30
start_time = datetime.now()


class VideoCamera(object):
    def __init__(
        self, page_width, page_height, multiplayerData: MultiPlayerConnectionData = None
    ):
        self.video = cv2.VideoCapture(CV_VIDEO_CAPTURE_DEVICE)
        # FIX BELOW
        self.video.set(3, page_width / 1.75)  # 3 -> WIDTH
        self.video.set(4, page_height / 1.75)  # 4 -> HEIGHT
        FRAME_WIDTH = int(self.video.get(
            cv2.CAP_PROP_FRAME_WIDTH))  # int `width`
        FRAME_HEIGHT = int(self.video.get(
            cv2.CAP_PROP_FRAME_HEIGHT))  # int `height`
        CHALLENGE_START_SIZE = 50

        os.environ["FRAME_WIDTH"] = f"{FRAME_WIDTH}"
        os.environ["FRAME_HEIGHT"] = f"{FRAME_HEIGHT}"

        self.collisionObserver = CollisionObserver()
        self.challengeManager = ChallengeManager()

        self.multiplayerManager = None
        if multiplayerData:
            self.multiplayerManager = MultiPlayerManager(
                multiplayerData.peer_ip,
                multiplayerData.peer_port,
                self.challengeManager,
            )

        self.eventManager = EventManager()
        if not multiplayerData:
            self.eventManager.addEvent(
                "generatePunchChallenge",
                100,
                self.challengeManager.generatePunchChallenge,
                ["frameWidth", "frameHeight", "startSize", "observer"],
            )
        self.eventManager.addEvent(
            "update_challenges",
            5,
            self.challengeManager.update_challenges,
            ["landmarks"],
        )

        self.drawManager = EventManager()
        self.drawManager.addEvent(
            "draw_challenges", 1, self.challengeManager.drawChallenges, [
                "frame"]
        )
        self.context = {
            "frameWidth": FRAME_WIDTH,
            "frameHeight": FRAME_HEIGHT,
            "startSize": CHALLENGE_START_SIZE,
            "observer": self.collisionObserver,
        }
        self.health = 5
        self.duration = 30  # Timer for scoring mode
        self.start_time = datetime.now()  # Initialize timer start time
        self.cooldownBar = CooldownBar(30)

    def restart(self):
        """Reset game state for both scoring and survival modes."""
        self.health = 5  # Reset health for survival mode
        self.start_time = datetime.now()  # Reset timer for scoring mode
        game_ui.reset_score()  # Reset score

    def score_mode(self):
        global ignore_left, ignore_right
        flag = True
        self.cooldownBar.setMaxCooldown(30)
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

            self.context["frame"] = frame
            self.context["landmarks"] = results.pose_landmarks

            # Get time and show timer
            active_time = self.duration - \
                (datetime.now() - self.start_time).seconds

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
                flag = False

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
                        self.cooldownBar.resetCooldown()

                elif current_command == "Right Jab" and right_jab and not ignore_right:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_hand_position)
                        game_ui.increment_score()
                        game_ui.clear_command()
                        self.cooldownBar.resetCooldown()

            collisions = self.collisionObserver.getCollisionCount()
            self.eventManager.update(self.context)
            self.drawManager.update(self.context)
            if collisions == self.collisionObserver.getCollisionCount() - 1:
                game_ui.decrement_score()

            # Display the game UI (commands and score)
            frame = punchanimation.draw(frame)

            frame = game_ui.display(frame)

            self.cooldownBar.displayCooldown(frame)
            self.cooldownBar.updateCooldown()

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes(), flag, game_ui.score

    def free_mode(self):
        global ignore_left, ignore_right
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                print("Error accessing the camera in free_mode.")
                break

            # Flip the frame for a mirrored view
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe
            results = pose.process(rgb_frame)
            if results.pose_landmarks:
                print("Landmarks detected.")  # Debug line
            else:
                print("No landmarks detected.")  # Debug line

            self.context["frame"] = frame
            self.context["landmarks"] = results.pose_landmarks

            # Get the current time
            current_time = time.time()

            if results.pose_landmarks:
                if 0 < ignore_left <= COOLDOWN:
                    ignore_left += 1
                else:
                    ignore_left = 0
                    game_ui.reset_cooldown()

                if 0 < ignore_right <= COOLDOWN:
                    ignore_right += 1
                else:
                    ignore_right = 0
                    game_ui.reset_cooldown()

                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

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

                if left_jab and not ignore_left:
                    ignore_left += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(left_hand_position)
                        game_ui.increment_score()
                        game_ui.clear_command()

                elif right_jab and not ignore_right:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_hand_position)
                        game_ui.increment_score()
                        game_ui.clear_command()

            # Update the game frame with animations and UI
            frame = punchanimation.draw(frame)
            frame = game_ui.display(frame)

            try:
                ret, jpeg = cv2.imencode(".jpg", frame)

            except Exception as e:
                print(f"Error encoding frame: {e}")
                continue

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Exiting free_mode.")
                break

            return jpeg.tobytes()

    def survival_mode(self):
        global ignore_left, ignore_right
        flag = True
        self.cooldownBar.setMaxCooldown(15)
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

            self.context["frame"] = frame
            self.context["landmarks"] = results.pose_landmarks

            if self.health > 0:
                # Health Bar Dimensions
                # X-coordinate of the health bar
                bar_x = (frame.shape[1] // 4) * 3
                bar_y = 50  # Y-coordinate of the health bar
                bar_width = 300  # Full width of the health bar
                bar_height = 30  # Height of the health bar

                # Calculate current health bar width
                current_bar_width = int(
                    (self.health / 20) * bar_width
                )  # Assuming max health = 20

                # Draw the background (gray bar)
                cv2.rectangle(
                    frame,
                    (bar_x, bar_y),
                    (bar_x + bar_width, bar_y + bar_height),
                    (50, 50, 50),
                    -1,
                )

                # Determine bar color based on health
                bar_color = (
                    (0, 255, 0)
                    if self.health > 10
                    else (0, 255, 255) if self.health > 5 else (0, 0, 255)
                )

                # Draw the current health bar
                cv2.rectangle(
                    frame,
                    (bar_x, bar_y),
                    (bar_x + current_bar_width, bar_y + bar_height),
                    bar_color,
                    -1,
                )

                # Add text for health
                cv2.putText(
                    frame,
                    f"Health: {self.health}/20",
                    (bar_x, bar_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
            else:
                # Define the text
                text = "GAME OVER!"

                # Font settings
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 3
                color = (0, 0, 255)  # Red color
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
                flag = False

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
                        punchanimation.trigger(left_wrist_position)
                        game_ui.increment_score()
                        game_ui.clear_command()
                        self.cooldownBar.resetCooldown()

                elif current_command == "Right Jab" and right_jab and not ignore_right:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_wrist_position)
                        game_ui.increment_score()
                        game_ui.clear_command()
                        self.cooldownBar.resetCooldown()

            collisions = self.collisionObserver.getCollisionCount()
            self.eventManager.update(self.context)
            self.drawManager.update(self.context)
            if collisions == self.collisionObserver.getCollisionCount() - 1:
                self.health -= 1

            # Display the game UI (commands and score)
            frame = punchanimation.draw(frame)

            frame = game_ui.display(frame)

            self.cooldownBar.displayCooldown(frame)
            self.cooldownBar.updateCooldown()

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes(), flag, game_ui.score

    def multiplayer_mode(self):
        global ignore_left, ignore_right
        flag = True
        self.cooldownBar.setMaxCooldown(15)

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

            self.context["frame"] = frame
            self.context["landmarks"] = results.pose_landmarks

            # Display health bar
            if self.health > 0:
                # Health Bar Dimensions
                # X-coordinate of the health bar
                bar_x = (frame.shape[1] // 4) * 3
                bar_y = 50  # Y-coordinate of the health bar
                bar_width = 300  # Full width of the health bar
                bar_height = 30  # Height of the health bar

                # Calculate current health bar width
                current_bar_width = int((self.health / 20) * bar_width)  # Assuming max health = 20

                # Draw the background (gray bar)
                cv2.rectangle(
                    frame,
                    (bar_x, bar_y),
                    (bar_x + bar_width, bar_y + bar_height),
                    (50, 50, 50),
                    -1,
                )

                # Determine bar color based on health
                bar_color = (
                    (0, 255, 0) if self.health > 10 else (0, 255, 255) if self.health > 5 else (0, 0, 255)
                )

                # Draw the current health bar
                cv2.rectangle(
                    frame,
                    (bar_x, bar_y),
                    (bar_x + current_bar_width, bar_y + bar_height),
                    bar_color,
                    -1,
                )

                # Add text for health
                cv2.putText(
                    frame,
                    f"Health: {self.health}/20",
                    (bar_x, bar_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
            else:
                # Define the text
                text = "GAME OVER!"

                # Font settings
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 3
                color = (0, 0, 255)  # Red color
                thickness = 5

                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(
                    text, font, font_scale, thickness)

                # Calculate the position for the text to appear in the center
                frame_height, frame_width, _ = frame.shape
                x = (frame_width - text_width) // 2
                y = (frame_height + text_height) // 2
                cv2.putText(frame, text, (x + 2, y + 2), font,
                            font_scale, color, thickness)

                flag = False

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

                if left_jab and not ignore_left and self.multiplayerManager:
                    ignore_left += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(left_hand_position)
                        self.cooldownBar.resetCooldown()
                    self.multiplayerManager.sendPunch(
                        (left_wrist.x, left_wrist.y))

                if right_jab and not ignore_right and self.multiplayerManager:
                    ignore_right += 1
                    if punch_sound.play():  # Play sound with cooldown
                        punchanimation.trigger(right_hand_position)
                        self.cooldownBar.resetCooldown()
                    self.multiplayerManager.sendPunch(
                        (right_wrist.x, right_wrist.y))

            collisions = self.collisionObserver.getCollisionCount()
            self.eventManager.update(self.context)
            self.drawManager.update(self.context)
            if collisions <= self.collisionObserver.getCollisionCount() - 1:
                self.health -= 1

            # Display the game UI (commands and score)
            frame = punchanimation.draw(frame)

            # Display the cooldown bar
            self.cooldownBar.displayCooldown(frame)
            self.cooldownBar.updateCooldown()

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, jpeg = cv2.imencode(".jpg", frame)
            return jpeg.tobytes(), flag
