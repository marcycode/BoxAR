from math import sqrt
from collision_detection import convertLandmarkToPoint

class Block:
    def __init__(self):
        return

    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


    def detectBlock(self, landmarks):
        """
        Simple logic to detect a block:
        Checks if elbows are tucked into shoulders and wrists are covering face
        """
        # Detect a "block" motion
        left_wrist = convertLandmarkToPoint(landmarks[15])
        left_elbow = convertLandmarkToPoint(landmarks[13])
        left_shoulder = convertLandmarkToPoint(landmarks[11])
        right_wrist = convertLandmarkToPoint(landmarks[16])
        right_elbow = convertLandmarkToPoint(landmarks[14])
        right_shoulder = convertLandmarkToPoint(landmarks[12])
        nose = convertLandmarkToPoint(landmarks[0])
        left_tuck = (
            self.calculate_distance(
                [left_elbow[0], left_elbow[1]], [left_shoulder[0], left_shoulder[1]]
            )
            < 0.15
        )
        right_tuck = (
            self.calculate_distance(
                [right_elbow[0], right_elbow[0]], [right_shoulder[0], right_shoulder[1]]
            )
            < 0.15
        )

        left_wrist_face = (
            self.calculate_distance([left_wrist[0], left_wrist[1]], [nose[0], nose[1]]) < 0.15
        )
        right_wrist_face = (
            self.calculate_distance([right_wrist[0], right_wrist[1]], [nose[0], nose[1]]) < 0.15
        )

        return left_tuck and right_tuck and left_wrist_face and right_wrist_face