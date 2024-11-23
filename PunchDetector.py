from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark

class PunchDetector(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PunchDetector, cls).__new__(cls)
        return cls.instance

    def detect_jab(self, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        """
        Simple logic to detect a jab: 
        Checks if the wrist moves forward (in the x-axis) relative to the shoulder and elbow.
        """
        leftJab = leftWrist.x < leftShoulder.x + 0.1 and leftWrist.x < leftElbow.x + 0.05
        rightJab = rightWrist.x > rightShoulder.x - 0.1 and rightWrist.x > rightElbow.x - 0.05
        return (leftJab, rightJab)
    
    def detect_cross(self, nose: NormalizedLandmark, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        """
        Simple logic to detect a cross: 
        Checks if the wrist moves forward (in the x-axis) relative to the elbow, nose and opposing wrist.
        """
        leftCross = leftWrist.x > leftElbow.x and leftWrist.x > nose.x - 0.1 and leftElbow.x > leftShoulder.x - 0.05
        rightCross = rightWrist.x < rightElbow.x and rightWrist.x < nose.x + 0.1 and rightElbow.x < rightShoulder.x + 0.05
        return (leftCross, rightCross)
    
    def detect_uppercut(self, nose: NormalizedLandmark, leftWrist: NormalizedLandmark, leftShoulder: NormalizedLandmark,
                        leftElbow: NormalizedLandmark, rightWrist: NormalizedLandmark,
                        rightShoulder: NormalizedLandmark, rightElbow: NormalizedLandmark) -> tuple[bool]: # (bool, bool)
        return