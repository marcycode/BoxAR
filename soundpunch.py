import cv2
import mediapipe as mp
import time
import math
from pygame import mixer
from cv2constants import CV_VIDEO_CAPTURE_DEVICE

# Initialize Pygame mixer for sound
mixer.init()
# Replace 'punch.wav' with your sound file
punch_sound = mixer.Sound("Punch.mp3")

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(CV_VIDEO_CAPTURE_DEVICE)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Variables to track wrist positions and time
prev_time = 0
prev_wrist_position = None
last_punch_time = 0
punch_cooldown = 0.5  # Minimum time (seconds) between punch sounds


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error accessing the camera.")
        break

    start_time = time.time()  # Measure processing time per frame

    # Flip the frame and convert to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = pose.process(rgb_frame)

    # Get the current time
    current_time = time.time()

    if results.pose_landmarks:
        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Get the right wrist coordinates
        wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        wrist_position = (wrist.x * frame.shape[1], wrist.y * frame.shape[0])

        # If a previous wrist position exists, calculate speed
        if prev_wrist_position is not None:
            displacement = calculate_distance(
                wrist_position, prev_wrist_position)
            time_diff = current_time - prev_time

            if time_diff > 0:  # Avoid division by zero
                speed = displacement / time_diff

                # Display the speed on the video frame
                cv2.putText(frame, f"Speed: {speed:.2f} px/s", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if speed > 150 and current_time - last_punch_time > punch_cooldown:
                    cv2.putText(frame, "PUNCH!", (100, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                    punch_sound.play()
                    last_punch_time = current_time

        prev_wrist_position = wrist_position
        prev_time = current_time

    # Show the video frame
    cv2.imshow("Wrist Speed Tracking", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Measure and display frame processing time
    processing_time = time.time() - start_time
    print(f"Processing Time: {processing_time:.2f} seconds")

cap.release()
cv2.destroyAllWindows()
