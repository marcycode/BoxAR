import mediapipe as mp
import cv2

class PunchTracker:
    """Tracks punches based on wrist and shoulder positions."""

    def __init__(self, game_ui):
        self.game_ui = game_ui

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_jab(self, landmarks):
        """
        Detect a jab motion based on wrist and shoulder positions.
        A jab is detected if the wrist moves forward (in the x-axis) relative to the shoulder.
        """
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        # Detect jabs
        left_jab = left_wrist.x > left_shoulder.x + 0.1  # Left jab threshold
        right_jab = right_wrist.x < right_shoulder.x - 0.1  # Right jab threshold

        return right_jab, left_jab

    def process_frame(self, frame):
        """Process the frame, detect punches, and update the score."""
        # Convert the frame to RGB (required by MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        # Draw pose landmarks and detect jabs
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Detect jabs
            right_jab, left_jab = self.detect_jab(results.pose_landmarks.landmark)

            # Check if the detected jab matches the current command
            if self.game_ui.current_command == "Left Jab" and left_jab:
                self.game_ui.increment_score()
                self.game_ui.current_command = None  # Clear command until the next interval
            elif self.game_ui.current_command == "Right Jab" and right_jab:
                self.game_ui.increment_score()
                self.game_ui.current_command = None  # Clear command until the next interval

            # Display jab detection feedback
            if left_jab:
                cv2.putText(frame, "Left Jab!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if right_jab:
                cv2.putText(frame, "Right Jab!", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame
