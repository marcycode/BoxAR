import cv2
import mediapipe as mp
import math

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

def calculate_angle(point1, point2, point3):
    """
    Calculate the angle between three points (shoulder, elbow, wrist).
    """
    # Extract coordinates
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y
    x3, y3 = point3.x, point3.y

    # Calculate vectors
    vector1 = (x1 - x2, y1 - y2)
    vector2 = (x3 - x2, y3 - y2)

    # Calculate the angle using dot product
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

    if magnitude1 == 0 or magnitude2 == 0:  # Avoid division by zero
        return 0

    angle = math.acos(dot_product / (magnitude1 * magnitude2))
    return math.degrees(angle)  # Convert to degrees

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot access the camera.")
        break

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

        # Define points for the left arm
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

        # Calculate angle of the left arm
        left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        # Repeat for the right arm
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

        # Flip the frame for a mirrored effect
        frame = cv2.flip(frame, 1)

        if 160 <= right_arm_angle <= 200:  # Allow some tolerance
            cv2.putText(frame, "Right Arm is Straight", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Check if the arm is straight (angle close to 180 degrees)
        if 160 <= left_arm_angle <= 200:  # Allow some tolerance
            cv2.putText(frame, "Left Arm is Straight", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the video feed
    cv2.imshow("Arm Straightness Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
