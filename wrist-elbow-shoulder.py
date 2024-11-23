import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

def detect_jab(landmarks):
    """
    Simple logic to detect a jab: 
    Checks if the wrist moves forward (in the x-axis) relative to the shoulder.
    """
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    # Detect a "jab" motion
    print(left_wrist, left_shoulder)
    print(right_wrist, right_shoulder)
    left_jab = left_wrist.x > left_shoulder.x + 0.1 and left_wrist.x >= left_elbow.x # Left jab threshold
    right_jab = right_wrist.x < right_shoulder.x - 0.1  and right_wrist.x <= right_elbow.x # Right jab threshold

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

    # Draw pose landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        # Extract landmarks
        landmarks = results.pose_landmarks.landmark

        # Detect jabs
        left_jab, right_jab = detect_jab(landmarks)
        if left_jab:
            print(left_jab)
            cv2.putText(frame, "Left Jab!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if right_jab:
            print(right_jab)
            cv2.putText(frame, "Right Jab!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the video feed
    cv2.imshow("Jab Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
