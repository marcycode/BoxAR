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
                [left_elbow.x, left_elbow.y], [left_shoulder.x, left_shoulder.y]
            )
            < 0.15
        )
        right_tuck = (
            self.calculate_distance(
                [right_elbow.x, right_elbow.y], [right_shoulder.x, right_shoulder.y]
            )
            < 0.15
        )

        left_wrist_face = (
            self.calculate_distance([left_wrist.x, left_wrist.y], [nose.x, nose.y]) < 0.15
        )
        right_wrist_face = (
            self.calculate_distance([right_wrist.x, right_wrist.y], [nose.x, nose.y]) < 0.15
        )

        return left_tuck and right_tuck and left_wrist_face and right_wrist_face