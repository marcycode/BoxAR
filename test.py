import cv2
import mediapipe as mp

# initialize Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

mp_hands = mp.solutions.hands.Hands()

# create capture object
cap = cv2.VideoCapture(0)
counter = 0
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
    if counter == 10:
        if results.pose_landmarks and results.pose_landmarks.landmark:
            print("Left hand")
            print(results.pose_landmarks.landmark[15])
            print("Right hand")
            print(results.pose_landmarks.landmark[16])

        else:
            print("No hand detected")
        counter = 0
    # print(results.pose_landmarks[15])
    # draw detected skeleton on the frame
    mp_drawing.draw_landmarks(
        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # show the final output
    counter += 1
    cv2.imshow('Output', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()