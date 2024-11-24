import cv2
import mediapipe as mp
import time
from src.PunchDetector import PunchDetector
from src.Speed import Speed
from cv2constants import CV_VIDEO_CAPTURE_DEVICE

QUEUE_SIZE = 5
# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

pd = PunchDetector()
speed = Speed(QUEUE_SIZE)
# Open webcam
cap = cv2.VideoCapture(CV_VIDEO_CAPTURE_DEVICE)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error accessing the camera.")
        break

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

        # Extract landmarks
        landmarks = results.pose_landmarks.landmark

        # Get the right wrist coordinates
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        right_wrist_position = (
            right_wrist.x * frame.shape[1], right_wrist.y * frame.shape[0])
        left_wrist_position = (
            left_wrist.x * frame.shape[1], left_wrist.y * frame.shape[0])

        right_hand = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX]
        left_hand = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX]
        right_hand_position = (
            right_hand.x * frame.shape[1], right_hand.y * frame.shape[0])
        left_hand_position = (
            left_hand.x * frame.shape[1], left_hand.y * frame.shape[0])

        right_average, right_average_y, left_average, left_average_y = speed.calculate_speeds(
            current_time, right_wrist_position, left_wrist_position, right_hand_position, left_hand_position)

        # Display the speed on the video frame
        # cv2.putText(frame, f"Right Speed: {right_speed:.2f} px/s", (50, 50),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # cv2.putText(frame, f"Left Speed: {speed.left_speed_y:.2f} px/s", (50, 50),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        right_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

        left_jab, right_jab = pd.detect_jab(left_wrist, left_shoulder, left_elbow,
                                            right_wrist, right_shoulder, right_elbow)
        left_cross, right_cross = pd.detect_cross(nose, left_wrist, left_shoulder, left_elbow,
                                                  right_wrist, right_shoulder, right_elbow)
        left_uppercut, right_uppercut = pd.detect_uppercut(nose, left_wrist, left_shoulder, left_elbow,
                                                           right_wrist, right_shoulder, right_elbow)

        if right_wrist.visibility > 0.98 and right_shoulder.visibility > 0.98 and right_elbow.visibility > 0.98:
            if abs(right_average) > 120 and right_average_y < 0 and right_uppercut:
                cv2.putText(frame, "RIGHT UPPERCUT!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            elif right_average > 150 and right_jab:
                cv2.putText(frame, "RIGHT JAB!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            elif right_average < -150 and right_cross:
                cv2.putText(frame, "RIGHT CROSS!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        if left_wrist.visibility > 0.98 and left_shoulder.visibility > 0.98 and left_elbow.visibility > 0.98:
            if abs(left_average_y) > 120 and left_average_y < 0 and left_uppercut:
                cv2.putText(frame, "LEFT UPPERCUT!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            elif left_average < -150 and left_jab:
                cv2.putText(frame, "LEFT JAB!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            elif left_average > 150 and left_cross:
                cv2.putText(frame, "LEFT CROSS!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    # Show the video frame
    cv2.imshow("Wrist Speed Tracking", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
