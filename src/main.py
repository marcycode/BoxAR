import cv2
import mediapipe as mp
import time
from game_ui import GameUI
from PunchDetector import PunchDetector
from sound_effect import SoundEffect
from Speed import Speed

QUEUE_SIZE = 10
COOLDOWN = 0
# Initialize components
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

game_ui = GameUI()
punch_detector = PunchDetector()
speed = Speed(QUEUE_SIZE)
punch_sound = SoundEffect("sound/Punch.mp3", cooldown=1.0)  # Set a 1-second cooldown for the punch sound
ignore_left, ignore_right = 0, 0
# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error accessing the camera.")
        break

    # Flip the frame for a mirrored view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = pose.process(rgb_frame)

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
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract landmarks
        landmarks = results.pose_landmarks.landmark
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hand = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]

        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_INDEX.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

        right_wrist_position = (right_wrist.x * frame.shape[1], right_wrist.y * frame.shape[0])
        left_wrist_position = (left_wrist.x * frame.shape[1], left_wrist.y * frame.shape[0])

        right_average, left_average = speed.calculate_speeds(current_time, right_wrist_position, left_wrist_position)

        # Detect punches
        left_jab, right_jab = punch_detector.detect_jab(left_wrist, left_shoulder, left_average,
                                                        right_wrist, right_shoulder, right_average)

        # Check for correct punches based on the current command
        current_command = game_ui.current_command
        if current_command == "Left Jab" and left_jab and not ignore_left:
            ignore_left += 1
            if punch_sound.play():  # Play sound with cooldown
                game_ui.increment_score()
                game_ui.clear_command()
        elif current_command == "Right Jab" and right_jab and not ignore_right:
            ignore_right += 1
            if punch_sound.play():  # Play sound with cooldown
                game_ui.increment_score()
                game_ui.clear_command()


    # Display the game UI (commands and score)
    frame = game_ui.display(frame)

    # Show the video feed
    cv2.imshow("Punch Detection Game", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
