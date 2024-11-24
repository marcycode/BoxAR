import numpy as np
import os
from pygame import mixer

mixer.init()


collision_sound = mixer.Sound("assets/collisionsound.mp3")
def pointIntersectsWithCircle(point, circleCoords, circleRadius):
    return np.linalg.norm(np.array(point) - np.array(circleCoords)) <= circleRadius


def circleIntersectsWithLine(circleCoords, circleRadius, lineStart, lineEnd, frame):
    a, b, c = lineStart[1] - lineEnd[1], lineEnd[0] - \
        lineStart[0], lineStart[0] * lineEnd[1] - lineEnd[0] * lineStart[1]
    x0, y0, r = circleCoords[0], circleCoords[1], circleRadius
    distance = abs(a * x0 + b * y0 + c) / np.sqrt(a ** 2 + b ** 2)
    if distance > r:
        return False

    if np.linalg.norm(np.array(lineStart) - np.array(circleCoords)) <= r or np.linalg.norm(np.array(lineEnd) - np.array(circleCoords)) <= r:
        return True
    else:
        return False


def convertLandmarkToPoint(landmark):
    return (int(landmark.x * int(os.getenv("FRAME_WIDTH"))), int(landmark.y * int(os.getenv("FRAME_WIDTH"))))


def circleIntersectsWithRectangle(circleCoords, circleRadius, rectangleCoords):
    topLeftCorner, topRightCorner, bottomRightCorner, bottomLeftCorner = rectangleCoords
    cx, cy = circleCoords
    circleDistanceX = abs(cx - (topLeftCorner[0] + topRightCorner[0]) / 2)
    circleDistanceY = abs(cy - (topLeftCorner[1] + bottomLeftCorner[1]) / 2)

    if circleDistanceX > (topRightCorner[0] - topLeftCorner[0]) / 2 + circleRadius:
        return False
    if circleDistanceY > (bottomLeftCorner[1] - topLeftCorner[1]) / 2 + circleRadius:
        return False

    if circleDistanceX <= (topRightCorner[0] - topLeftCorner[0]) / 2:
        return True
    if circleDistanceY <= (bottomLeftCorner[1] - topLeftCorner[1]) / 2:
        return True

    cornerDistanceSquared = (circleDistanceX - (topRightCorner[0] - topLeftCorner[0]) / 2) ** 2 + (
        circleDistanceY - (bottomLeftCorner[1] - topLeftCorner[1]) / 2) ** 2
    return cornerDistanceSquared <= circleRadius ** 2


def hitCriticalMass(landmarks, circleCoords, circleRadius):
    leftShoulder = convertLandmarkToPoint(landmarks[11])
    rightShoulder = convertLandmarkToPoint(landmarks[12])
    leftHip = convertLandmarkToPoint(landmarks[23])
    rightHip = convertLandmarkToPoint(landmarks[24])
    leftEyeOuter = convertLandmarkToPoint(landmarks[3])
    rightEyeOuter = convertLandmarkToPoint(landmarks[6])
    leftMouth = convertLandmarkToPoint(landmarks[9])
    rightMouth = convertLandmarkToPoint(landmarks[10])

    cx, cy = circleCoords
    # draw bounding box
    # flip because of cv image flip
    torsoBoundingBox = (rightShoulder, leftShoulder, leftHip, rightHip)

    headBoxTopLeft = (rightEyeOuter[0], rightEyeOuter[1] - 50)
    headBoxTopRight = (leftEyeOuter[0], leftEyeOuter[1] - 50)
    headBoxBottomRight = (leftMouth[0], leftMouth[1] + 50)
    headBoxBottomLeft = (rightMouth[0], rightMouth[1] + 50)
    headBoundingBox = (headBoxTopLeft, headBoxTopRight,
                       headBoxBottomRight, headBoxBottomLeft)
    # if circle is within torso
    if circleIntersectsWithRectangle(circleCoords, circleRadius, torsoBoundingBox):
        collision_sound.play()
        return True
    elif circleIntersectsWithRectangle(circleCoords, circleRadius, headBoundingBox):
        collision_sound.play()
        return True
    return False
