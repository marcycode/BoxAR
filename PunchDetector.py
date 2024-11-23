class PunchDetector(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PunchDetector, cls).__new__(cls)
        return cls.instance

    def detect_jab(self, leftWrist: float, leftShoulder: float, leftElbow: float,
                    rightWrist: float, rightShoulder: float, rightElbow: float) -> (bool, bool): # type: ignore
        """
        Simple logic to detect a jab: 
        Checks if the wrist moves forward (in the x-axis) relative to the shoulder and elbow.
        """
        leftJab = leftWrist < leftShoulder + 0.1 and leftWrist < leftElbow + 0.05
        rightJab = rightWrist > rightShoulder - 0.1 and rightWrist > rightElbow - 0.1
        return (leftJab, rightJab)
    
    def detect_cross(self, nose: float, leftWrist: float, leftShoulder: float, 
                        leftElbow: float, rightWrist: float, 
                        rightShoulder: float, rightElbow: float) -> (bool, bool): # type: ignore
        """
        Simple logic to detect a cross: 
        Checks if the wrist moves forward (in the x-axis) relative to the elbow, nose and opposing wrist.
        """
        leftCross = leftWrist > leftElbow and leftWrist > nose - 0.1 and leftElbow > leftShoulder -0.05
        rightCross = rightWrist < rightElbow and rightWrist < nose + 0.1 and rightElbow < rightShoulder
        return (leftCross, rightCross)
    
    def detect_uppercut(self):
        return