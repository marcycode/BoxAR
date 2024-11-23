import cv2
import mediapipe as mp
from challenge import ChallengeManager
from update_hook import EventManager
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

challengeManager = ChallengeManager()
eventManager = EventManager()
eventManager.addEvent("generatePunchChallenge", 50,
                      challengeManager.generatePunchChallenge,
                      ["frameWidth", "frameHeight", "startSize"])
eventManager.addEvent("update_challenges", 1,
                      challengeManager.update_challenges)

drawManager = EventManager()
drawManager.addEvent("draw_challenges", 1,
                     challengeManager.draw_challenges, ["frame"])

context = {
    "frameWidth": FRAME_WIDTH,
    "frameHeight": FRAME_HEIGHT,
    "startSize": CHALLENGE_START_SIZE
}

while cap.isOpened():
    # read frame from capture object
    _, frame = cap.read()

    try:
        # convert the frame to RGB format
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        break

    # process the RGB frame to get the result
    results = pose.process(RGB)
    context["frame"] = frame
    context["landmarks"] = results.pose_landmarks

    # print(results.pose_landmarks[15])
    # draw detected skeleton on the frame
    mp_drawing.draw_landmarks(
        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # show the final output
    # over lay image

    eventManager.update(context)
    drawManager.update(context)

    counter += 1
    cv2.imshow('Output', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
