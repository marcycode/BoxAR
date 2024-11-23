from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import math

class PunchDetector(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PunchDetector, cls).__new__(cls)
        return cls.instance
    
    def calculate_angle(self, point1, point2, point3):
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

    def detect_jab(self, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        """
        Simple logic to detect a jab: 
        Checks if the wrist moves forward (in the x-axis) relative to the shoulder and elbow.
        """
        # leftAngle = self.calculate_angle(leftShoulder, leftElbow, leftWrist)
        # rightAngle = self.calculate_angle(rightShoulder, rightElbow, rightWrist)
        leftJab = leftWrist.x < leftShoulder.x + 0.1 and leftWrist.x < leftElbow.x + 0.1
        rightJab = rightWrist.x > rightShoulder.x - 0.1 and rightWrist.x > rightElbow.x - 0.1
        return (leftJab, rightJab)
    
    def detect_cross(self, nose: NormalizedLandmark, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        """
        Simple logic to detect a cross: 
        Checks if the wrist moves forward (in the x-axis) relative to the elbow, nose and opposing wrist.
        """
        # leftAngle = self.calculate_angle(leftShoulder, leftElbow, leftWrist)
        # rightAngle = self.calculate_angle(rightShoulder, rightElbow, rightWrist)
        leftCross = leftWrist.x > leftElbow.x and leftWrist.x > nose.x - 0.05 and leftElbow.x > leftShoulder.x - 0.05
        rightCross = rightWrist.x < rightElbow.x and rightWrist.x < nose.x + 0.05 and rightElbow.x < rightShoulder.x + 0.05
        return (leftCross, rightCross)
    
    def detect_uppercut(self, nose: NormalizedLandmark, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        """
        Simple logic to detect an uppercut: 
        Checks if the wrist moves forward (in the y-axis) relative to the elbow, and nose.
        """
        # leftAngle = self.calculate_angle(leftShoulder, leftElbow, leftWrist)
        # rightAngle = self.calculate_angle(rightShoulder, rightElbow, rightWrist)
        leftUppercut = leftWrist.y < leftElbow.y and nose.y < leftWrist.y < nose.y + 0.15
        rightUppercut = rightWrist.y < rightElbow.y and nose.y< rightWrist.y < nose.y + 0.15
        return (leftUppercut, rightUppercut)