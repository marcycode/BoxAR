import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils


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
        self.video.set(3, page_width / 2)  # 3 -> WIDTH
        self.video.set(4, page_height / 2)  # 4 -> HEIGHT

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
