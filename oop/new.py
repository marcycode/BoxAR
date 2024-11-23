import cv2
import mediapipe as mp
import random
import time

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

# Game variables
score = 0
current_command = None
command_time = 0
command_interval = 5  # New command every 5 seconds


def generate_command():
    """Generate a random command: 'Left Jab' or 'Right Jab'."""
    return random.choice(["Left Jab", "Right Jab"])


def detect_jab(landmarks):
    """
    Detect a jab motion based on wrist and shoulder positions.
    A jab is detected if the wrist moves forward (in the x-axis) relative to the shoulder.
    """
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    # Detect jabs
    left_jab = left_wrist.x > left_shoulder.x + 0.1  # Left jab threshold
    right_jab = right_wrist.x < right_shoulder.x - 0.1  # Right jab threshold

    return right_jab, left_jab


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot access the camera.")
        break

    # Flip the frame for a mirrored effect
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB (required by MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Update command every `command_interval` seconds
    if time.time() - command_time > command_interval:
        current_command = generate_command()
        command_time = time.time()

    # Draw pose landmarks and detect jabs
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        # Extract landmarks
        landmarks = results.pose_landmarks.landmark

        # Detect jabs
        right_jab, left_jab = detect_jab(landmarks)

        # Check if the detected jab matches the current command
        if current_command == "Left Jab" and left_jab:
            score += 1
            current_command = None  # Reset command until the next interval
        elif current_command == "Right Jab" and right_jab:
            score += 1
            current_command = None  # Reset command until the next interval

        # Display jab detection
        if left_jab:
            cv2.putText(frame, "Left Jab!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if right_jab:
            cv2.putText(frame, "Right Jab!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the current command and score
    if current_command:
        cv2.putText(frame, f"Command: {current_command}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(frame, f"Score: {score}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Show the video feed
    cv2.imshow("Jab Detection Game", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
