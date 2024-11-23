import cv2
import mediapipe as mp
from challenge import ChallengeManager
from update_hook import EventManager
import numpy as np

POSE_CONNECTIONS = [
    (11, 12),  # left to right shoulder
    (11, 13),  # left shoulder to left elbow
    (13, 15),  # left elbow to left wrist
    (12, 14),  # right shoulder to right elbow
    (14, 16),  # right elbow to right wrist
    (15, 17),  # left wrist to left pinky
    (16, 18),  # right wrist to right pinky
    (11, 23),  # left shoulder to left hip
    (12, 24),  # right shoulder to right hip
    (23, 24),  # left hip to right hip
    (23, 25),  # left hip to left knee
    (24, 26),  # right hip to right knee
]


def buildLineSet(landmarks):
    lineSet = []
    for connection in POSE_CONNECTIONS:
        startIdx = connection[0]
        endIdx = connection[1]
        startLandmark = landmarks[startIdx]
        endLandmark = landmarks[endIdx]

        lineSet.append((
            (int(startLandmark.x) * 1920, int(startLandmark.y * 1080)
             ), (int(endLandmark.x * 1920), int(endLandmark.y * 1080))
        ))

    return lineSet


def buildPoints(landmarks):
    lineSet = buildLineSet(landmarks)
    points = []
    for line in lineSet:
        points.append(line[0])
        points.append(line[1])
        # append 25 evenly spaced points in between the two points
        for i in range(1, 25):
            x = line[0][0] + (line[1][0] - line[0][0]) * i // 25
            y = line[0][1] + (line[1][1] - line[0][1]) * i // 25
            points.append((x, y))
    return points


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
    return
    x1, y1 = int(lineStart[0]), int(lineStart[1])
    x2, y2 = int(lineEnd[0]), int(lineEnd[1])
    cx, cy = int(circleCoords[0]), int(circleCoords[1])
    r = int(circleRadius)

    lineVector = np.array([x2 - x1, y2 - y1])
    startToCircleVector = np.array([cx - x1, cy - y1])

    cv2.line(frame, [x1, y1], [x2, y2], (0, 255, 0), 2)
    cv2.line(frame, [x1, y1], [cx, cy], (0, 0, 255), 2)

    # calculate the projection of startToCircleVector onto lineVector

    if not np.linalg.norm(lineVector) or not np.linalg.norm(startToCircleVector):
        print("no length of vector")
        return False

    projection = (np.dot(startToCircleVector, lineVector) /
                  np.dot(lineVector, lineVector)) * lineVector
    print(projection)

    cv2.line(frame, [x1, y1], [int(projection[0]), int(
        projection[1])], (255, 0, 0), 2)

    # if the projection is less than or equal to the radius, then the line intersects the circle
    return np.linalg.norm(projection) <= r


def convertLandmarkToPoint(landmark):
    return (int(landmark.x * 1920), int(landmark.y * 1080))


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
    cv2.rectangle(frame, leftShoulder, rightHip, (0, 255, 0), 2)
    # flip because of cv image flip
    torsoBoundingBox = (rightShoulder, leftShoulder, leftHip, rightHip)

    headBoxTopLeft = (rightEyeOuter[0], rightEyeOuter[1] - 50)
    headBoxTopRight = (leftEyeOuter[0], leftEyeOuter[1] - 50)
    headBoxBottomRight = (leftMouth[0], leftMouth[1] + 50)
    headBoxBottomLeft = (rightMouth[0], rightMouth[1] + 50)
    headBoundingBox = (headBoxTopLeft, headBoxTopRight,
                       headBoxBottomRight, headBoxBottomLeft)
    cv2.rectangle(frame, headBoundingBox[1],
                  headBoundingBox[3], (0, 0, 255), 2)
    # if circle is within torso
    if circleIntersectsWithRectangle(circleCoords, circleRadius, torsoBoundingBox):
        return True
    elif circleIntersectsWithRectangle(circleCoords, circleRadius, headBoundingBox):
        return True
    return False


# initialize Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# im_height = 250  # define your top image size here
# im_width = 250
# im = cv2.resize(cv2.imread("glove.png"), (im_width, im_height))
# create capture object
cap = cv2.VideoCapture(0)
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # int `width`
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # int `height`
CHALLENGE_START_SIZE = 50
counter = 0

circle_coords = (FRAME_WIDTH // 2, FRAME_HEIGHT // 2 - FRAME_HEIGHT // 4)
circle_radius = 50


while cap.isOpened():
    # read frame from capture object
    _, frame = cap.read()
    cv2.flip(frame, 1, frame)

    try:
        # convert the frame to RGB format
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        break

    # process the RGB frame to get the result
    results = pose.process(RGB)
    if results.pose_landmarks:
        if hitCriticalMass(results.pose_landmarks.landmark, circle_coords, circle_radius):
            print("Critical Mass Hit")
            cv2.putText(
                frame,
                "Critical Mass Hit",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                5,
            )
        else:
            print("Not Hit")
        # lineSet = buildLineSet(results.pose_landmarks.landmark)
        # for line in lineSet:
        #     if circleIntersectsWithLine(circle_coords, circle_radius, line[0], line[1], frame):
        #         cv2.putText(
        #             frame,
        #             "Collision Detected",
        #             (50, 100),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             1,
        #             (0, 255, 0),
        #             5,
        #         )
        #         cv2.line(frame, line[0], line[1], (0, 0, 255), 5)
        #         break

        # print(results.pose_landmarks[15])
        # draw detected skeleton on the frame
    mp_drawing.draw_landmarks(
        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.circle(frame, circle_coords, circle_radius, (0, 255, 0), 2)

    counter += 1
    cv2.imshow('Output', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
